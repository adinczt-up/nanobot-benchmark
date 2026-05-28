# Nanobot Benchmark Overlay

本仓库不包含 nanobot 框架源码。使用者需要先准备好自己的 nanobot 项目，然后将本仓库内容放到 nanobot 根目录下运行。

## 内容

- isolated_benchmark_runner/: 隔离运行与评测脚本
- datasets/: task.json、数据文件、skills
- runs/: 已完成的运行结果、轨迹、统一输出和测评结果
- .nanobot/config.example.json: 示例模型配置，不含真实 API Key

## 使用方式

1. 将本仓库内容放到 nanobot-main 根目录。
2. 配置 .nanobot/config.json。
3. 使用 isolated_benchmark_runner/run_isolated_task.py 运行任务。
4. 使用 isolated_benchmark_runner/evaluate_task_outputs.py 进行测评。

## 查看任务

.\.venv\Scripts\python.exe isolated_benchmark_runner\run_isolated_task.py --list-tasks

## 测评当前结果

.\.venv\Scripts\python.exe isolated_benchmark_runner\evaluate_task_outputs.py `
  --judge llm `
  --judge-timeout 180 `
  --run-root runs\task_company_weekly_order_risk `
  --run-root runs\task_company_weekly_sales_performance `
  --run-root runs\task_earthwork_cost_control_review `
  --run-root runs\task_earthwork_rate_breakdown `
  --run-root runs\task_gaokao_shandong_2025_recommendation\skill_on\exp_gaokao_rerun `
  --run-root runs\task_gaokao_shandong_2025_recommendation\skill_off\exp_gaokao_rerun `
  --output-json runs\evaluation_summary_latest10.json `
  --output-md runs\evaluation_summary_latest10.md

## 结果说明

gaokao 任务请以 exp_gaokao_rerun 为准。
