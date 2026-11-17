from html import escape
from pathlib import Path
from sys import argv

PUBLIC = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parent
NAV = {
    "": "首页",
    "projects/agent/": "Agent 项目",
    "research/": "科研项目",
    "projects/": "工程项目",
    "blog/": "技术博客",
    "resume/": "个人简历",
    "about/": "关于我",
}
GITHUB = "https://github.com/Mster111-zhang"


def local(prefix, route):
    return prefix + route + "index.html"


def section_for(route):
    return max((section for section in NAV if route.startswith(section)), key=len)


def page(route, title, description, body):
    prefix = "../" * route.count("/")
    active = section_for(route)
    nav = "".join(
        f'<a href="{local(prefix, path)}"'
        + (' aria-current="page"' if path == active else "")
        + f">{label}</a>"
        for path, label in NAV.items()
    )
    heading = "张艺豪 · 个人网站" if not route else f"{title} · 张艺豪"
    document = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#102724">
  <meta name="description" content="{escape(description)}">
  <title>{escape(heading)}</title>
  <link rel="icon" type="image/png" sizes="32x32" href="{prefix}favicon.png">
  <link rel="stylesheet" href="{prefix}style.css">
</head>
<body>
  <a class="skip" href="#main">跳到正文</a>
  <header class="topbar">
    <div class="shell header-inner">
      <a href="{local(prefix, '')}" class="brand" aria-label="张艺豪，返回首页">
        <img src="{prefix}favicon.png" width="32" height="32" alt="">
        <span>张艺豪</span>
      </a>
      <nav aria-label="主导航">{nav}</nav>
    </div>
  </header>
  <main id="main">
    {body}
  </main>
  <footer id="contact" class="footer">
    <div class="shell footer-inner">
      <span>© 张艺豪</span>
      <div><a href="{GITHUB}">GitHub</a><a href="{local(prefix, 'about/')}#credits">图片来源</a></div>
    </div>
  </footer>
</body>
</html>
"""
    target = PUBLIC / route / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(document, encoding="utf-8")


def lead(title, text):
    return f'<section class="page-lead"><div class="shell"><h1>{title}</h1><p>{text}</p></div></section>'


def card(prefix, route, title, label, description, image=None, action="查看项目"):
    cover = ""
    if image:
        cover = f"""<a class="card-image" href="{local(prefix, route)}" tabindex="-1" aria-hidden="true">
        <img src="{prefix}{image}" alt="" loading="lazy" decoding="async"></a>"""
    return f"""<article class="card">
      {cover}
      <div class="card-content">
        <p class="metadata">{label}</p>
        <h3><a href="{local(prefix, route)}">{title}</a></h3>
        <p>{description}</p>
        <a class="text-link" href="{local(prefix, route)}" aria-label="{action}：{title}">{action} <span aria-hidden="true">↗</span></a>
      </div>
    </article>"""


def detail(route, title, label, description, sections):
    prefix = "../" * route.count("/")
    back_route = section_for(route)
    back_title = NAV[back_route]
    contents = "".join(f'<h2>{name}</h2>{body}' for name, body in sections)
    body = f"""<article class="shell article-shell">
      <div class="article-heading">
        <a class="back" href="{local(prefix, back_route)}">← 返回{back_title}</a>
        <p class="metadata">{label}</p>
        <h1>{title}</h1>
        <p class="dek">{description}</p>
      </div>
      <div class="prose">{contents}</div>
    </article>"""
    page(route, title, description, body)


MRI = (
    "research/cardiac-mri/",
    "基于心脏 MRI 的心肌功能评估",
    "硕士研究课题 · 2025.12 至今",
    "从心脏 MRI 自动分割心室与心肌，探索薄壁和边界的精细表征，并开发功能量化原型。",
    "assets/cardiac-mri-comparison.png",
)
AGENT = (
    "projects/agent/",
    "Agent 项目",
    "大模型应用 · 工作流编排",
    "记录我做过的 Agent 应用，包括工具调用、流程编排和结果展示。",
    "assets/dify-query-workflow.png",
)
TEXT_TO_SQL = (
    "projects/agent/text-to-sql/",
    "自然语言查数与图表生成",
    "独立完成 · Text-to-SQL",
    "用自然语言查询 MySQL，自动生成并执行 SQL，再返回文字汇总与 ECharts 图表。",
)
MORE_AGENT_PROJECTS = ()
HEALTH = (
    "projects/health-records/",
    "公共卫生健康档案系统",
    "本科毕业设计 · Java 后端",
    "面向居民、医生与管理员，覆盖档案管理、异常预警、统计分析和跨机构查询。",
)
PARKING = (
    "projects/smart-parking/",
    "智慧停车管理系统",
    "实习项目 · 2023.09–2024.01",
    "参与智慧停车系统开发，使用 MVC 组织业务代码，通过 MySQL 事务保障数据一致性。",
)
PATIENT_NOTE = "blog/patient-split/"
AGENT_NOTE = "blog/agent-workflow/"


def note_links(prefix):
    return f"""<div class="note-list">
      <article><p class="metadata">医学影像</p>
        <h3><a href="{local(prefix, PATIENT_NOTE)}">医学影像分割为什么要按患者划分数据</a></h3>
        <p>从相邻切片的相似性出发，理解患者级划分如何减少数据泄漏。</p>
      </article>
      <article><p class="metadata">Agent 开发</p>
        <h3><a href="{local(prefix, AGENT_NOTE)}">从工作流入门大模型 Agent</a></h3>
        <p>用知识问答理解节点、工具、状态和结果评估。</p>
      </article>
    </div>"""


homepage = f"""<section class="home-hero" aria-labelledby="hero-title">
  <div class="shell hero-content">
    <p>东北林业大学 · 计算机技术硕士</p>
    <h1 id="hero-title">张艺豪</h1>
    <p class="hero-description">Agent 应用开发 · 心脏 MRI 研究</p>
    <p class="hero-goal">预计 2028 年毕业，正在寻找 Agent 应用开发实习。</p>
    <div class="hero-actions">
      <a class="button solid" href="#projects">查看项目 <span aria-hidden="true">↓</span></a>
      <a class="button outline" href="resume/index.html">个人简历 <span aria-hidden="true">↗</span></a>
      <a class="button outline" href="{GITHUB}">GitHub <span aria-hidden="true">↗</span></a>
    </div>
  </div>
</section>
<div class="shell home-body">
  <section id="about" class="intro-panel">
    <div>
      <h2>关于我</h2>
      <dl class="education">
        <div><dt>东北林业大学</dt><dd>计算机技术 · 硕士在读</dd></div>
        <div><dt>黑龙江工程学院</dt><dd>智能科学与技术 · 本科</dd></div>
      </dl>
    </div>
    <div>
      <p>我正在研究心脏 MRI 分割与功能量化，也在做把大模型接到数据库与工具上的应用。</p>
      <ul class="tags" aria-label="技术方向"><li>Agent 工作流</li><li>Python / PyTorch</li><li>MySQL</li><li>Java 后端</li></ul>
    </div>
  </section>
  <section id="projects" class="home-section">
    <div class="section-heading"><h2>项目方向</h2></div>
    <div class="card-grid">
      {card("", "research/", "科研项目", "医学影像 · 硕士课题", "心脏 MRI 分割、模型评估与心功能量化。", MRI[4], action="进入栏目")}
      {card("", *AGENT, action="进入栏目")}
      {card("", "projects/", "工程项目", "Java 后端 · 工程实践", "本科毕设、实习开发和业务系统。", action="进入栏目")}
    </div>
  </section>
  <section id="experience" class="home-section">
    <div class="section-heading"><h2>实习经历</h2><a class="text-link" href="resume/index.html">查看简历 ↗</a></div>
    <div class="note-list">
      <article><p class="metadata">2023.09–2024.01 · 开发实习</p>
        <h3>华育兴业科技哈尔滨分公司</h3>
        <p>参与智慧停车管理系统开发，用 Spring Boot 组织后端业务，通过 MySQL 事务保障数据一致性。</p>
      </article>
      <article><p class="metadata">统计与档案管理实习</p>
        <h3>陕州区柴洼卫生院</h3>
        <p>协助日常收费、统计和居民健康档案维护。</p>
      </article>
    </div>
  </section>
  <section id="articles" class="home-section">
    <div class="section-heading"><h2>技术笔记</h2><a class="text-link" href="blog/index.html">全部笔记 ↗</a></div>
    {note_links("")}
  </section>
</div>"""
page("", "首页", "张艺豪的技术主页，记录 Agent 应用开发、心脏 MRI 研究与工程实践。", homepage)

page("research/", "科研项目", "心脏 MRI 分割与心肌功能评估。",
     lead("科研项目", "心脏 MRI 分割、模型对比与心肌功能量化。")
     + f'<div class="shell collection"><div class="card-grid one">{card("../", *MRI)}</div></div>')

page("projects/", "工程项目", "本科毕设、实习开发和 Java 后端项目。",
     lead("工程项目", "本科毕设、实习开发和业务系统。")
     + f'<div class="shell collection"><div class="card-grid">{card("../", *HEALTH)}{card("../", *PARKING)}</div></div>')

additional_agent_cards = "".join(card("../../", *project) for project, _ in MORE_AGENT_PROJECTS)
project_slots = '<div class="project-slot">预留项目位</div>' * max(0, 2 - len(MORE_AGENT_PROJECTS))

page(AGENT[0], AGENT[1], AGENT[3], lead(AGENT[1], AGENT[3])
     + f"""<div class="shell collection">
       <article class="paper-panel agent-case">
         <p class="metadata">{TEXT_TO_SQL[2]}</p>
         <h2><a href="{local("../../", TEXT_TO_SQL[0])}">{TEXT_TO_SQL[1]}</a></h2>
         <p>{TEXT_TO_SQL[3]}</p>
         <ul class="tags" aria-label="项目技术"><li>MySQL</li><li>SQL 工具调用</li><li>ECharts</li></ul>
         <div class="case-gallery">
           <figure><a href="../../assets/dify-query-result.png"><img src="../../assets/dify-query-result.png" width="1660" height="984" alt="查询年级平均成绩，返回文字总结和柱状图"></a><figcaption>查数与图表输出</figcaption></figure>
           <figure><a href="../../assets/dify-query-workflow.png"><img src="../../assets/dify-query-workflow.png" width="1636" height="739" alt="从生成 SQL 到执行查询和图表输出的完整工作流"></a><figcaption>工作流节点图</figcaption></figure>
         </div>
         <a class="text-link" href="{local("../../", TEXT_TO_SQL[0])}">查看实现细节 ↗</a>
       </article>
       <section class="project-followup card-grid" aria-label="更多项目">
         {additional_agent_cards}
         {project_slots}
       </section>
     </div>""")

page("blog/", "技术博客", "医学影像与大模型 Agent 学习笔记。",
     lead("技术博客", "从实验和开发中遇到的具体问题出发。")
     + f'<div class="shell collection">{note_links("../")}</div>')

detail(*MRI[:4], [
    ("分割结果示例", """<figure class="article-image result-figure">
      <a href="../../assets/cardiac-mri-comparison.png" aria-label="打开高分辨率心脏 MRI 分割对比图">
        <img src="../../assets/cardiac-mri-comparison.png" width="1405" height="645"
          alt="同一心脏 MRI 切片的原始影像、人工标注和模型预测。红色是左心室，黄色是心肌，蓝色是右心室。">
      </a>
      <figcaption>同一验证切片，左为原始影像，中为人工标注，右为模型预测。点击可查看原图。图像经裁切并叠加标注和预测轮廓。数据来源 <a href="https://doi.org/10.1109/TMI.2018.2837502">Bernard 等，ACDC</a> · <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a></figcaption>
    </figure>"""),
    ("研究背景", "<p>心脏 MRI 可以用来观察心室和心肌的结构。要从图像进一步估算心室容积与射血分数，需要先准确地识别这些结构。心肌薄壁或心室边界分得不够细，都可能影响后续量化。</p>"),
    ("我做了什么", "<ol><li>用 Python 和 PyTorch 搭建分割实验框架，统一数据预处理、空间几何对齐、训练、推理和评价流程。</li><li>按患者划分数据，实现左心室、右心室与心肌的自动分割，在 ACDC 数据集上完成五类模型的首轮基准训练与验证。</li><li>围绕改良 U-Net 探索内容感知上采样和多尺度语义融合，进行结构筛选和模块对照分析。</li></ol>"),
    ("评估与当前进展", '<p>用 Dice 查看预测与标注的重叠程度，用 HD95 查看边界距离，并结合逐病例误差分析定位典型失误。流程支持预测可视化和实验报告导出，已开发心室容积和射血分数计算原型。</p><p><a href="../../blog/patient-split/index.html">相关笔记：医学影像为什么要按患者划分数据</a></p>'),
])

detail(*TEXT_TO_SQL, [
    ("运行效果", """<figure class="article-image result-figure">
      <a href="../../../assets/dify-query-result.png">
        <img src="../../../assets/dify-query-result.png" width="1660" height="984"
          alt="Dify 预览中输入查询全年级平均成绩，工作流返回文字统计和各年级平均成绩柱状图。">
      </a>
      <figcaption>输入「查询全年级平均成绩」后，工作流返回各年级的平均成绩、文字汇总和对比柱状图。点击可查看原图。</figcaption>
    </figure>"""),
    ("工作流设计", """<figure class="article-image result-figure">
      <a href="../../../assets/dify-query-workflow.png">
        <img src="../../../assets/dify-query-workflow.png" width="1636" height="739" loading="lazy"
          alt="Dify Chatflow 节点图，依次生成 SQL、迭代执行查询、汇总结果，并按图表类型分支输出。">
      </a>
      <figcaption>Dify Chatflow 的完整节点图。点击可查看原图。</figcaption>
    </figure>
    <p>我独立搭建了整套 Chatflow，并接入 MySQL，串联从提问到结果展示的各个环节。</p>
    <ol>
      <li><strong>生成查询</strong>　让大模型将自然语言问题转为 SQL，通过代码节点解析待执行的语句。</li>
      <li><strong>执行与汇总</strong>　在迭代节点调用 SQL 执行工具查询 MySQL，整理返回的数据，再交给模型生成文字摘要。</li>
      <li><strong>图表展示</strong>　根据汇总结果生成 ECharts 参数，通过条件分支输出折线图、柱状图或饼图。</li>
    </ol>"""),
])

for project, sections in MORE_AGENT_PROJECTS:
    detail(*project[:4], sections)

detail(*HEALTH, [
    ("项目背景", "<p>居民、医生和管理员在健康档案管理中需要完成不同操作。本科毕设围绕这些使用场景，开发了档案录入、查询、预警和统计功能。</p>"),
    ("我做了什么", "<ol><li>使用 Spring Boot、MySQL、Redis 和 Bootstrap，按使用场景设计档案录入、查询和异常预警模块。</li><li>根据血糖异常等规则触发短信提醒，用图表展示疫苗接种率与慢性病趋势。</li><li>设计并实现过敏史查询 RESTful API，提供跨机构查询相关档案信息的接口。</li></ol>"),
])

detail(*PARKING, [
    ("实习项目", "<p>在北京华育兴业科技有限公司哈尔滨分公司实习期间，我参与了智慧停车管理系统开发。项目使用 Spring Boot、MySQL、JSP、Tomcat 和百度地图 SDK。</p>"),
    ("我做了什么", "<p>按 MVC 划分页面交互、业务逻辑和数据访问，使用 Spring Boot 整合配置。在业务写入涉及多步操作的场景中，使用 MySQL 事务保障原子性和一致性。</p>"),
])

detail(PATIENT_NOTE, "医学影像分割为什么要按患者划分数据", "医学影像 · 学习笔记",
       "把同一患者的影像留在同一个数据集合，评估更接近模型遇到新病例时的表现。", [
           ("问题出在哪", "<p>一个患者的影像可以包含多张相邻切片。这些切片往往相似。如果逐张随机分配，训练集和验证集可能出现来自同一患者的切片，使验证结果偏乐观。</p>"),
           ("怎么划分", "<p>先按患者编号确定训练、验证和测试集合，再按归属放入该患者的全部样本。划分后可以检查三组患者编号是否有交集，并保存划分清单，便于用同一协议比较多个模型。</p>"),
           ("怎么读结果", "<p>整体 Dice 或 HD95 适合比较模型，逐病例结果则能提醒我们哪些样本值得回看。把原图、标注和预测放在一起，更容易判断偏差出现在心肌薄壁还是心室边界。</p>"),
       ])

detail(AGENT_NOTE, "从工作流入门大模型 Agent", "Agent 开发 · 学习笔记",
       "用一个知识问答的例子理解输入、检索、生成、状态与评价。", [
           ("从一个简单工作流开始", "<p>一个知识问答工作流可以先接收问题，接着检索资料，最后根据资料组织回答。把任务拆开，就能分别检查检索是否找对材料、模型是否引用了有用的证据。</p>"),
           ("把节点的输入和输出写清楚", "<p>问题、检索片段和引用来源可以成为节点之间传递的状态。当检索结果不足时，可以设计一个分支返回补充信息的提示，而不是让模型继续猜测。</p>"),
           ("先检查能否稳定回答", "<p>用几条已知有答案的问题检查检索与生成，再加一条资料里没有答案的问题，观察流程如何处理。这个例子可以作为学习 Dify 工作流或 LangGraph 编排时的检查思路。</p>"),
       ])

resume = """<div class="shell collection resume-body">
  <section class="paper-panel"><h2>教育经历</h2>
    <p><strong>东北林业大学</strong> · 计算机技术硕士在读 · 预计 2028 年毕业</p>
    <p>相关课程包括深度学习、高级算法设计与分析、现代优化方法和模式识别。</p>
    <p><strong>黑龙江工程学院</strong> · 智能科学与技术本科 · 2021.09–2025.06</p>
  </section>
  <section class="paper-panel"><h2>技术能力</h2>
    <ul><li><strong>Agent 应用开发</strong>　用 Dify 独立搭建 Text-to-SQL 工作流并接入 MySQL。了解 LangChain、LangGraph、RAG 和 vLLM 基础。</li>
    <li><strong>医学影像</strong>　用 Python、PyTorch 开展心脏 MRI 分割、基准实验与逐病例误差分析。</li>
    <li><strong>后端开发</strong>　使用 Java、Spring Boot、RESTful API、MySQL 和 Redis。</li></ul>
  </section>
  <section class="paper-panel"><h2>代表项目与实习</h2>
    <ul><li><a href="../projects/agent/text-to-sql/index.html">自然语言查数与图表生成</a> · 独立完成</li>
    <li><a href="../research/cardiac-mri/index.html">心脏 MRI 心肌功能评估</a> · 硕士研究课题</li>
    <li><a href="../projects/health-records/index.html">公共卫生健康档案系统</a> · 本科毕业设计</li>
    <li><a href="../projects/smart-parking/index.html">智慧停车管理系统</a> · 北京华育兴业科技有限公司哈尔滨分公司</li>
    <li>陕州区卫生院 · 协助日常收费、统计和居民健康档案维护。</li></ul>
  </section>
  <section class="paper-panel"><h2>证书与校园经历</h2>
    <p>软件设计师（软考中级）、CET-4。曾任校健美社团社长及院资助发展中心部长，获得过校内奖学金和优秀个人、优秀干部等荣誉。</p>
  </section>
</div>"""
page("resume/", "个人简历", "张艺豪的教育、项目、技能与实习经历。",
     lead("个人简历", "张艺豪 · 东北林业大学计算机技术硕士在读") + resume)

about = f"""<div class="shell collection about-body">
  <section class="paper-panel"><h2>个人简介</h2>
    <p>我是张艺豪，目前在东北林业大学读计算机技术硕士，预计 2028 年毕业。我的课题围绕心脏 MRI 分割，希望从影像结构进一步提取能够描述心室功能的指标。</p>
    <p>我也在学习 Agent 工作流和知识问答，关注如何把模型接到工具和已有业务系统上。我本科做过 Java 后端开发，参与过智慧停车项目，也做过公共卫生健康档案系统。</p>
  </section>
  <section class="paper-panel"><h2>联系</h2>
    <p>欢迎交流 Agent 应用开发、医学影像研究和实习机会。</p>
    <p><a href="{GITHUB}">GitHub 主页 ↗</a></p>
  </section>
  <section class="paper-panel" id="credits"><h2>图片来源</h2>
    <ul>
      <li>心脏 MRI 分割对比图 · <a href="https://doi.org/10.1109/TMI.2018.2837502">Bernard 等，ACDC</a> · <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a></li>
      <li>自然语言查数工作流与运行结果 · 项目截图</li>
    </ul>
  </section>
</div>"""
page("about/", "关于我", "张艺豪的个人简介、GitHub 主页与图片来源。",
     lead("关于我", "计算机技术研究生，关注 Agent 应用开发与医学影像分析。") + about)

