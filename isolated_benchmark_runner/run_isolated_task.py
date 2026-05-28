"""Run dataset tasks in fresh, skill-controlled nanobot workspaces.

This runner prepares isolated workspaces for tasks declared in datasets/task.json
and can optionally execute each turn. It writes unified benchmark outputs in
addition to logs so downstream evaluators do not need to parse terminal text.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_TASK_JSON = REPO_ROOT / "datasets" / "task.json"
RUNS_ROOT = REPO_ROOT / "runs"

AGENT_DEFAULT_KEYS_TO_COPY = {
    "model",
    "provider",
    "maxTokens",
    "contextWindowTokens",
    "contextBlockLimit",
    "temperature",
    "maxToolIterations",
    "maxConcurrentSubagents",
    "maxToolResultChars",
    "providerRetryMode",
    "toolHintMaxLength",
    "reasoningEffort",
    "botName",
    "botIcon",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_system_prompt_snapshot(
    *,
    run_root: Path,
    idx: int,
    system_prompt: str,
) -> Path:
    """Persist the system prompt sent context for audit/debugging."""
    path = run_root / "system_prompts" / f"turn_{idx:02d}.system.md"
    write_text(path, system_prompt)
    return path


def timestamp_run_id() -> str:
    return datetime.now().strftime("run_%Y%m%d_%H%M%S")


def safe_name(value: str) -> str:
    bad = '<>:"/\\|?*'
    return "".join("_" if ch in bad else ch for ch in value).strip() or "task"


def discover_builtin_skills() -> list[str]:
    skills_dir = REPO_ROOT / "nanobot" / "skills"
    if not skills_dir.is_dir():
        return []
    return sorted(
        child.name
        for child in skills_dir.iterdir()
        if child.is_dir() and (child / "SKILL.md").is_file()
    )


def discover_dataset_skills() -> list[str]:
    skills_dir = REPO_ROOT / "datasets" / "skills"
    if not skills_dir.is_dir():
        return []
    return sorted(
        child.name
        for child in skills_dir.iterdir()
        if child.is_dir() and (child / "SKILL.md").is_file()
    )


def load_tasks(task_json: Path) -> list[dict[str, Any]]:
    tasks = load_json(task_json)
    if not isinstance(tasks, list) or not tasks:
        raise ValueError(f"No tasks found in {task_json}")
    valid_tasks = [task for task in tasks if isinstance(task, dict)]
    if not valid_tasks:
        raise ValueError(f"No object tasks found in {task_json}")
    return valid_tasks


def split_task_ids(values: list[str] | None) -> list[str]:
    if not values:
        return []
    task_ids: list[str] = []
    for value in values:
        for item in value.split(","):
            item = item.strip()
            if item:
                task_ids.append(item)
    return list(dict.fromkeys(task_ids))


def select_tasks(
    *,
    task_json: Path,
    task_ids: list[str],
    all_tasks: bool,
) -> list[dict[str, Any]]:
    tasks = load_tasks(task_json)
    by_id = {str(task.get("task_id")): task for task in tasks if task.get("task_id")}
    if all_tasks and task_ids:
        raise ValueError("Use either --all-tasks or --task-id, not both.")
    if all_tasks:
        return tasks
    if task_ids:
        selected: list[dict[str, Any]] = []
        missing: list[str] = []
        for task_id in task_ids:
            task = by_id.get(task_id)
            if task is None:
                missing.append(task_id)
            else:
                selected.append(task)
        if missing:
            raise ValueError(f"Task id not found: {', '.join(missing)}")
        return selected
    task = tasks[0]
    if not isinstance(task, dict):
        raise ValueError("First task entry is not an object")
    return [task]


def default_base_config_path() -> Path | None:
    candidate = Path.home() / ".nanobot" / "config.json"
    return candidate if candidate.is_file() else None


def load_base_config(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    if not path.is_file():
        raise FileNotFoundError(f"Base config not found: {path}")
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError(f"Base config must be a JSON object: {path}")
    return data


def build_config(
    *,
    base_config: dict[str, Any],
    workspace: Path,
    allowed_skills: list[str],
    skill_mode: str,
    timezone: str,
    max_tool_iterations: int | None,
) -> dict[str, Any]:
    base_defaults = (
        base_config.get("agents", {}).get("defaults", {})
        if isinstance(base_config.get("agents"), dict)
        else {}
    )
    copied_defaults = {
        key: value
        for key, value in base_defaults.items()
        if key in AGENT_DEFAULT_KEYS_TO_COPY
    }

    disabled = set(discover_builtin_skills())
    disabled.update(skill for skill in discover_dataset_skills() if skill not in allowed_skills)
    if skill_mode == "off":
        disabled.update(allowed_skills)

    defaults: dict[str, Any] = {
        **copied_defaults,
        "workspace": str(workspace),
        "timezone": timezone,
        "unifiedSession": False,
        "idleCompactAfterMinutes": 0,
        "maxMessages": 200,
        "disabledSkills": sorted(disabled),
        "dream": {
            "intervalH": 999999,
            "maxBatchSize": 1,
            "maxIterations": 1,
            "annotateLineAges": False,
        },
    }
    if max_tool_iterations is not None:
        defaults["maxToolIterations"] = max_tool_iterations

    return {
        "providers": base_config.get("providers", {}),
        "agents": {"defaults": defaults},
        "channels": {
            "sendProgress": False,
            "sendToolHints": False,
            "sendMaxRetries": 1,
        },
        "tools": {
            "restrictToWorkspace": True,
            "web": {"enable": False},
            "my": {"enable": False, "allowSet": False},
            "imageGeneration": {"enabled": False},
            "mcpServers": {},
        },
    }


def copy_task_assets(task: dict[str, Any], workspace: Path) -> list[dict[str, str]]:
    copied: list[dict[str, str]] = []
    datasets_root = REPO_ROOT / "datasets"
    for asset in task.get("data_assets", []):
        if not isinstance(asset, dict):
            continue
        src_rel = asset.get("path")
        env_rel = asset.get("env_path")
        if not isinstance(src_rel, str) or not isinstance(env_rel, str):
            raise ValueError(f"Invalid data asset entry: {asset}")
        src = datasets_root / src_rel
        dst = workspace / env_rel
        if not src.is_file():
            raise FileNotFoundError(f"Task asset not found: {src}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append({"source": str(src), "destination": str(dst)})
    return copied


def copy_allowed_skills(
    *,
    allowed_skills: list[str],
    workspace: Path,
    skill_mode: str,
    skill_policy: str,
) -> list[dict[str, str]]:
    if skill_mode == "off":
        (workspace / "skills").mkdir(parents=True, exist_ok=True)
        return []

    copied: list[dict[str, str]] = []
    source_root = REPO_ROOT / "datasets" / "skills"
    target_root = workspace / "skills"
    target_root.mkdir(parents=True, exist_ok=True)
    for skill in allowed_skills:
        src = source_root / skill
        dst = target_root / skill
        src_skill = src / "SKILL.md"
        if not src_skill.is_file():
            raise FileNotFoundError(f"Allowed skill not found: {src}")
        if dst.exists():
            shutil.rmtree(dst)
        if skill_policy == "force-use":
            shutil.copytree(src, dst)
            force_skill_into_system_prompt(dst / "SKILL.md")
            copied.append(
                {
                    "source": str(src),
                    "destination": str(dst),
                    "description_only": "false",
                    "system_prompt_loaded": "true",
                }
            )
        else:
            dst.mkdir(parents=True, exist_ok=True)
            description = extract_skill_description(src_skill, fallback=skill)
            write_description_only_skill(dst / "SKILL.md", skill, description)
            copied.append(
                {
                    "source": str(src),
                    "destination": str(dst),
                    "description_only": "true",
                }
            )
    return copied


def force_skill_into_system_prompt(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n?", content, re.DOTALL)
    force_lines = ["always: true", "benchmark_force_use: true"]
    if match:
        frontmatter = match.group(1)
        body = content[match.end():]
        kept = [
            line
            for line in frontmatter.splitlines()
            if not re.match(r"^\s*(always|benchmark_force_use)\s*:", line)
        ]
        new_frontmatter = "\n".join([*kept, *force_lines]).strip()
        write_text(path, f"---\n{new_frontmatter}\n---\n\n{body.lstrip()}")
        return
    write_text(path, f"---\n{chr(10).join(force_lines)}\n---\n\n{content}")


def extract_skill_description(path: Path, fallback: str = "") -> str:
    if not path.is_file():
        return fallback
    content = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\r?\n(.*?)\r?\n---", content, re.DOTALL)
    if match:
        frontmatter = match.group(1)
        desc_match = re.search(
            r"^description\s*:\s*(.+?)\s*$",
            frontmatter,
            re.MULTILINE,
        )
        if desc_match:
            return desc_match.group(1).strip().strip("\"'")
    return fallback


def write_description_only_skill(path: Path, skill: str, description: str) -> None:
    safe_description = description.replace("\\", "\\\\").replace('"', '\\"')
    write_text(
        path,
        f"""---
name: "{skill}"
description: "{safe_description}"
benchmark_description_only: true
---

# {skill}

Description-only benchmark skill stub.

This isolated benchmark exposes only this skill description:

{description}
""",
    )


def skill_description(workspace: Path, skill: str) -> str:
    path = workspace / "skills" / skill / "SKILL.md"
    return extract_skill_description(path, fallback=skill)


def build_skill_description_text(workspace: Path, allowed_skills: list[str]) -> str:
    lines = []
    for skill in allowed_skills:
        description = skill_description(workspace, skill)
        if description:
            lines.append(f"- {skill}: {description}")
        else:
            lines.append(f"- {skill}")
    return "\n".join(lines)


def build_turn_prompt(
    *,
    task: dict[str, Any],
    turn: dict[str, Any],
    skill_mode: str,
    allowed_skills: list[str],
    skill_policy: str,
    skill_description_text: str = "",
    preloaded_skill_context: str = "",
) -> str:
    if skill_mode == "on" and allowed_skills:
        skill_list = "、".join(allowed_skills)
        skill_paths = "、".join(f"skills/{name}/SKILL.md" for name in allowed_skills)
        if skill_policy == "force-use":
            turn_idx = int(turn.get("idx", 0))
            if turn_idx == 0:
                skill_text = (
                    f"本次任务必须使用以下 workspace skill：{skill_list}。"
                    "这些 skill 的完整 SKILL.md 已作为 Active Skills 加载到系统提示词中，后续每一轮都可见。"
                    "你需要遵循这些 skill 的适用方法完成任务；"
                    "如果 skill 内容和本任务说明、本轮问题或本地数据冲突，以本任务说明、本轮问题和本地数据为准。"
                )
            else:
                skill_text = (
                    f"本次任务必须继续使用前序已确认的 workspace skill：{skill_list}。"
                    "这些 skill 的完整 SKILL.md 已作为 Active Skills 加载到系统提示词中，本轮仍然可见。"
                    "如果 skill 内容和本任务说明、本轮问题或本地数据冲突，以本任务说明、本轮问题和本地数据为准。"
                )
        elif skill_policy == "required-read":
            skill_text = (
                f"本次 run 必须先读取以下 workspace skill 的 description-only 文件：{skill_list}。"
                f"回答前请先用 read_file 读取：{skill_paths}。"
                "这些 SKILL.md 只包含 description；读取后是否采纳 skill，由你根据本任务说明和本轮问题自行判断。"
            )
        elif skill_policy == "preload":
            skill_text = (
                f"本次 run 已预加载以下 workspace skill description：{skill_list}。"
                "请只基于预加载的 description 判断 skill 适用性；不要读取或使用其他 skill。"
            )
        else:
            skill_text = (
                f"本次 run 允许使用以下 workspace skill description：{skill_list}。"
                f"\n{skill_description_text}"
                "\n如果你决定使用 skill，只能基于这些 description-only 信息判断。"
            )
    else:
        skill_text = "本次 run 禁止使用任何 skill；请不要读取 workspace/skills 下的内容。"

    related = turn.get("related_tables") or []
    related_text = "\n".join(f"- {item}" for item in related if isinstance(item, str))
    if not related_text:
        related_text = "- 无"

    return f"""你正在执行一个隔离的 nanobot benchmark 任务。请严格遵守任务说明，直接回答当前轮问题。

全局任务说明：
{task.get("instruction", "")}

隔离与工具约束：
- 只能使用当前 workspace 内的本地文件。
- 数据文件路径以 workspace 为根目录，例如 datasets/2025年分段表.xls。
- 禁止联网；不要调用 web_search 或 web_fetch。
- 禁止安装、创建、修改或保存新的 skill。
- {skill_text}
- 如果 skill 内容和本任务说明冲突，以本任务说明、本轮问题和本地数据为准。

当前轮次：{turn.get("idx")}
当前相关数据表：
{related_text}

当前问题：
{turn.get("question", "")}
{preloaded_skill_context}
""".strip()


def build_preloaded_skill_context(
    *,
    workspace: Path,
    allowed_skills: list[str],
    skill_mode: str,
    skill_policy: str,
) -> str:
    if skill_mode != "on" or skill_policy != "preload" or not allowed_skills:
        return ""

    parts: list[str] = []
    for skill in allowed_skills:
        path = workspace / "skills" / skill / "SKILL.md"
        if not path.is_file():
            raise FileNotFoundError(f"Allowed skill not found for preload: {path}")
        description = skill_description(workspace, skill)
        parts.append(f"## Skill Description: {skill}\n\n{description}")
    return "\n\n预加载 skill description：\n" + "\n\n---\n\n".join(parts)


def assert_allowed_skills(workspace: Path, allowed_skills: list[str], skill_mode: str) -> None:
    skills_dir = workspace / "skills"
    if not skills_dir.exists():
        return
    expected = set(allowed_skills if skill_mode == "on" else [])
    actual = {child.name for child in skills_dir.iterdir() if child.is_dir()}
    extra = sorted(actual - expected)
    if extra:
        raise RuntimeError(
            "Unexpected skill directory created or copied: "
            + ", ".join(extra)
            + f" under {skills_dir}"
        )


def _normalize_tool_path(value: str) -> str:
    return value.replace("\\", "/").strip().lower()


def detect_skill_usage(manifest: dict[str, Any]) -> dict[str, Any]:
    run_root = Path(manifest["run_root"])
    workspace = Path(manifest["workspace"])
    allowed_skills = list(manifest.get("allowed_skills", []))
    usage = {
        "skill_mode": manifest.get("skill_mode"),
        "skill_policy": manifest.get("skill_policy", "available"),
        "allowed_skills": allowed_skills,
        "description_only_skills": bool(allowed_skills) and manifest.get("skill_policy") != "force-use",
        "system_prompt_loaded": bool(allowed_skills) and manifest.get("skill_policy") == "force-use",
        "description_preloaded": manifest.get("skill_policy") == "preload" and bool(allowed_skills),
        "description_presented": manifest.get("skill_policy") == "available" and bool(allowed_skills),
        "skills": {
            skill: {
                "read_file_called": False,
                "read_file_lines": [],
                "read_file_paths": [],
            }
            for skill in allowed_skills
        },
        "session_files": [],
    }
    sessions_dir = workspace / "sessions"
    if not sessions_dir.is_dir():
        return usage

    expected_paths = {
        skill: f"skills/{skill}/skill.md".lower()
        for skill in allowed_skills
    }
    for session_path in sorted(sessions_dir.glob("*.jsonl")):
        usage["session_files"].append(str(session_path))
        with session_path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                for tool_call in event.get("tool_calls") or []:
                    function = tool_call.get("function") or {}
                    if function.get("name") != "read_file":
                        continue
                    raw_args = function.get("arguments") or "{}"
                    try:
                        args = json.loads(raw_args)
                    except json.JSONDecodeError:
                        args = {}
                    path_value = args.get("path", "")
                    if not isinstance(path_value, str):
                        continue
                    normalized = _normalize_tool_path(path_value)
                    for skill, expected in expected_paths.items():
                        if normalized.endswith(expected):
                            usage["skills"][skill]["read_file_called"] = True
                            usage["skills"][skill]["read_file_lines"].append(line_no)
                            usage["skills"][skill]["read_file_paths"].append(path_value)
    return usage


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def detect_agent_error(content: str) -> str | None:
    stripped = content.strip()
    lowered = stripped.lower()
    if stripped.startswith("Error:") or lowered.startswith("error:"):
        return stripped.splitlines()[0][:1000]
    for token in (
        "invalidsubscription",
        "does not have a valid codingplan subscription",
        "llm returned error",
        "maximum number of tool call iterations",
        "max tool iterations",
        "without completing the task",
    ):
        if token in lowered:
            return stripped.splitlines()[0][:1000] if stripped else token
    return None


def extract_json_payload(text: str) -> Any | None:
    """Best-effort extraction of a JSON object/array from a model response."""
    stripped = text.strip()
    if not stripped:
        return None

    fence_markers = ("```json", "```JSON", "```")
    for marker in fence_markers:
        start = stripped.find(marker)
        if start < 0:
            continue
        body_start = start + len(marker)
        end = stripped.find("```", body_start)
        if end < 0:
            continue
        candidate = stripped[body_start:end].strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    for pos, ch in enumerate(stripped):
        if ch not in "{[":
            continue
        try:
            value, _ = decoder.raw_decode(stripped[pos:])
            return value
        except json.JSONDecodeError:
            continue
    return None


def write_unified_outputs(
    *,
    manifest: dict[str, Any],
    task: dict[str, Any],
    records: list[dict[str, Any]],
) -> None:
    """Write evaluator-friendly outputs for the run."""
    run_root = Path(manifest["run_root"])
    skill_usage = detect_skill_usage(manifest)
    skill_usage_path = run_root / "skill_usage.json"
    write_json(skill_usage_path, skill_usage)
    successful = [
        record
        for record in records
        if record.get("returncode") == 0 and isinstance(record.get("content"), str)
    ]
    final_content = successful[-1]["content"] if successful else ""
    final_md_path = run_root / "final_output.md"
    write_text(final_md_path, final_content)

    parsed = extract_json_payload(final_content)
    final_json_path: str | None = None
    if parsed is not None:
        path = run_root / "final_output.json"
        write_json(path, parsed)
        final_json_path = str(path)

    task_result = {
        "task_id": task.get("task_id"),
        "skill_mode": manifest.get("skill_mode"),
        "run_id": manifest.get("run_id"),
        "status": "completed" if records and all(r.get("returncode") == 0 for r in records) else "failed",
        "final_output_md": str(final_md_path),
        "final_output_json": final_json_path,
        "final_output_parseable_json": parsed is not None,
        "final_output": parsed if parsed is not None else final_content,
        "skill_policy": manifest.get("skill_policy", "available"),
        "skill_usage_json": str(skill_usage_path),
        "skill_usage": skill_usage,
        "turns": records,
    }
    write_json(run_root / "task_result.json", task_result)


def prepare_run(
    *,
    task: dict[str, Any],
    skill_mode: str,
    skill_policy: str,
    run_id: str,
    base_config: dict[str, Any],
    timezone: str,
    max_tool_iterations: int | None,
    overwrite: bool,
) -> dict[str, Any]:
    task_id = str(task["task_id"])
    run_root = RUNS_ROOT / safe_name(task_id) / f"skill_{skill_mode}" / safe_name(run_id)
    workspace = run_root / "workspace"
    config_path = run_root / "config.json"

    if run_root.exists():
        if not overwrite:
            raise FileExistsError(f"Run directory already exists: {run_root}")
        shutil.rmtree(run_root)

    workspace.mkdir(parents=True, exist_ok=True)
    allowed_skills = [str(skill) for skill in task.get("skills", [])]
    assets = copy_task_assets(task, workspace)
    skills = copy_allowed_skills(
        allowed_skills=allowed_skills,
        workspace=workspace,
        skill_mode=skill_mode,
        skill_policy=skill_policy,
    )
    config = build_config(
        base_config=base_config,
        workspace=workspace,
        allowed_skills=allowed_skills,
        skill_mode=skill_mode,
        timezone=timezone,
        max_tool_iterations=max_tool_iterations,
    )
    write_json(config_path, config)

    prompts_dir = run_root / "prompts"
    preloaded_skill_context = build_preloaded_skill_context(
        workspace=workspace,
        allowed_skills=allowed_skills,
        skill_mode=skill_mode,
        skill_policy=skill_policy,
    )
    skill_description_text = build_skill_description_text(workspace, allowed_skills)
    for turn in task.get("turns", []):
        if isinstance(turn, dict):
            prompt = build_turn_prompt(
                task=task,
                turn=turn,
                skill_mode=skill_mode,
                allowed_skills=allowed_skills,
                skill_policy=skill_policy,
                skill_description_text=skill_description_text,
                preloaded_skill_context=preloaded_skill_context,
            )
            write_text(prompts_dir / f"turn_{int(turn.get('idx', 0)):02d}.txt", prompt)

    manifest = {
        "task_id": task_id,
        "skill_mode": skill_mode,
        "skill_policy": skill_policy if skill_mode == "on" else "off",
        "run_id": run_id,
        "created_at": datetime.now().isoformat(),
        "repo_root": str(REPO_ROOT),
        "run_root": str(run_root),
        "workspace": str(workspace),
        "config": str(config_path),
        "allowed_skills": allowed_skills if skill_mode == "on" else [],
        "task_declared_skills": allowed_skills,
        "copied_assets": assets,
        "copied_skills": skills,
    }
    write_json(run_root / "manifest.json", manifest)
    assert_allowed_skills(workspace, allowed_skills, skill_mode)
    return manifest


async def run_turns_direct_async(
    *,
    manifest: dict[str, Any],
    task: dict[str, Any],
    keep_going: bool,
    continue_turns_on_error: bool,
    turn_timeout_seconds: int,
) -> int:
    """Execute turns in-process and capture clean assistant content."""
    from nanobot.agent.loop import AgentLoop
    from nanobot.bus.queue import MessageBus
    from nanobot.config.loader import load_config, resolve_config_env_vars, set_config_path
    from nanobot.cron.service import CronService
    from nanobot.utils.helpers import sync_workspace_templates

    run_root = Path(manifest["run_root"])
    config_path = Path(manifest["config"])
    workspace = Path(manifest["workspace"])
    task_id = str(task["task_id"])
    session_id = f"bench:{task_id}:{manifest.get('skill_mode')}:{manifest.get('run_id')}"
    responses_path = run_root / "responses.jsonl"
    records: list[dict[str, Any]] = []
    exit_code = 0

    if responses_path.exists():
        responses_path.unlink()

    set_config_path(config_path)
    config = resolve_config_env_vars(load_config(config_path))
    sync_workspace_templates(config.workspace_path, silent=True)
    bus = MessageBus()
    cron = CronService(config.workspace_path / "cron" / "jobs.json")
    agent_loop = AgentLoop.from_config(config, bus, cron_service=cron)
    pending_system_prompt_path: Path | None = None
    original_build_messages = agent_loop.context.build_messages

    def capture_build_messages(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        messages = original_build_messages(*args, **kwargs)
        if pending_system_prompt_path and messages:
            first = messages[0]
            if first.get("role") == "system":
                write_text(pending_system_prompt_path, str(first.get("content", "")))
        return messages

    agent_loop.context.build_messages = capture_build_messages  # type: ignore[method-assign]

    try:
        for turn in task.get("turns", []):
            if not isinstance(turn, dict):
                continue
            idx = int(turn.get("idx", 0))
            prompt_path = run_root / "prompts" / f"turn_{idx:02d}.txt"
            prompt = prompt_path.read_text(encoding="utf-8")
            response_path = run_root / "outputs" / f"turn_{idx:02d}.response.md"
            error_path = run_root / "outputs" / f"turn_{idx:02d}.error.txt"

            record: dict[str, Any] = {
                "idx": idx,
                "prompt_path": str(prompt_path),
                "response_path": str(response_path),
                "returncode": 0,
                "content": "",
            }
            system_prompt_path = write_system_prompt_snapshot(
                run_root=run_root,
                idx=idx,
                system_prompt=agent_loop.context.build_system_prompt(channel="bench"),
            )
            record["system_prompt_path"] = str(system_prompt_path)
            try:
                pending_system_prompt_path = system_prompt_path
                response = await asyncio.wait_for(
                    agent_loop.process_direct(
                        content=prompt,
                        session_key=session_id,
                        channel="bench",
                        chat_id=task_id,
                    ),
                    timeout=turn_timeout_seconds,
                )
                pending_system_prompt_path = None
                content = response.content if response else ""
                record["content"] = content
                write_text(response_path, content)
                agent_error = detect_agent_error(content)
                if agent_error:
                    exit_code = 1
                    record["returncode"] = 1
                    record["error"] = agent_error
                    write_text(error_path, agent_error)
                    record["error_path"] = str(error_path)
                assert_allowed_skills(
                    workspace,
                    list(manifest.get("task_declared_skills", [])),
                    str(manifest["skill_mode"]),
                )
                if agent_error and not continue_turns_on_error:
                    records.append(record)
                    append_jsonl(responses_path, record)
                    break
            except Exception as exc:
                exit_code = 1
                record["returncode"] = 1
                record["error"] = f"{type(exc).__name__}: {exc}"
                write_text(error_path, record["error"])
                record["error_path"] = str(error_path)
                pending_system_prompt_path = None
                if not continue_turns_on_error:
                    records.append(record)
                    append_jsonl(responses_path, record)
                    break

            records.append(record)
            append_jsonl(responses_path, record)
    finally:
        await agent_loop.close_mcp()

    write_unified_outputs(manifest=manifest, task=task, records=records)
    return exit_code


def run_turns_direct(
    *,
    manifest: dict[str, Any],
    task: dict[str, Any],
    keep_going: bool,
    continue_turns_on_error: bool,
    turn_timeout_seconds: int,
) -> int:
    return asyncio.run(
        run_turns_direct_async(
            manifest=manifest,
            task=task,
            keep_going=keep_going,
            continue_turns_on_error=continue_turns_on_error,
            turn_timeout_seconds=turn_timeout_seconds,
        )
    )


def extract_cli_response(stdout: str) -> str:
    """Extract response text from nanobot CLI output when using --backend cli."""
    marker = "nanobot"
    pos = stdout.rfind(marker)
    if pos < 0:
        return stdout.strip()
    return stdout[pos + len(marker):].strip()


def run_turns_cli(
    *,
    manifest: dict[str, Any],
    task: dict[str, Any],
    python_exe: str,
    keep_going: bool,
    continue_turns_on_error: bool,
    turn_timeout_seconds: int,
) -> int:
    run_root = Path(manifest["run_root"])
    config_path = Path(manifest["config"])
    workspace = Path(manifest["workspace"])
    task_id = str(task["task_id"])
    session_id = f"bench:{task_id}:{manifest.get('skill_mode')}:{manifest.get('run_id')}"
    responses_path = run_root / "responses.jsonl"
    records: list[dict[str, Any]] = []
    exit_code = 0

    if responses_path.exists():
        responses_path.unlink()

    for turn in task.get("turns", []):
        if not isinstance(turn, dict):
            continue
        idx = int(turn.get("idx", 0))
        prompt_path = run_root / "prompts" / f"turn_{idx:02d}.txt"
        prompt = prompt_path.read_text(encoding="utf-8")
        cmd = [
            python_exe,
            "-m",
            "nanobot",
            "agent",
            "--config",
            str(config_path),
            "--workspace",
            str(workspace),
            "--session",
            session_id,
            "--message",
            prompt,
            "--no-markdown",
        ]
        try:
            result = subprocess.run(
                cmd,
                cwd=REPO_ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=turn_timeout_seconds,
            )
            content = extract_cli_response(result.stdout)
            returncode = result.returncode
            error_text = ""
            timed_out = False
            stdout_text = result.stdout
            stderr_text = result.stderr
        except subprocess.TimeoutExpired as exc:
            stdout_text = exc.stdout or ""
            stderr_text = exc.stderr or ""
            if isinstance(stdout_text, bytes):
                stdout_text = stdout_text.decode("utf-8", errors="replace")
            if isinstance(stderr_text, bytes):
                stderr_text = stderr_text.decode("utf-8", errors="replace")
            content = f"Error: turn timed out after {turn_timeout_seconds} seconds"
            returncode = 1
            error_text = content
            timed_out = True

        stdout_path = run_root / "outputs" / f"turn_{idx:02d}.stdout.txt"
        stderr_path = run_root / "outputs" / f"turn_{idx:02d}.stderr.txt"
        response_path = run_root / "outputs" / f"turn_{idx:02d}.response.md"
        write_text(stdout_path, stdout_text)
        write_text(stderr_path, stderr_text)
        write_text(response_path, content)

        record = {
            "idx": idx,
            "returncode": returncode,
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
            "response_path": str(response_path),
            "content": content,
        }
        if timed_out:
            record["error"] = error_text
        agent_error = detect_agent_error(content)
        if agent_error and record["returncode"] == 0:
            record["returncode"] = 1
            record["error"] = agent_error
            exit_code = 1
        records.append(record)
        append_jsonl(responses_path, record)

        try:
            assert_allowed_skills(
                workspace,
                list(manifest.get("task_declared_skills", [])),
                str(manifest["skill_mode"]),
            )
        except RuntimeError:
            exit_code = 2
            if not keep_going:
                raise

        if record["returncode"] != 0:
            exit_code = int(record["returncode"])
            if not continue_turns_on_error:
                break

    write_unified_outputs(manifest=manifest, task=task, records=records)
    return exit_code


def run_turns(
    *,
    manifest: dict[str, Any],
    task: dict[str, Any],
    python_exe: str,
    keep_going: bool,
    continue_turns_on_error: bool,
    backend: str,
    turn_timeout_seconds: int,
) -> int:
    if backend == "direct":
        return run_turns_direct(
            manifest=manifest,
            task=task,
            keep_going=keep_going,
            continue_turns_on_error=continue_turns_on_error,
            turn_timeout_seconds=turn_timeout_seconds,
        )
    return run_turns_cli(
        manifest=manifest,
        task=task,
        python_exe=python_exe,
        keep_going=keep_going,
        continue_turns_on_error=continue_turns_on_error,
        turn_timeout_seconds=turn_timeout_seconds,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare and optionally execute isolated nanobot dataset tasks.",
    )
    parser.add_argument("--task-json", default=str(DEFAULT_TASK_JSON))
    parser.add_argument(
        "--task-id",
        action="append",
        default=None,
        help="Task id to run. Can be repeated or comma-separated. Defaults to the first task for compatibility.",
    )
    parser.add_argument("--all-tasks", action="store_true", help="Run every task in task.json.")
    parser.add_argument("--list-tasks", action="store_true", help="List task ids and exit.")
    parser.add_argument("--skill-mode", choices=["on", "off", "both"], default="both")
    parser.add_argument(
        "--skill-policy",
        choices=["available", "required-read", "force-use", "preload"],
        default="available",
        help=(
            "How skill_on exposes task skills: available only lists them, "
            "required-read asks the model to read SKILL.md, force-use requires using it, "
            "preload injects SKILL.md into prompts."
        ),
    )
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--base-config", default=None)
    parser.add_argument("--timezone", default="Asia/Shanghai")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--keep-going", action="store_true")
    parser.add_argument(
        "--continue-turns-on-error",
        action="store_true",
        help="Continue later turns inside the same task after a failed turn. Not recommended for dependent multi-turn benchmarks.",
    )
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument(
        "--turn-timeout",
        type=int,
        default=600,
        help="Maximum seconds to wait for each task turn before marking it failed.",
    )
    parser.add_argument(
        "--max-tool-iterations",
        type=int,
        default=25,
        help="Maximum agent tool/LLM loop iterations per turn. Use 0 to keep the base config value.",
    )
    parser.add_argument(
        "--backend",
        choices=["direct", "cli"],
        default="direct",
        help="Execution backend. direct captures clean response.content; cli captures terminal output.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    task_json = Path(args.task_json).expanduser().resolve()
    task_ids = split_task_ids(args.task_id)
    if args.list_tasks:
        for task in load_tasks(task_json):
            print(task.get("task_id", ""))
        return 0
    tasks = select_tasks(task_json=task_json, task_ids=task_ids, all_tasks=args.all_tasks)
    run_id = args.run_id or timestamp_run_id()

    base_config_path = (
        Path(args.base_config).expanduser().resolve()
        if args.base_config
        else default_base_config_path()
    )
    base_config = load_base_config(base_config_path)
    max_tool_iterations = args.max_tool_iterations if args.max_tool_iterations > 0 else None

    modes = ["on", "off"] if args.skill_mode == "both" else [args.skill_mode]
    runs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for task in tasks:
        for mode in modes:
            manifest = prepare_run(
                task=task,
                skill_mode=mode,
                skill_policy=args.skill_policy,
                run_id=run_id,
                base_config=base_config,
                timezone=args.timezone,
                max_tool_iterations=max_tool_iterations,
                overwrite=args.overwrite,
            )
            runs.append((task, manifest))
            print(f"[prepared] {task.get('task_id')} {mode}: {manifest['run_root']}")

    if not args.execute:
        print(f"Prepared {len(runs)} run(s). Re-run with --execute to call nanobot.")
        return 0

    final_code = 0
    for task, manifest in runs:
        print(f"[execute] {manifest['task_id']} {manifest['skill_mode']}: {manifest['run_root']}")
        code = run_turns(
            manifest=manifest,
            task=task,
            python_exe=args.python,
            keep_going=args.keep_going,
            continue_turns_on_error=args.continue_turns_on_error,
            backend=args.backend,
            turn_timeout_seconds=args.turn_timeout,
        )
        final_code = final_code or code
        print(f"[done] {manifest['task_id']} {manifest['skill_mode']}: exit={code}")
        if code != 0 and not args.keep_going:
            print("Stopped after run error. Re-run with --keep-going to continue later runs after failures.")
            break
    return final_code


if __name__ == "__main__":
    raise SystemExit(main())
