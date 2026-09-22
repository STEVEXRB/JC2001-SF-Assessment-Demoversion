# i18n_figures.py - Chinese labels for the diagrams.
#
# Keys are the exact strings the figure modules pass in. Anything absent is left
# alone, which is deliberate: SQL fragments, API paths, file names, attribute
# names and enumerated constants such as ON_SALE stay in their source form
# because that is what the reader must find in the code.

TR = {
    # ---------------------------------------------------------------- titles
    "System context - who and what the PoC interacts with":
        "系统上下文：PoC 与哪些人和系统交互",
    "Use case diagram - Campus Market": "用例图：Campus Market",
    "Business process - one complete second-hand transaction":
        "业务流程：一笔完整的二手交易",
    "Activity diagram - publish a listing": "活动图：发布一件商品",
    "Layered architecture and the responsibility of each layer":
        "分层架构与各层职责",
    "Module decomposition and the direction of each dependency":
        "模块划分与依赖方向",
    "Domain class diagram (persistence-oriented)": "领域类图（面向持久化）",
    "Entity-relationship diagram of the SQLite schema": "SQLite 数据库的实体关系图",
    "State machine governing the life cycle of a listing": "商品状态机",
    "JSON endpoint surface, grouped by resource": "JSON 接口一览（按资源分组）",
    "Client-side view router": "前端视图路由",
    "Technology choices and the reasoning behind them": "技术选型与理由",
    "How a status request is validated before the row is written":
        "状态变更请求在写库前的校验流程",
    "Rendering the conversation list without a query per conversation":
        "用一条聚合查询渲染会话列表",
    "Sequence diagram - publish a listing, from form submit to committed row":
        "时序图：从提交表单到写入数据库的发布流程",
    "Sequence diagram - reserving an item and confirming the sale":
        "时序图：预订商品与确认成交",
    "Sequence diagram - conversation list, opening a thread and sending a reply":
        "时序图：会话列表、打开会话与回复",

    # ---------------------------------------------------------------- subtitles
    "Solid arrows are calls; dashed arrows are returns. Self-calls are work done inside one component.":
        "实线箭头为调用，虚线为返回；自调用为一个组件内部的处理。",
    "Both transitions are validated against the same rule table before either row is written.":
        "两次状态变更在写库前都按同一张规则表校验。",
    "The list is produced by one aggregate query rather than one query per conversation.":
        "会话列表由一条聚合查询产生，而不是每个会话查一次。",
    "The same five-entry rule table drives every transition, so authorisation and state cannot drift apart.":
        "同一张五条目的规则表驱动全部状态变更，权限与状态不会各自走偏。",
    "One grouped aggregate returns the newest message of every thread the caller takes part in.":
        "一条分组聚合查询返回调用者参与的每个会话的最新一条消息。",
    "One lane per role; time flows left to right. Dashed edges cross a lane boundary.":
        "每个角色一条泳道，时间从左向右；虚线表示跨泳道传递。",
    "Rounded bars are decisions; the guard is written on the outgoing edge.":
        "圆角横条为判断节点，分支条件写在出口边上。",
    "One HTML document, five views, and a hash route that makes a single listing shareable.":
        "单个 HTML 文档、五个视图，以及让单件商品可分享的 hash 路由。",
    "23 routes in total: 2 page routes, 21 JSON endpoints. Shaded badges mark methods that need a session.":
        "共 23 条路由：2 条页面路由、21 个 JSON 接口。带底色的方法名表示需要登录会话。",
    "Every component was chosen to keep the proof of concept installable on a laptop with one command.":
        "所有组件的选择标准只有一个：让 PoC 能在一台笔记本上用一条命令装起来。",
    "Highlighted rows are the surviving MAX(id) per partner group.":
        "高亮行是每个会话对象分组中 MAX(id) 的幸存行。",

    # ---------------------------------------------------------------- context
    "City campus": "校园",
    "Visitor": "访客", "unregistered student": "未注册的学生",
    "Registered student": "注册学生", "buyer and seller roles": "兼具买家与卖家身份",
    "Web browser": "浏览器", "renders the single-page client": "渲染单页客户端",
    "Local filesystem": "本地文件系统", "Course assessor": "课程评阅人",
    "installs and evaluates the PoC": "安装并评估 PoC",
    "Campus Market PoC": "Campus Market PoC",
    "Flask web application + client code": "Flask 应用 + 客户端代码",
    "browses": "浏览", "trades": "交易", "file I/O": "文件读写", "runs locally": "本机运行",

    # ---------------------------------------------------------------- use cases
    "Register an account": "注册账号", "Log in": "登录", "Log out": "登出",
    "Browse listings": "浏览商品", "Search and filter listings": "搜索与筛选商品",
    "View listing detail": "查看商品详情", "Read comments": "阅读留言",
    "Publish a listing": "发布商品", "Upload listing photos": "上传商品照片",
    "Edit own listing": "编辑自己的商品", "Take listing offline": "下架商品",
    "Relist an item": "重新上架", "Reserve an item": "预订商品",
    "Confirm the sale": "确认成交", "Cancel a reservation": "取消预订",
    "Save a favourite": "收藏商品", "Post a comment": "发表留言",
    "Send a direct message": "发送私信", "View personal centre": "查看个人中心",
    "not logged in": "未登录", "student": "学生",
    "Campus Market": "Campus Market",

    # ---------------------------------------------------------------- swimlane
    "Buyer": "买家", "Seller": "卖家", "System": "系统",
    "Browse and open": "浏览并打开", "Reserve the item": "预订商品",
    "Reservation appears": "卖家看到预订", "Hand over and confirm": "当面交付并确认",
    "Validate and persist": "校验并落库", "Listing shows as sold": "商品显示为已售",
    "Reject an illegal act": "拒绝非法操作",
    "cancel the reservation  ·  take the listing offline  ·  relist":
        "取消预订 · 下架 · 重新上架",
    "normal flow": "正常流程", "cross-lane handover": "跨泳道传递",
    "error path": "异常路径", "terminal outcome": "终态结果",

    # ---------------------------------------------------------------- activity
    'Open the "Sell an item" view': "打开「出售商品」视图",
    "redirects to the auth view if no session": "无会话时跳转到登录视图",
    "Fill in title, description, price, category and condition":
        "填写标题、描述、价格、分类和成色",
    "Client validation passes?": "前端校验通过？",
    "POST /api/upload with the selected photos": "POST /api/upload 上选中的照片",
    "Is each extension allowed?": "每个扩展名都在白名单内？",
    "Save each file under a random UUID name": "每个文件以随机 UUID 命名保存",
    "POST /api/items with the returned file names": "POST /api/items 带上返回的文件名",
    "Are title and price present?": "标题和价格是否填写？",
    "INSERT into items, then one row per image in images":
        "插入 items，再按照片数逐条插入 images",
    "Commit and return the new item_id": "提交事务并返回新的 item_id",
    "no → 400 / toast": "否 → 400 / 提示", "end": "结束",
    "single transaction": "同一事务", "multipart/form-data": "multipart/form-data",
    "application/json": "application/json", "requires a session": "需要登录会话",

    # ---------------------------------------------------------------- layers
    "Presentation layer": "表示层", "Application layer": "应用层", "Data layer": "数据层",
    "runs in the browser": "运行在浏览器中",
    "Flask route handlers in app.py": "app.py 中的 Flask 路由处理函数",
    "persistence and file storage": "数据持久化与文件存储",
    "5 views + 2 modals +": "5 个视图 + 2 个弹窗 +", "icon sprite": "图标精灵",
    "design tokens ·": "设计令牌 ·", "components · responsive": "组件 · 响应式",
    "state, rendering, event": "状态、渲染、事件", "wiring": "绑定",
    "Auth": "账号", "Catalogue": "商品目录", "Listing CRUD": "商品增删改",
    "Upload": "上传", "Transitions": "状态变更", "Favourites": "收藏",
    "Comments": "留言", "Messaging": "私信", "Personal centre": "个人中心",
    "connection factory ·": "连接工厂 ·",
    "users · items · images ·": "users · items · images ·",
    "comments · messages": "comments · messages",
    "one file per uploaded": "每张已上传", "photo": "照片一张",
    "six relational tables": "六张关系表",
    "fetch() / JSON over HTTP": "fetch() / HTTP 上的 JSON",
    "SQL + file I/O": "SQL + 文件读写",

    # ---------------------------------------------------------------- modules
    "escaped template, no logic": "已转义模板，无业务逻辑",
    "design tokens + components": "设计令牌 + 组件样式",
    "one method per endpoint": "每个接口一个方法",
    "view state and rendering": "视图状态与渲染",
    "Flask app · 21 JSON": "Flask 应用 · 21 个 JSON",
    "login_required · upload": "login_required · 上传",
    "get_db() · init_db()": "get_db() · init_db()",
    "hashing · secure_filename": "密码哈希 · 文件名净化",
    "renders": "渲染", "image files": "图片文件", "SQL": "SQL",
    "queries": "查询", "hash": "哈希",
    "asset": "静态资源", "script": "客户端脚本", "server": "服务端",
    "data": "数据", "library": "第三方库",

    # ---------------------------------------------------------------- classes
    "«enumeration»": "«枚举»", "«generalisation»": "«泛化»",
    "«include»": "«包含»", "«uses»": "«使用»",
    "has photos": "包含照片", "sells": "发布", "writes": "撰写",
    "saved as": "收藏为", "saves": "收藏", "receives comments": "接收留言",
    "refers to": "指向", "about": "关于", "illustrated by": "配图",

    # ---------------------------------------------------------------- state machine
    "visible in the catalogue": "在目录中可见", "held for one buyer": "为一位买家保留",
    "terminal outcome": "终态", "hidden, reversible": "不可见但可恢复",
    "initial": "初始",
    "reserve": "reserve", "actor: buyer": "角色：买家",
    "sell": "sell", "actor: seller": "角色：卖家",
    "cancel_reserve  ·  actor: seller": "cancel_reserve · 角色：卖家",
    "off_shelf  ·  actor: seller": "off_shelf · 角色：卖家",
    "relist  ·  actor: seller": "relist · 角色：卖家",

    # ---------------------------------------------------------------- sequences
    "main.js": "main.js", "controller and view state": "控制器与视图状态",
    "api.js": "api.js", "one method per endpoint": "每个接口一个方法",
    "app.py": "app.py", "Flask route handler": "Flask 路由处理函数",
    "models + SQLite": "models + SQLite", "connection and tables": "连接与数据表",
    "Buyer browser": "买家浏览器", "detail view": "商品详情页",
    "app.py": "app.py", "status endpoint": "状态变更接口",
    "SQLite": "SQLite", "items table": "items 表",
    "Seller browser": "卖家浏览器",
    "main.js": "main.js", "profile view and chat panel": "个人中心与聊天面板",
    "app.py": "app.py", "message endpoints": "私信接口",
    "SQLite": "SQLite", "messages table": "messages 表",

    "validate the form": "校验表单", "check files": "检查文件",
    "uploadImages(formData)": "uploadImages(formData)",
    "POST /api/upload": "POST /api/upload",
    "@login_required": "@login_required", "allowed_file()": "allowed_file()",
    "save as <uuid>.ext": "以 <uuid>.ext 保存", "saved file names": "已保存的文件名",
    "resolved image names": "解析出的图片名",
    "createItem({ title, price, … })": "createItem({ title, price, … })",
    "POST /api/items  ·  JSON": "POST /api/items · JSON",
    "re-validate input": "服务端再校验输入",
    "INSERT INTO items": "INSERT INTO items",
    "item_id ← lastrowid": "item_id ← lastrowid",
    "INSERT INTO images": "INSERT INTO images",
    "commit and close": "提交并关闭连接", "toast + reload": "提示 + 刷新列表",

    "POST /items/42/status  ·  reserve": "POST /items/42/status · reserve",
    "look up the rule": "查规则表",
    "SELECT * FROM items WHERE id = 42": "SELECT * FROM items WHERE id = 42",
    "status = 'ON_SALE'": "status = 'ON_SALE'",
    "UPDATE … SET status = 'RESERVED'": "UPDATE … SET status = 'RESERVED'",
    "200 · status updated": "200 · 状态已更新",
    "toast and re-render": "提示并重新渲染",
    "POST /items/42/status  ·  sell": "POST /items/42/status · sell",
    "status = 'RESERVED'": "status = 'RESERVED'",
    "UPDATE … SET status = 'SOLD'": "UPDATE … SET status = 'SOLD'",

    "GET /api/messages   (conversation list)": "GET /api/messages（会话列表）",
    "one aggregate query": "一条聚合查询",
    "SELECT … MAX(id) … GROUP BY CASE …": "SELECT … MAX(id) … GROUP BY CASE …",
    "one row per partner, newest first": "每个对象一行，最新的在前",
    "200 { data: [ … ] }": "200 { data: [ … ] }",
    "render the list": "渲染列表",
    "GET /api/messages/7   (open a thread)": "GET /api/messages/7（打开会话）",
    "SELECT … both directions, ordered by time":
        "SELECT … 两个方向，按时间排序",
    "UPDATE … SET is_read = 1": "UPDATE … SET is_read = 1",
    "render the bubbles": "渲染气泡",
    "POST /api/messages   { receiver_id: 7, … }":
        "POST /api/messages { receiver_id: 7, … }",
    "INSERT INTO messages ( … )": "INSERT INTO messages ( … )",
    "200 · message sent": "200 · 消息已发送",
    "re-fetch the thread": "重新拉取该会话",

    # ---------------------------------------------------------------- route map
    "Accounts": "账号", "Catalogue": "商品目录", "Listing management": "商品管理",
    "Media": "媒体", "Transactions": "交易", "Social": "社交",
    "Personal centre": "个人中心",
    "public": "公开", "session": "需会话",

    # ---------------------------------------------------------------- ui states
    "persistent header  ·  brand   ·   search   ·   \"Sell an item\"   ·   avatar menu":
        "常驻页头  ·  品牌   ·  搜索  ·  「出售商品」  ·  头像菜单",
    "brand": "品牌", "Log in / Sign up": "登录 / 注册", "avatar menu": "头像菜单",
    "home": "首页", "catalogue, filters": "目录与筛选",
    "auth": "登录注册", "log in / sign up": "登录 / 注册",
    "profile": "个人中心", "4 tabs": "4 个标签页",
    "detail": "详情", "gallery, comments": "图廊与留言",
    "publish": "发布", "form + live preview": "表单 + 实时预览",
    "open a card   ·   #item-<id>   ·   back": "打开商品卡  ·  #item-<id>  ·  返回",
    "log in  ·  log out": "登录  ·  登出",
    "\"Sell an item\"": "「出售商品」",
    "requires a session": "需要登录会话",
    "anyone": "任何人可访问", "session required": "需要登录会话",

    # ---------------------------------------------------------------- status guard
    "transitions (server-side rule table)": "transitions（服务端规则表）",
    "action  →  from  →  to  →  role": "操作 → 原状态 → 新状态 → 角色",
    "Is the action known?": "操作是否已知？",
    "Does the item exist?": "商品是否存在？",
    "Does the caller hold the role?": "调用者是否具备该角色？",
    "Is the stored status the required source?": "当前状态是否为要求的原状态？",
    "UPDATE items SET status = ?": "UPDATE items SET status = ?",
    "400 invalid action": "400 非法操作", "404 not found": "404 未找到",
    "403 refused": "403 拒绝", "400 refused": "400 拒绝",
    "200 one row changed": "200 修改一行",
    "buyer": "买家", "seller": "卖家",

    # ---------------------------------------------------------------- conversation aggregate
    "messages table (before)": "messages 表（处理前）",
    "sender, receiver, content, created_at": "sender、receiver、content、created_at",
    "id": "id", "sender": "sender", "receiver": "receiver", "content": "content",
    "single aggregate query": "一条聚合查询",
    "Is the bike still availabl": "自行车还在吗",
    "Yes, free tomorrow.": "在的，明天有空。",
    "Can we meet at the library": "能在图书馆碰面吗？",
    "Textbook still on sale?": "教材还在卖吗？",
    "Still on sale.": "还在卖。",
    "Great, I'll take it.": "好，我要了。",

    # ---------------------------------------------------------------- stack
    "Python 3.8+": "Python 3.8+", "language": "实现语言",
    "already available on the lab and staff machines; no runtime purchase":
        "机房和教师机上已装好，无需额外采购运行时",
    "Flask 2.3.3": "Flask 2.3.3", "web framework": "Web 框架",
    "routing, sessions and JSON helpers in one small dependency":
        "路由、会话与 JSON 处理，只引入一个小依赖",
    "Werkzeug 2.3.7": "Werkzeug 2.3.7", "security utilities": "安全工具",
    "password hashing and secure_filename without extra libraries":
        "密码哈希与文件名净化，不用再加库",
    "SQLite 3": "SQLite 3", "database": "数据库",
    "file-based, no server to install; the schema travels with the submission":
        "文件型，无需安装服务端；数据库随作业一起提交",
    "Vanilla JS / CSS": "原生 JS / CSS", "client": "客户端",
    "no build step, no node_modules; the marker opens index.html from Flask":
        "无构建步骤、无 node_modules；由 Flask 直接打开 index.html",
    "SQL + file I/O": "SQL + 文件读写",
    "endpoints": "接口",
    "one file per photo": "每张照片一行",
    "one file per uploaded": "每张已上传",
    "«unique» (user_id, item_id)": "«唯一» (user_id, item_id)",
    "Registered": "注册学生",
    "demo": "示例",
    "SQL + file I/O": "SQL + 文件读写",
    "endpoints": "接口",
    "one file per photo": "每张照片一行",
    "one file per uploaded": "每张已上传",
    "«unique» (user_id, item_id)": "«唯一» (user_id, item_id)",
    "Registered": "注册学生",
    "demo": "示例",
    "Playwright + Edge": "Playwright + Edge", "verification": "验证工具",
    "used to capture the interface states reproduced in this report":
        "用于抓取本报告中的界面状态",
}


def install():
    import svgkit
    svgkit.set_translation(TR)
    return TR
