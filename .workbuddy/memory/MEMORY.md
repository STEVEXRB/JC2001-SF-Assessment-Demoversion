# JC2001-SF-Assessment-Demoversion — 项目长期备忘

- 校园二手交易平台 PoC：Flask 2.3 + SQLite + 原生 JS 单页，无框架无构建。
- **运行环境**：系统 python (3.13.5) 未装 Flask/pytest；统一用隔离 venv
  `C:/Users/Huawei/.workbuddy/binaries/python/envs/default/Scripts/python.exe`（Flask 2.3.3 / Werkzeug 2.3.7 / pytest）。
- **数据/资源不在 git 里**：`data.db` 与 `uploads/` 均被 gitignore；演示数据靠 `python seed.py` 重建，9 张演示封面插画由 `demo_covers.py` 生成（write_covers 幂等，不覆盖已有文件）。
- 前端图片兜底：`main.js` 顶部 capture 阶段监听 img error/load，坏图替换为 `.no-img` 占位；图库主图节点不可删除（缩略图切换依赖 `#gallery-main-img`）。
- 测试：`python -m pytest tests/ -q`（86 例，约 2 分多钟，全量跑请用后台/长超时）。
- 演示账号：demo_wang / demo_li / demo_zhang / demo_chen，密码均为 123456。
