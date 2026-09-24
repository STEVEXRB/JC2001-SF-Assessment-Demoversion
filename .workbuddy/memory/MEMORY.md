# MEMORY.md — JC2001-SF-Assessment 项目长期记忆

## 项目是什么

JC2001 软件工程导论课程作业（AI 组 9）：**校园二手交易平台 PoC**——
Flask + SQLite + 原生前端，23 个路由、6 张表、约 3,356 行运行时代码。
工作目录 `C:\Users\Administrator\Desktop\JC2001-SF-Assessment`。

## 交付物与规格（来自课程要求 PDF，别记错）

这两份文档的规格是**外部强制**的，改动内容前先回看：

| 交付物 | 页数要求 | 说明 |
|---|---|---|
| Project Proposal | 正文 **4–8 页**（标题页不计） | 必交、不计分。按官方模板：Problem / Solution / Objectives / Benefits / Timeline / Action plan |
| Technical Report | 正文 **40–60 页** | 占组项目分 50%。标题页 → 目录 → 图目录 → 表目录 → 八章 → References → 附录 A（Workload Profile）|
| PoC 软件 | — | 占 30%，ZIP：源码 + 可运行版 + 8–12 页 PDF 用户手册 |
| Presentation | — | 占 20%，PPT + 含出镜的 MP4 |

共同排版硬指标：**A4、四边 1 英寸、单栏、12pt、Times New Roman、1.5 倍行距，交单个 PDF**。
源码不得进正文。「正文页数」只算 Introduction 到 Conclusions 之间，前后附件不计。

## 做文档时反复用到的约定

- 生成脚本在 `.workbuddy/build/`：`docxkit.py`（排版引擎）、`svgkit.py`（图表库）、
  `figures_*.py`（图形）、`charts.py`（matplotlib）、`shots.js`（界面截图）、
  `crop_ui.py`（裁切）、`build_report.py` / `build_proposal.py`、`convert.ps1`（Word→PDF）。
  **全部可重跑**，改内容后按 build → PowerShell 点源 convert.ps1 → 读 convert.log 的顺序迭代。
- 报告用**两遍渲染**：第 1 遍占位页码并 dump 每个图表标题的真实页码，第 2 遍写入终版。
  正文目录用 Word TOC 域；图目录/表目录用静态表（Word 的 `TOC \c` 需要 SEQ 域，不稳）。
- 图表编号用 `number=` 参数可**覆盖**：搬动表格到附录时用它锁住表号，正文引用就不用改。
- 图表可读性经验公式：`纸面 pt = font_px / canvas_w_px × 插入宽度(in) × 72`。
  图形画布建议做窄（~620px 有效宽），**别做 1000px 宽配 9px 字**——缩到栏宽后只有 4pt，不可读。
- 界面截图：视口用 **1240×900**（>1040 才触发详情页双栏），先拍视口再拍整页
  （整页截图会留下滚动位置），然后按区域裁切用小宽度插入以保证文字可读。
- 报告里的测试/性能数字**必须来自真实运行**：`tests/` 下 80 个 pytest 用例 +
  `benchmark.py` + `scale.py`。当前 80 个全过；500 条商品下读取中位 1.9–3.5ms。

## 已知事实与遗留

- 演示数据：4 个账号（demo_wang / demo_li / demo_zhang / demo_chen，密码均 123456）、
  11 件商品、6 个用户（含 2 个历史账号）。空库备份 `data.db.backup-20260919`。
- **截图流程会改演示数据**（点收藏会切换状态）——每次都跑的话记得还原。
- 已知真实缺陷（报告里如实写了，未修）：会话列表 `ORDER BY created_at` 在同秒内次序不确定；
  上传的三张照片上限与"至少一张"只在客户端校验；`app.secret_key` 硬编码；外键未开 pragma。
- 用户偏好：交付物要**观感与完成度**，英文学术文档，不要编造数据。

## 给用户的默认答复口径

- 结论先行 + 说清取舍；顺手发现的问题一并说明。
- 涉及页面/份数的硬指标，直接给实测数字（页数、字数），别只说"已完成"。
