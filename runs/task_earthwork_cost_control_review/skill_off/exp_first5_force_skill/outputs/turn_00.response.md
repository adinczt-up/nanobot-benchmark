本次成本复盘锁定的项目是 **PRJ-003 — 河道泵站基坑开挖**。

我是从以下项目资料中定位到的：

1. **`project_briefs.csv`**（项目简介表）——第4行明确记录了 PRJ-003 的基本信息：
   - 项目名称：河道泵站基坑开挖
   - 项目类型：infrastructure（基础设施）
   - 交付方式：CM-at-risk
   - 所在地：上海
   - 范围描述：泵站基坑开挖、弃土运输与回填压实
   - 工期：8个月
   - 估算类型：detailed（详细估算）
   - 关键假设：围护已另行发包，本场景仅覆盖土方专业
   - 排除项：不含主体结构与机电安装

2. **`selection_manifest.json`**（数据选取清单）——确认本次数据子集聚焦于 **Shanghai earthwork and site-preparation estimating subset**（上海土方与场地准备估算子集），MasterFormat 分区为 `31 00 00`（土方工程），与 PRJ-003 的土方专业定位一致。

3. 其余数据表（`boq_items.csv`、`subcontractor_quotes.csv`、`change_orders.csv`、`monthly_cost_reports.csv`）中均包含 PRJ-003 的专属记录，进一步印证本次分析范围锁定在 PRJ-003。