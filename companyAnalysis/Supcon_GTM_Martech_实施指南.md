# Supcon GTM Martech 具体实施指南

**基于**：Supcon Marketing Technology Recommendations 既定架构与阶段规划  
**参照**：GTM Engineer、Senior Lifecycle Marketing Manager、Senior Product Marketing Manager 岗位职责与行业实践  
**目标**：将「产品/行为数据 → 线索/商机」的闭环落地为可执行步骤，并明确各阶段数据与技术的使用方式；覆盖生命周期营销（首触→高价值用户、培育、再激活、多区域）与**产品营销**（定位与叙事、发布 GTM、销售赋能、竞争与品类领导）的设计与协同

---

## 1. 指南定位与适用范围

本指南在**不改变**《Supcon Marketing Technology Recommendations》中 Phase 0 → Phase 1 → Phase 2 总体架构的前提下，将 GTM/Martech 常见职责拆解为：

- **谁在什么阶段做哪些事**（需求设计、验证闭环、统一中台）
- **数据与技术在漏斗各阶段的用途**（Attract → Inform → Convert → Engage）
- **与现有文档的对应关系**（指标体系、数据实体、HubSpot 配置、数据平台需求规格）

适用角色：负责 GTM 系统与数据结构设计/演进的同学；与产品、数据、销售、客户成功协作时，可据此对齐范围与优先级。

---

## 2. 职责与阶段映射总览

| GTM 常见职责 | 在本公司的阶段归属 | 对应现有文档位置 |
|-------------|-------------------|------------------|
| 识别「谁该找销售、何时、为何」 | Phase 1 验证 + Phase 2 增强 | 9.4 数据实体、9.3 HubSpot 配置、Phase 2 数据平台 |
| 产品/行为数据 → 线索/商机 | Phase 1：HubSpot 内闭环；Phase 2：统一数据平台 | 9.1 / 9.2 转化路径 |
| 线索/商机识别与打分（**PQL**/MQL/SQL） | Phase 1 规则打分（MQL 为主）；Phase 2 有产品使用数据后可定义 PQL（team expansion / feature adoption / engagement）并可扩展为预测模型 | 9.4 生命周期阶段、9.3 打分与工作流 |
| 自动化账户/客户研究（如 AI 摘要） | Phase 2 或更晚，在数据与权限就绪后 | 本节 5.2 |
| 数据管道（产品/行为 → CRM/MA） | Phase 1：HubSpot 追踪 + 表单；Phase 2：ETL/Reverse ETL | 5.1、9.2 |
| 仪表盘与报表（销售/CS/管理层可见） | Phase 1：HubSpot Dashboard；Phase 2：统一营销数据中台 | 9.5、9.2 |
| 与产品/数据团队协作：埋点、口径、质量 | Phase 0 需求设计 + Phase 1 验证全程 | 9.5 Phase 0、9.4 事件规范 |
| **生命周期营销**：首触→激活→培育→再激活；关键转化节点优化；按 persona/区域差异化 | Phase 1：HubSpot 工作流 + 邮件/落地页；Phase 2：统一看板 + A/B 与多区域 | §4.6、9.3 工作流、9.4 属性 |
| **A/B 测试**：文案、触达时机、流程结构 | Phase 1 起可用 HubSpot A/B；Phase 2 用数据平台做统计与归因 | §4.6、9.5 报表 |
| **多区域/多语言**：时区、文化、本地行为适配 | Phase 1 用 region/语言属性 + 工作流分支；Phase 2 可做 i18n/l10n 与区域报表 | 9.4 region；§4.6 国际适配 |
| **与市场/产品/CX 协作**：品牌一致、功能发布、用户反馈融入体验 | Phase 0 需求对齐；Phase 1/2 活动与功能上线协同 | §4.5、§4.6 协作 |
| **产品营销（PMM）**：定位与叙事、发布 GTM、销售赋能（竞品情报、Demo、ROI）、市场研究与品类领导、与产品/销售/市场跨职能协同 | Phase 0/1 需求与内容；Phase 1/2 发布节奏与赋能物料 | §4.7 产品营销 |

---

## 3. 按漏斗阶段：数据与技术的使用

以下按**营销漏斗四层**（Attract → Inform → Convert → Engage）说明：每层要回答什么问题、需要什么数据、在 Phase 1 / Phase 2 分别用什么技术实现。

### 3.1 Attract（认知 / 流量）

| 要回答的问题 | 需要的数据 | Phase 1 技术实现 | Phase 2 技术实现 |
|-------------|-----------|------------------|------------------|
| 流量从哪来、多少、质量如何？ | UV、来源、媒介、活动、内容 | GA4 + GTM + HubSpot 追踪代码；HubSpot 流量报表 | 统一数据平台：GA4 + 站内事件 ETL 入仓，同一套来源维度 |
| 哪些内容/活动带来高意向？ | 页面/内容 ID、UTM、首次/末次触点 | UTM 标准化 + HubSpot Contact 属性（first/last touch） | 多触点归因模型、内容维度分析 |
| 品牌/声量是否提升？ | SOV、搜索量、活动参与（可选） | 手工或外部数据；可先在 HubSpot 外管理 | 若有数据接口，可接入统一看板 |

**数据用途小结**：Attract 阶段的数据主要用于**来源与内容效果评估**；Phase 1 以 HubSpot + GA4 为主，Phase 2 在统一中台做跨渠道、跨内容、跨时间对比。

### 3.2 Inform（考虑 / 培育）

| 要回答的问题 | 需要的数据 | Phase 1 技术实现 | Phase 2 技术实现 |
|-------------|-----------|------------------|------------------|
| 谁在下载内容、参加活动、留资？ | 表单提交、内容下载、Webinar 报名、邮件互动 | HubSpot Forms + 工作流 + 联系人属性；事件用 GTM 推送（见 9.4.3） | 事件表 + 联系人/公司表关联，统一「内容—线索—行为」模型 |
| 哪些线索算 MQL、该转销售？ | 行为得分 + 属性（行业、产品线、地区） | HubSpot 打分规则 + 生命周期阶段 + 工作流（MQL 创建/分配） | 同一套口径在数据平台复现；可增加预测得分 |
| 培育效果如何？ | 打开率、点击率、内容参与、到 MQL 转化率 | HubSpot 邮件/ landing 报表 + 漏斗报表 | 统一漏斗报表、培育路径分析、**A/B 测试**结果 |
| 沉睡线索如何再激活？ | 长期未打开/未点击、未访问、未转化 | HubSpot 工作流：基于「最后活动时间」触发**再激活**邮件/触达 | 统一行为表 + 再激活流程效果报表 |
| 不同 persona 的培育路径是否差异化？ | 行业、产品线、角色、地区 | HubSpot 列表 + 工作流分支，按 **persona**（industry/product_line/region）推送不同**培育序列** | 数据平台中按 persona 的转化与留存分析 |

**PLG 常用指标在本阶段的对应**：**activation** = 首次关键行为（如首份内容下载、首场 Webinar 报名）；**engagement** = 持续互动（邮件打开/点击、内容参与、重复参会）；**expansion** = 多产品/多席位采用或增购意向（Phase 2 有产品使用数据后可在 Engage 层细化）。在 HubSpot 中通过属性、工作流与报表落地。

**数据用途小结**：Inform 阶段是**线索与 MQL 识别的核心**；Phase 1 用 HubSpot 规则打分与工作流完成「谁该找销售、何时」的初版逻辑；Phase 2 用统一数据与（可选）模型做精细化与预测。

### 3.3 Convert（转化 / 成单）

| 要回答的问题 | 需要的数据 | Phase 1 技术实现 | Phase 2 技术实现 |
|-------------|-----------|------------------|------------------|
| Demo/询价/报价请求是否进入 CRM？ | Demo 表单、商机创建、阶段更新 | HubSpot CRM（Deal/Pipeline）+ 表单与工作流 | 从 CRM 同步到数据平台；统一「Lead → Opportunity → Deal」 |
| 从 MQL 到 SQL 到成单的转化率？ | 阶段变更时间、赢单/输单原因 | HubSpot 管线与阶段；可选自定义属性 | 数据平台中的漏斗与转化周期分析 |
| 哪些产品线/行业/区域转化更好？ | 商机维度（产品线、行业、区域） | HubSpot 商机属性与报表 | 与 9.4 中 product_line/product_category 一致，在平台做多维分析 |

**数据用途小结**：Convert 阶段依赖 **CRM 与 MA 的衔接**；Phase 1 在 HubSpot 内完成；Phase 2 通过数据平台打通 MA + CRM + 行为，支持「为何成单/为何流失」的分析。

### 3.4 Engage（忠诚 / 留存）

| 要回答的问题 | 需要的数据 | Phase 1 技术实现 | Phase 2 技术实现 |
|-------------|-----------|------------------|------------------|
| 客户健康度、续约/扩增风险？ | 使用情况、支持工单、NPS（若有） | 若暂无产品使用数据，可先用 HubSpot 客户属性 + 手动更新 | 产品使用数据 + CRM + CS 数据入仓，健康度模型/看板 |
| 哪些客户适合 upsell/cross-sell？ | 产品使用、模块/功能、合同与续约 | 同上，Phase 1 可仅做基础列表与标签 | 扩展/流失倾向预测、推荐逻辑 |

**数据用途小结**：Engage 阶段在 Phase 1 以**基础客户管理与列表**为主；Phase 2 在**产品数据与 CRM 打通**后，再做健康度与扩展信号。

---

## 4. 核心能力实施要点（对齐 JD 与现有报告）

### 4.1 「谁该找销售、何时、为何」—— 线索与商机识别（含 PQL）

- **PQL 与 MQL 的区分**
  - **PQL（Product Qualified Lead）**：基于**产品使用**的购买信号，如 **team expansion**（团队/席位增长）、**feature adoption**（关键功能采用）、**engagement**（使用深度/频率）。需有产品使用数据后才能在系统中落地。
  - **MQL（Marketing Qualified Lead）**：基于营销行为（内容下载、Webinar、Demo 请求）+ 属性（行业、规模、地区）的线索。Phase 1 以 MQL 为主。
- **Phase 1（规则驱动）**
  - **谁**：用 9.4 的 Contact 属性（company, industry, region, product_line, product_category） + 行为（内容下载、Webinar、Demo 请求）界定 MQL/SQL。
  - **何时**：用 HubSpot lead score 阈值 + lifecycle_stage 变更触发「创建/分配商机」或「通知销售」工作流。
  - **为何**：在 Contact/Deal 上记录 lead_source、lead_source_detail、conversion_event（见 9.4.2、9.4.3），报表中按来源/内容/活动做归因。
- **Phase 2（可扩展 PQL + 预测）**
  - 有**产品使用数据**后：用 team expansion、feature adoption、engagement 等定义 **PQL**，并写入 HubSpot/CRM（经数据平台 + Reverse ETL）。
  - 在统一数据平台复用同一套维度与事件，增加「转化概率」「高价值账户」等预测字段；再通过 Reverse ETL 或 API 写回 HubSpot/CRM，驱动优先级与路由。

### 4.2 产品/行为数据 → HubSpot（数据管道）

- **Phase 1**
  - **网站/落地页**：GTM + HubSpot 追踪代码 + 标准事件（9.4.3）→ HubSpot 自动识别/更新 Contact。
  - **表单与转化**：HubSpot Forms + 工作流，保证 Demo/下载/Webinar 等进入统一 Contact 与 Deal 模型。
  - **与内部 CRM/ERP**：若有线下或既有系统，用 **n8n**（或 Zapier、Make、Tray.io 等）做定时/触发同步与 API 工作流，保持 Contact/Company 主数据一致（见报告 4.1、5.2）。
- **Phase 2**
  - **统一数据平台**：HubSpot、GA4、CRM、**产品使用数据**（usage、feature adoption、team expansion）等 → 经 ETL 入仓（报告 9.2、9.5 Phase 2）。
  - **产品数据入 GTM**：产品使用数据入仓后，经 **Reverse ETL**（**Census、Hightouch** 或自建）写回 HubSpot/Salesforce，使销售与 CS 在 CRM/报表中看到 **real-time engagement、usage trends、expansion signals**。
  - **Reverse ETL** 同时承载「得分、分层、预测结果」从数据平台写回 GTM 系统（报告 9.2 数据流）。

### 4.3 线索打分（规则 → 可选 AI/ML）

- **Phase 1**
  - 使用 HubSpot 内置打分：**行为分**（页面、邮件、表单、活动）+ **属性分**（**firmographics**：行业、公司规模、地区；产品兴趣）。
  - 与 9.4 的 product_line/product_category、lifecycle_stage 一致，便于报表和路由。
- **Phase 2**
  - **AI-powered lead scoring**：在数据平台用 **product behavior**（产品使用/功能采用）、**firmographics**、**engagement patterns** 训练 ML 模型（如 MQL 转化概率、商机赢单概率）；结果写回 CRM/MA，作为「为何找销售」的补充信号。
  - 预测模型需**生产化**（部署、监控、定期重训）；可由数据/算法团队负责，GTM 侧定义指标与用数场景。

### 4.4 仪表盘与报表（销售/CS/管理层可见）

- **Phase 1**
  - **HubSpot Dashboard**：按漏斗层（Attract/Inform/Convert/Engage）建报表——流量与来源、线索与 MQL、管线与转化率、客户数（见 9.5 Phase 1）。
  - 确保核心指标与 9.4、2.2 的指标体系一致，便于 Phase 2 复现。
- **Phase 2**
  - **统一营销数据中台**：同一套指标与维度，覆盖全渠道、全触点、资源流转与归因（见 9.2、9.5 Phase 2）。
  - **面向销售/CS/管理层的可见内容**：**account health**（客户健康度）、**product adoption**（产品采用/使用深度）、**expansion opportunities**（扩展/增购机会）、**churn risk**（流失风险）；在数据与产品打通后由看板与报表呈现。
  - 权限与角色：按销售/CS/管理层划分可见范围（报告 9.5 Phase 2 权限模块）。

### 4.5 与产品/数据团队的协作（埋点、口径、质量）

- **Phase 0**
  - 一起敲定：哪些事件必选（9.4.3）、属性命名与枚举（9.4）、核心指标定义（2.2），输出《营销数据指标体系 v1.0》与《数据中台需求规格说明书》初稿。
- **Phase 1**
  - 验证埋点与口径：从 GTM/HubSpot 到报表的链路是否一致、是否有缺失或重复；将问题与需求写进 Phase 2 需求规格。
- **Phase 2**
  - 数据平台与产品埋点/数据团队对齐：事件 schema、身份解析（contact_id/account_id）、增量与全量同步方式。

### 4.6 生命周期营销与关键转化节点（Lifecycle Marketing）

本小节将 **Senior Lifecycle Marketing Manager** 类职责映射到本公司：**customer.io → HubSpot**，**Weekly Active Creators → MQL/高价值线索**，**first meaningful creation → 首次关键行为**（如首份内容下载、首场 Webinar），**free-to-paid → Lead→MQL→SQL→Customer**。生命周期营销方法论同时适用于 **B2C 与 B2B**（JD 常要求「B2C and B2B chops」）；本公司以 **B2B** 为主，实施时以**联系人/公司/商机**为粒度，persona 与区域差异化逻辑一致。

#### 4.6.1 用户旅程：首触 → 高价值用户

| 常见表述（B2C/PLG） | 在本公司的对应 | 实施方式 |
|---------------------|----------------|----------|
| First touch | 首次访问/首次留资 | GTM + HubSpot 识别；first_touch 属性（9.4） |
| Onboarding completion | 完成「入门」动作（如首封欢迎邮件打开、首份内容下载） | HubSpot 工作流：表单提交 → 欢迎邮件 → 首份内容推荐；用事件判断「完成」 |
| First meaningful creation | 首次关键行为（如首份白皮书下载、首场 Webinar 报名） | 对应 9.4.3 的 content_download、webinar_register；作为 **activation** 指标 |
| Free-to-paid conversion | 从免费/低意向到付费/成单 | Lead → MQL → SQL → Opportunity → Customer；用 lifecycle_stage 与 Deal 阶段衡量 |
| Weekly Active Creator / power user | 高价值用户（B2B：高互动线索或已购客户中的高使用/扩展意向） | 用 engagement 频率、内容参与、产品使用（Phase 2）或 CS 反馈来定义；HubSpot 列表 + 报表 |

#### 4.6.2 生命周期战役与自动化流

- **渠道**：本公司以 **Email + 落地页/内容** 为主；若后续有 **in-app（应用内消息）、push 通知**，可与 Email 一起纳入同一套 Contact 与事件模型，在 Phase 2 统一触达与归因（对应 JD 中「email, in-app, and push notifications」的多渠道生命周期战役）。
- **自动化流（HubSpot 工作流）**：
  - **欢迎/入门序列**：表单提交 → 确认邮件 → 首份内容/首场 Webinar 邀请 → 根据打开/点击进入不同分支。
  - **培育序列**：按 **persona**（industry、product_line、region）设计不同邮件与内容路径；用 9.4 属性做列表与分支。
  - **再激活（re-engagement）**：针对长期未打开、未点击、未访问的线索，触发「再激活」邮件或轻量触达；用「最后活动时间」或「未打开天数」作为触发条件。
  - **与品牌、产品、CX 对齐**：生命周期文案与节奏需与**市场品牌**一致；**功能发布**时与产品协作，将新功能/用例融入邮件或落地页；**用户反馈**（调研、支持工单）可反哺培育内容与再激活话术（与 Customer Experience 协作）。
- **平衡自动化与真实性**：避免过度模板化；在关键节点（如 Demo 请求、高得分）可转为销售人工跟进，自动化负责「培育」与「再激活」。

#### 4.6.3 关键转化节点优化与 time-to-value

- **关键转化点**：**onboarding 完成**（首份内容/首场 Webinar）→ **first meaningful creation**（首次深度参与）→ **MQL**（得分/行为达标）→ **SQL**（销售确认）→ **成单**；B2C/PLG 语境下的 **Weekly Active Creator / 高价值用户状态** 在本公司对应「持续高互动线索或已购客户中的高使用/扩展意向」，可作为 Engage 层优化目标。在 HubSpot 中为每一层建漏斗报表，识别卡点。
- **提升激活与转化、缩短 time-to-value**：通过优化**入门流程**（减少步骤、明确 CTA）、**培育内容**（按 persona 推送）、**再激活**（唤醒沉睡线索）提高各层转化率；用 A/B 测试验证文案、时机、流程（见下）。

#### 4.6.4 A/B 测试与数据驱动

- **Phase 1**：在 **HubSpot** 内做邮件/落地页的 **A/B 测试**（主题、文案、CTA、发送时间）；用 HubSpot 报表看打开率、点击率、转化率，并关注**统计显著性**（样本量与置信度）。**实验严谨性**：设计**规范的 A/B 实验**（明确假设、对照组、样本量、统计检验），理解统计显著性后再下结论，并保持迭代节奏（move fast）。
- **Phase 2**：在数据平台中统一 A/B 实验与用户行为数据，做**多触点归因**与**实验效果分析**；便于「messaging、timing、campaign structure」的持续优化。
- **数据驱动**：**Data-driven mindset**——熟练使用分析工具、搭建看板、让**数据指导策略与决策**（Phase 1 HubSpot Dashboard，Phase 2 统一中台）；**SQL 或数据分析能力**（Nice to have）有助于自助取数与实验分析。

#### 4.6.5 多区域/国际适配（international, multi-market）

- **Phase 1**：用 9.4 的 **region**、语言或国家属性做**列表与工作流分支**；不同区域使用不同邮件模板、发送窗口（**时区**）、以及可选的不同首推内容（**本地行为/需求**）。
- **Phase 2**：若有**国际化/本地化（i18n/l10n）**需求，可在内容与邮件中接入多语言与区域化配置；报表按 region 拆解转化与留存，便于「adapt campaigns for international markets with diverse user needs」。**Nice to have**：有**国际化/本地化项目（internationalization and localization programs）**经验可加速多区域落地。
- **文化与时区**：邮件发送时间、节日与话术需考虑**文化差异**和**时区**；可在 Contact 上维护 preferred_language / region，供工作流与报表使用。

#### 4.6.6 与市场、产品、客户体验的协作

- **Marketing**：生命周期战役的**品牌语调、视觉、话术**与市场整体一致；大促或品牌活动与生命周期节奏协同。
- **Product**：**功能发布**时，将新功能/用例融入生命周期邮件或落地页；产品侧提供**功能说明与卖点**，便于编写培育与再激活内容。
- **Customer Experience (CX)**：将**用户反馈**（NPS、支持工单、访谈）纳入培育与再激活内容；对流失或沉睡客户，可与 CX 一起设计「挽回」或「再教育」路径。

#### 4.6.7 文案与写作（on-brand, compelling copy）

- 生命周期邮件与落地页需**简洁、有说服力、有行动导向（compelling, on-brand copy that drives action）、符合品牌**；若团队有专职文案，可由其负责核心模板，GTM/Martech 侧负责**流程、分支与数据**；若无，可在 Phase 0 约定**文案原则与审批流程**，便于自动化与真实性平衡。

### 4.7 产品营销（Product Marketing）——定位、叙事与发布 GTM

本小节将 **Senior Product Marketing Manager** 类职责映射到本公司：**AI 产品组合** → 本公司**工业软件/自动化/数字化产品组合**；**technical fluency in AI/LLM** → **对产品能力与技术差异的深度理解**；**thought leader in AI** → **在工业数字化/自动化领域的 thought leadership**。PMM 与 GTM Engineer、Lifecycle Marketing 协同：**定位与叙事** 支撑 Attract/Inform 的内容与落地页；**销售赋能** 支撑 Convert；**用户洞察与竞品情报** 反哺产品路线图与 4.5/4.6 的协作。

#### 4.7.1 定位与叙事（positioning and messaging）

- **职责**：负责产品组合的 **positioning and messaging**，将**复杂能力**转化为**清晰、差异化的价值主张**；面向**技术与非技术受众**都能产生共鸣，建立**思想领导力**（thought leadership）。
- **本公司对应**：工业软件/自动化/数字化产品的**价值主张**、**与竞品的差异化话术**、**技术能力 → 业务价值**的翻译；白皮书、案例、Webinar、落地页与销售话术保持一致叙事。
- **与数据/漏斗的衔接**：定位与核心信息写入 9.4 的 content 维度与 UTM/归因；培育与生命周期内容（§4.6）采用同一套 messaging，便于报表按「主题/价值主张」分析效果。

#### 4.7.2 发布 GTM 与跨职能协同

- **Lead go-to-market strategy and execution for major product launches**：从 **kickoff 到 post-launch optimization**，协调**产品、销售、市场**等跨职能；时间表、里程碑、内容与触达节奏与 Phase 1/2 的 HubSpot 活动、工作流、报表对齐。
- **Partner with product, design, engineering（及 AI/技术团队）**：将**客户洞察与市场情报**注入路线图；确保 PMM 能**快速建立技术理解**（develop technical fluency quickly）、**深入复杂产品能力**（go deep on complex product capabilities），与产品/工程有效协作。本公司可对应与**产品、研发、解决方案**的定期对齐，把竞品动态、客户反馈、分析师观点纳入需求与发布节奏。

#### 4.7.3 销售赋能（technical sales enablement）

- **Build technical sales enablement materials**：
  - **Competitive intelligence**：竞品定位、功能对比、赢单/输单话术；可维护在知识库或 CRM 侧，供销售与 CS 使用。
  - **Demos showcasing technical capabilities**：产品演示脚本、差异化亮点、技术能力如何对应客户场景。
  - **ROI frameworks**：投资回报/价值量化框架，支撑销售与客户沟通。
- **Serve as product evangelist**：代表公司在**客户对话、分析师沟通、行业活动**中传递产品愿景与差异化；与市场活动（Attract/Inform）和销售周期（Convert）一致。

#### 4.7.4 内容与叙事线（technical → business value）

- **Craft compelling narratives**：从**技术博客、发布公告**到**高管/决策层定位**（executive positioning），解释**产品战略与愿景**；**技术深度与业务价值**兼顾（storytelling that bridges technical depth and business value）。
- **Develop and execute integrated marketing programs**：教育用户/客户理解产品能力，推动 **self-serve（如官网、内容、试用）与 sales-led（Demo、商机）** 双轨采用；与 §3 漏斗（Attract → Inform → Convert → Engage）和 §4.6 生命周期触达一致。

#### 4.7.5 市场研究与品类领导

- **Conduct market research**：理解**技术/行业如何改变客户工作流**（如 AI 改造创意工作流 → 本公司可为工业数字化/自动化如何改变生产与运营）；**跟踪竞品动态**（competitive developments）；**识别品类领导机会**（category leadership opportunities）。
- **Analytical mindset**：定义**产品/功能采用类指标**（如 AI feature adoption → 本公司可为关键模块/场景采用率）；**运行实验、用数据优化定位与话术**；与 §4.4 仪表盘、§4.6.4 A/B 与数据驱动衔接。
- **Entrepreneurial spirit**：适应**快速演进的技术与市场**（如 AI  landscape）；本公司可对应工业软件、自动化、数字化赛道的政策与需求变化，持续更新定位与竞争叙事。

#### 4.7.6 能力与协作要点（What you'll bring 映射）

- **6+ years PMM in B2B SaaS/technology**，**AI/ML 产品面向 prosumer + business**：本公司对应 B2B 工业客户与多角色（技术决策者、业务决策者）；若有 AI/智能相关产品线，可强调「技术能力 → 业务价值」的翻译。
- **Strong technical foundation**；**explain how LLMs/agents work**；**translate technical features into business value**：本公司可对应「解释核心算法/平台能力如何工作」、将**技术特性转化为客户场景与 ROI**。
- **Cross-functional leadership**：赢得**技术团队信任**，同时影响**销售、市场、高管**；与 §4.5、§4.6.6 的协作模型一致，PMM 作为「产品—市场—销售」的桥梁。
- **Exceptional storytelling**：技术深度与业务价值兼顾；与 4.6.7 文案原则一致，统一用于落地页、销售物料与活动。

---

## 5. 可选增强（Phase 2 及以后）

### 5.1 AI 驱动的账户/客户研究（如 LLM 摘要）

- **典型用途**：根据公司官网、新闻、融资、技术栈等，自动生成「为何适合联系、可谈什么」的要点，供销售/CS 使用。
- **前置条件**：数据与权限就绪（公司/联系人主数据、合规使用外部信息）；API 与工作流可调用 LLM。
- **实施建议**：
  - 先明确使用场景（例如：仅对「高价值/高意向」账户生成）、数据来源与合规，再选型（自建 agent vs 采购工具）。
  - 可与 4.1「为何找销售」结合：在 CRM/MA 中展示「推荐联系原因」或「谈话要点」字段。

### 5.2 数据仓库与 dbt（若采用）

- 若 Phase 2 采用数仓（如 **Snowflake、BigQuery、Redshift**），建议：
  - 用 **dbt**（或同类工具）做指标与维度建模，保证与 9.4、2.2 的定义一致。
  - 输出层可直接支撑 Reverse ETL（Census/Hightouch）与 BI/Dashboard，避免重复逻辑。
- **技术能力**：ETL/Reverse ETL 与数据平台建设通常需要 **Python、SQL** 及 API 集成能力；与「What you'll bring」中的技能要求一致。

### 5.3 从 PLG 向 Enterprise 延伸（若适用）

- 若业务从 PLG（产品驱动增长）向 enterprise（大客户/销售驱动）延伸，本指南的 **Phase 2 数据平台、PQL 设计、Reverse ETL** 可支撑该过渡：产品使用信号（team expansion、feature adoption）入仓并写回 CRM，使销售/CS 可见「哪些账户该联系、为何、谈什么」。
- 行业常见参考：Figma、Notion、Slack、Miro、Airtable 等早期数据系统均强调「产品使用数据 → GTM 可见」的管道与看板。

---

## 6. 与现有报告的一一对应

| 本指南章节 | 对应《Supcon Marketing Technology Recommendations》 |
|-----------|------------------------------------------------------|
| 2 职责与阶段映射 | 5.1 目标状态、5.2 阶段演进；9.5 Phase 0/1/2 |
| 3 按漏斗的数据与技术 | 9.0 漏斗模型、9.1/9.2 转化路径、2.2 指标体系 |
| 4.1 谁/何时/为何 | 9.4 数据实体与生命周期、9.3 HubSpot 配置 |
| 4.2 数据管道 | 9.1（HubSpot 闭环）、9.2（统一平台）、4.1 n8n、5.2 P1→P2 |
| 4.3 打分 | 9.3 打分与工作流、9.4 lead_score / lifecycle_stage |
| 4.4 仪表盘 | 9.5 Phase 1 HubSpot Dashboard、9.2 Phase 2 看板 |
| 4.5 产品/数据协作 | 9.5 Phase 0 需求设计、9.4 事件规范 |
| 4.6 生命周期营销 | 9.3 工作流、9.4 属性、§4.6 各小节 |
| 4.7 产品营销 | 定位与叙事、发布 GTM、销售赋能、市场研究；与 9.1/9.2、活动/内容一致 |
| 5 可选增强 | Phase 2 及后续扩展，不改变现有 Phase 1/2 范围与优先级 |

---

## 7. 小结

- 本指南把 GTM Martech 的常见职责（识别高意向账户、数据管道、打分、仪表盘、与产品/数据协作）、**生命周期营销**（培育、再激活、多区域、A/B）与**产品营销**（定位与叙事、发布 GTM、销售赋能、竞品与品类领导）**落到 Supcon 已有的 Phase 0/1/2 和漏斗/数据模型上**，避免重复造轮子。
- **Phase 1**：优先**开箱即用**（HubSpot + GTM + 标准数据实体）完成「谁该找销售、何时、为何」的验证闭环，并输出可复用的指标体系与数据平台需求规格。
- **Phase 2**：按需**自建**（统一数据平台、Reverse ETL、ML 模型、AI 账户研究），在统一数据平台上实现全链路数据、可选预测打分与 Census/Hightouch 等 Reverse ETL，随反馈迭代；技术选型平衡 custom vs off-the-shelf。
- 具体技术选型与排期仍以《Supcon Marketing Technology Recommendations》9.5 及与相关技术团队的共同确认为准。

---

---

## 附录：JD 条款逐条对照

以下为 GTM Engineer JD 中「What you'll do」与「What you'll bring」的逐条映射，确保无遗漏。

### What you'll do（职责）

| JD 原文 | 本指南对应位置 | 说明 |
|--------|----------------|------|
| Build **PQL identification systems** that surface enterprise buying signals based on **team expansion, engagement, feature adoption, and company attributes** | §2 职责映射「PQL/MQL/SQL」；§4.1 谁/何时/为何；§4.3 打分；§3.2 Inform、§3.4 Engage | PQL = 基于**产品使用**的线索（团队扩展、功能采用、使用深度）。Phase 1 以 MQL（营销行为+属性）为主；Phase 2 有产品使用数据后，用 team expansion / feature adoption / engagement 等信号定义 PQL 并写入 HubSpot。 |
| Build **AI agents for automated account research** using **LLM APIs** to analyze **company websites, news, funding events, and tech stacks**, generating **personalized talking points** | §5.1 AI 驱动的账户/客户研究 | 明确对应：官网/新闻/融资/技术栈 → LLM 生成谈话要点；Phase 2 及以后，数据与合规就绪后实施。 |
| Design and implement **data pipelines from product usage data to HubSpot**, enabling **sales and CS** to see **real-time engagement, usage trends, and expansion signals** | §4.2 数据管道；§3.4 Engage；§4.4 仪表盘 | Phase 1：网站/表单数据入 HubSpot。Phase 2：产品使用数据 ETL 入仓 → 再经 Reverse ETL 或 API 写入 HubSpot/CRM，使销售/CS 在报表中看到使用趋势与扩展信号。 |
| Create **AI-powered lead scoring models** using **ML algorithms** combined with **product behavior, firmographics, and engagement patterns** to **predict conversion** | §4.3 线索打分；§4.1 Phase 2 预测 | Phase 1 规则打分（行为+属性）；Phase 2 用 product behavior（产品使用）+ firmographics（行业/规模/地区）+ engagement（邮件/内容/活动）训练 ML 模型预测转化，结果写回 CRM。 |
| Build **dashboards and reporting** for **sales, CS, and leadership** visibility into **account health, product adoption, expansion opportunities, and churn risk** | §4.4 仪表盘；§3.4 Engage | Phase 1：HubSpot 按漏斗层建报表。Phase 2：统一中台提供 account health、product adoption、expansion opportunities、churn risk 等视图，并按角色（销售/CS/管理层）做权限划分。 |
| Implement **reverse ETL** using **Census, Hightouch**, or custom solutions so **product data flows seamlessly into GTM systems** | §4.2 Phase 2 Reverse ETL | 明确工具：Census、Hightouch 或自建；将数据平台中的产品数据与预测结果写回 HubSpot/Salesforce 等 GTM 系统。 |

### What you'll bring（技能与背景）

| JD 原文 | 本指南对应位置 | 说明 |
|--------|----------------|------|
| 3–5 years in **GTM Engineer / Growth / RevOps / Analytics Engineering** at **PLG B2B SaaS** | §1 适用范围 | 本指南面向负责 GTM 系统与数据结构设计/演进的角色；Supcon 为 B2B 硬件+软件，PQL 在具备产品使用数据后（Phase 2）适用。 |
| **Python and SQL**；data pipelines；**ETL/reverse ETL**；integrating **product data with GTM systems** | §4.2 数据管道；§5.2 数仓与 dbt | Phase 2 的 ETL/Reverse ETL、数据平台与模型通常需 Python/SQL；dbt 用于指标与维度建模。 |
| **API integration**；**workflow automation**（**n8n, Zapier, Make, Tray.io**）for API-driven workflows | §4.2 与内部 CRM/ERP 的 n8n；§4.1 报告 4.1 | 数据与流程集成：n8n 已在报告中推荐；同类型可选 Zapier、Make、Tray.io 等，用于 MA↔CRM/ERP 同步与自动化。 |
| Deep understanding of **PLG metrics and CRM**（**HubSpot or Salesforce**）；operationalize **activation, engagement, expansion** signals | §3 按漏斗阶段；§2.2 指标体系；§9.4 生命周期 | activation = 首次关键行为（如首份内容下载/首场 Webinar）；engagement = 持续互动（邮件、内容、活动）；expansion = 增购/扩展/多产品采用。在 HubSpot 中通过属性、工作流与报表落地。 |
| Proven impact building **PQL models, AI agents, predictive analytics** that drove pipeline/revenue | §4.1、§4.3、§5.1 | 本指南将上述能力对应到 Phase 1（规则 PQL/MQL）与 Phase 2（预测模型、AI 研究、Reverse ETL）。 |
| **Scrappy builder**；balance **custom vs off-the-shelf**，iterate on feedback | §7 小结 | Phase 1 优先用开箱即用（HubSpot）；Phase 2 按需自建数据平台、Reverse ETL 或 ML 模型，并随反馈迭代。 |
| (Nice to have) **Data warehouse**（**Snowflake, BigQuery, Redshift**）and **dbt** | §5.2 数据仓库与 dbt | Phase 2 若采用数仓，用 dbt 做指标与维度建模，与 9.4/2.2 定义一致。 |
| (Nice to have) Early data systems for **PLG to enterprise** transition（e.g. Figma, Notion, Slack） | §5 可选增强；§4.1 PQL | 从 PLG 向 enterprise 延伸时，本指南 Phase 2 的数据平台、PQL 设计与 Reverse ETL 可支撑「产品信号 → 销售/CS 可见」的过渡。 |
| (Nice to have) **Production ML**：building, deploying, **monitoring** predictive models | §4.3 Phase 2 | 预测模型需生产化（部署、监控、回写 CRM）；可由数据/算法团队负责，GTM 侧定义指标与用数场景。 |

---

### Senior Lifecycle Marketing Manager JD 对照（email/in-app/push、customer.io、多区域）

以下为 **Lifecycle Marketing Manager** 类 JD（如「About the role / What you'll do / What you'll bring」）的逐条映射，确保生命周期营销与实验、文案、多区域等无遗漏。

#### About the role / What you'll do

| JD 表述 | 本指南对应 | 说明 |
|--------|------------|------|
| Own **user journey from first touch to power user**；design/optimize **email, in-product messaging, cross-channel** experiences | §4.6.1 用户旅程表；§4.6.2 渠道（Email + in-app、push） | 首触→高价值用户；本公司以 Email + 落地页为主，in-app/push 在 Phase 2 可接入同一 Contact 与事件。 |
| Build **sophisticated automation flows in customer.io** | §4.6.2 自动化流（HubSpot 工作流） | customer.io → HubSpot 工作流：欢迎/培育/再激活序列，按 persona 分支。 |
| **Rigorous A/B tests** on messaging, timing, campaign structure；analyze performance and user behavior data | §4.6.4 A/B 测试与数据驱动 | Phase 1 HubSpot A/B；Phase 2 数据平台做实验与归因；强调实验严谨性与统计显著性。 |
| Optimize **onboarding completion, first meaningful creation, free-to-paid, Weekly Active Creator status** | §4.6.1 表、§4.6.3 关键转化点 | 对应首份内容/Webinar、MQL→SQL→成单、高价值用户状态。 |
| **Re-engagement campaigns for dormant users**；**nurture sequences tailored to different personas** | §4.6.2 再激活、培育序列；§3.2 Inform | 用「最后活动时间」等触发再激活；按 industry/product_line/region 做培育分支。 |
| **Adapt campaigns for international markets**（cultural nuances, time zones, local behaviors） | §4.6.5 多区域/国际适配 | region/语言属性、发送窗口、i18n/l10n（Phase 2）。 |
| **Partner with Marketing, Product, CX**：brand voice, feature launches, user feedback, full experience | §4.6.6 与市场、产品、客户体验的协作 | 品牌一致、功能发布融入触达、用户反馈反哺培育与再激活。 |

#### What you'll bring

| JD 表述 | 本指南对应 | 说明 |
|--------|------------|------|
| **5–8 years** marketing，**3+ years** building **email campaigns, automation flows, multi-channel lifecycle** | §4.6 全节 | 本指南将上述能力落在 HubSpot 工作流、漏斗与 Phase 1/2。 |
| **customer.io expertise**：complex lifecycle campaigns，deep platform knowledge | §4.6.2、9.3 HubSpot 配置 | 映射为 HubSpot 工作流与 MA 的深度使用、复杂分支与数据模型。 |
| **B2C and B2B chops** | §4.6 开篇 | 生命周期方法论通用；本公司 B2B，以联系人/公司/商机为粒度。 |
| **Global experience**：international, multi-market user bases | §4.6.5 | region、时区、文化、i18n/l10n。 |
| **Data-driven mindset**：analytics tools, dashboards, data guide decisions | §4.6.4、§4.4 仪表盘 | Phase 1 HubSpot Dashboard；Phase 2 统一中台；数据指导策略。 |
| **Experimental rigor**：proper A/B tests, statistical significance, move fast | §4.6.4 | 规范实验设计、统计显著性、迭代节奏。 |
| **Excellent writing**：compelling, on-brand copy that **drives action** | §4.6.7 | 有说服力、符合品牌、驱动行动。 |
| (Nice to have) **Internationalization and localization programs** | §4.6.5 | i18n/l10n 项目经验。 |
| (Nice to have) **PLG strategies and metrics** | §3.2、§4.6.1、§5.3 | activation / engagement / expansion；PLG 向 enterprise 延伸。 |
| (Nice to have) **SQL or data analysis skills** | §4.6.4、§5.2 | 自助取数、实验分析、数仓/dbt。 |
| (Nice to have) **Already a [product] user** | — | 产品深度理解；本公司可对应「已熟悉行业/产品线」等。 |

---

### Senior Product Marketing Manager JD 对照（positioning、launch GTM、sales enablement、thought leadership）

以下为 **Product Marketing Manager** 类 JD（如「About the role / What you'll do / What you'll bring」）的逐条映射，确保定位、叙事、发布、销售赋能与市场研究无遗漏。

#### About the role / What you'll do

| JD 表述 | 本指南对应 | 说明 |
|--------|------------|------|
| Own **positioning and messaging** for **AI-powered product portfolio**；**translate complex capabilities into clear, differentiated value propositions** | §4.7.1 定位与叙事 | 本公司对应工业软件/自动化/数字化产品组合；复杂能力 → 清晰价值主张。 |
| **Deep technical fluency** in how AI works（models, how we apply them）；**authentic messaging** for **technical and non-technical audiences**；**thought leader in AI innovation** | §4.7.1、§4.7.4、§4.7.6 | 本公司对应产品能力与技术差异的深度理解；技术与非技术受众兼顾；工业数字化/自动化领域 thought leadership。 |
| **Bridge product, sales, and marketing**；drive **successful launches and feature adoption** | §4.7.2 发布 GTM 与跨职能协同 | 从 kickoff 到 post-launch，协调产品/销售/市场；与 Phase 1/2 活动与工作流对齐。 |
| **Partner with product, engineering, AI**；**customer insights into roadmap**；**technical sales enablement**；**AI product evangelist**（customers, analysts, events） | §4.7.2、§4.7.3 | 客户洞察与市场情报 → 路线图；竞品情报、Demo、ROI 框架；对外代表产品愿景与差异化。 |
| **Lead go-to-market strategy and execution** for major launches；**cross-functional teams from kickoff through post-launch optimization** | §4.7.2 | 发布 GTM 全流程；时间表、里程碑、内容与触达与 HubSpot/报表衔接。 |
| **Technical sales enablement**：**competitive intelligence, demos, ROI frameworks** | §4.7.3 销售赋能 | 竞品对比、演示脚本与差异化、价值量化框架。 |
| **Craft compelling narratives**：technical blog posts, launch announcements, **executive positioning**；explain **AI strategy and vision** | §4.7.4 内容与叙事线 | 技术深度与业务价值兼顾；从博客/发布到高管层叙事一致。 |
| **Integrated marketing programs** that **educate on [product] capabilities**；**self-serve and sales-led motions** | §4.7.4、§3 漏斗、§4.6 | 与 Attract/Inform/Convert 及生命周期触达一致。 |
| **Market research**：how [tech] is transforming [workflows]；**competitive developments**；**category leadership opportunities** | §4.7.5 市场研究与品类领导 | 行业/技术改变客户工作流；竞品跟踪；品类领导机会。 |
| **Partner with product, design, engineering, AI**；**customer insights and market intelligence inform roadmap** | §4.7.2、§4.5 | 与 4.5 产品/数据协作、4.6.6 市场/产品/CX 协作一致。 |

#### What you'll bring

| JD 表述 | 本指南对应 | 说明 |
|--------|------------|------|
| **6+ years PMM** in **B2B SaaS or technology**；**AI/ML products to prosumer and business audiences** | §4.7 开篇、§4.7.6 | 本公司 B2B 工业客户；多角色（技术/业务决策者）。 |
| **Strong technical foundation**；understand **AI/ML concepts**；explain **how LLMs and agents work**；**translate technical features into business value** | §4.7.1、§4.7.4、§4.7.6 | 产品能力与技术差异的深度理解；技术特性 → 客户场景与 ROI。 |
| **Develop technical fluency quickly**；**go deep on complex product capabilities**；**partner effectively with product and engineering** | §4.7.2、§4.7.6 | 快速建立技术理解、深入复杂能力、与产品/研发协同。 |
| **Exceptional storytelling**：**bridge technical depth and business value** | §4.7.4、§4.6.7 | 叙事线统一；技术深度与业务价值兼顾。 |
| **Cross-functional leadership**；**credibility with technical teams**；**influence sales, marketing, executive stakeholders** | §4.7.2、§4.7.6 | 产品—市场—销售桥梁；与 4.5、4.6.6 协作模型一致。 |
| **Analytical mindset**：**metrics for [product] adoption**，**experiments**，**data to optimize positioning** | §4.7.5、§4.4、§4.6.4 | 产品/功能采用指标、实验、数据优化定位；与仪表盘与 A/B 衔接。 |
| **Entrepreneurial spirit**；**navigate rapidly evolving [tech] landscape** | §4.7.5 | 适应技术与市场快速变化；本公司可对应工业数字化/自动化赛道变化。 |

---

**文档版本**：v1.0  
**关联文档**：`Supcon_Marketing_Technology_Recommendations.md`、`Martech_自动化运营机制与技术栈分析.md`
