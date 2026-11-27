# HubSpot 团队 Align 需求文档（Marketing Hub + Content Hub）

## 目标与范围
本文件用于团队对齐 HubSpot 实施范围与功能需求，当前已确定 HubSpot 为数据集成平台。重点覆盖 Marketing Hub 与 Content Hub 的配置能力，并确保 6 个核心席位（Core Seats）能够满足关键业务场景。

## 基本假设
- 账号规划：6 Core Seats。
- 平台范围：Marketing Hub + Content Hub（含 HubSpot Breeze AI 能力）。
- 数据集成：HubSpot 为核心 data integration 入口。

## 功能需求（必须原生支持）

### 1. 高级邮件自动化与工作流（Advanced Email Automation & Workflows）
用于事件与活动的自动化运营，要求：
- 行为触发（Behavior-Based Triggers）：基于特定网站行为、表单提交或活动报名触发自动邮件。
- 滴灌与培育（Drip / Nurture Sequences）：多步骤邮件旅程，推动 Lead → MQL → SQL，无需人工干预。
- 个性化与 Token（Personalization & Tokens）：使用客户数据动态个性化内容以提高参与度（例如行业、职位等）。
- 自动内部通知（Automated Internal Notifications）：当 Lead 达到特定 SQL 阈值时即时通知团队。

### 2. 社媒管理与追踪（Social Media Management & Tracking）
集中化管理社媒运营：
- 多渠道发布与监控（Multi-channel Publishing & Monitoring）：统一管理 LinkedIn 与 YouTube 账号的发布与监控。
- 社媒归因（Social Attribution）：追踪社媒互动与点击对线索生成及成交收入的贡献。

### 3. 全漏斗追踪与 ROI（Full-Funnel Tracking & ROI）
要求以真实 ROI 为目标的报表能力：
- 漏斗速度（Funnel Velocity）：报告 Lead → MQL → SQL 的推进时间。
- 闭环归因（Closed-Loop Reporting）：将特定活动预算与数字营销投入与收入关联。
- 网站分析（Website Analytics）：网站表现数据直接进入 ROI 报表。
- 二次计算指标（Derived Metrics）：数据看板支持基于原始指标进行二次计算（如转化率、LTV/CAC、漏斗速度等）。

### 4. HubSpot Breeze + Content Hub 能力
使用 Breeze AI 与 Content Hub 支持内容与线索智能化：
- Breeze 内容 Remix：基于现有内容进行改写、扩展与多渠道输出。
- Breeze 线索智能（Lead Intelligence）：辅助评分与识别高意向线索。
- 费用确认：确认 Breeze AI 是否有额外费用或附加包。

### 5. 内容与网站体验（Content Hub / CMS）
确保内容产出、网站承载与表单转化闭环：
- 内容管理：页面/博客/落地页管理与版本控制。
- 表单与转化：表单字段、渐进式收集、隐藏字段自动写入来源信息。
- A/B 测试：页面或邮件的对照实验与统计。
- SEO 与内容优化：SEO 关键词、元数据、可读性与结构化内容建议。
- 多语言与地区化：支持多地区页面内容管理与发布流程。

### 6. 线索与客户生命周期管理（Lifecycle & CRM Alignment）
确保销售协同与生命周期可执行：
- 生命周期阶段：Lead / MQL / SQL / Opportunity / Customer 的标准口径与变更规则。
- 线索评分：行为 + 画像评分并可回写至名单/工作流。
- 细分与名单：动态/静态名单、过滤器与细分规则。
- SLA 与跟进：MQL → SQL 的跟进时限与超时提醒。

### 7. 广告与投放数据整合（Paid Media / Ads）
要求投放数据可关联转化与收入：
- 广告平台连接：连接主流广告平台并同步花费与转化。
- 投放归因：投放与渠道级别的归因与 ROI 统计。
- 受众同步：从 HubSpot 细分名单同步到广告受众。

### 8. 事件与活动支持（Events / Campaigns）
支持线上线下活动数据回流：
- 活动注册与签到：与活动平台或表单对接，记录注册/签到状态。
- 活动效果归因：活动对 MQL/SQL 与成交的影响回传。
- 线下名片导入：支持批量导入与字段映射。

### 9. 合规与数据治理（Compliance & Governance）
确保数据合规与质量控制：
- 同意管理：隐私合规、订阅偏好、退订与审计追踪。
- 数据质量：重复记录检测、字段校验、必填规则。
- 权限控制：角色权限、字段级可见性与审批流程。

## 实施支持需求（HubSpot / Oxygen）
需要 HubSpot 或 Oxygen 提供以下实施支持，确保配置逻辑稳定且可扩展：
- 工作流架构（Workflow Architecture）：设计自动培育逻辑，确保序列不重叠、不冲突。
- 线索评分与漏斗定义（Lead Scoring & Funnel Definition）：明确 MQL / SQL 的触发条件与阈值。
- 归因模型（Attribution Modeling）：确保 ROI Dashboard 能正确区分 Email / Social / Organic 等渠道贡献。

## 数据集成与来源追踪（Data Integration & Source Tracking）
确保 HubSpot 作为核心集成平台，覆盖历史数据与未来数据来源：
- 区域客户数据集成：从 Angela 收集并整合各个 region 的 customer data。
- 历史网站数据集成：从 Jessie 集成历史网站的 visitor / customer data。
- 新增数据源扩展：支持未来 campaign / event 的 business card 等线下数据来源。
- Webflow 表单集成：与 Webflow 网站表单打通，用于收集用户信息并回传 HubSpot。
- 来源标记（Source Tagging）：支持标记与区分用户来源（Organic / Ads / Referral 等）。
- 链接追踪（Bitly-like Tracking）：支持使用不同链接追踪 traffic source（短链或 UTM 方案）。
- Bitly 集成：支持与 Bitly 集成，用于短链生成与点击追踪。

## 数据字典与字段对齐（Data Dictionary & Field Alignment）
确保跨来源数据可被统一治理与追踪：
- 字段映射：明确各来源字段 → HubSpot 字段的映射关系（含必填字段）。
- 标准化规则：命名、枚举值、日期格式、地区/国家等统一规范。
- 去重与主键：定义联系人/公司唯一标识与去重逻辑。
- 事件与活动字段：统一活动、campaign、event、线下名片等字段口径。
- 归因字段：UTM / referrer / source / medium 的口径与写入规则。

## 调研对齐要点（基于现有项目调研补充）
为保持与既有调研一致，需求需满足以下方向：
- 统一事件模型：网站行为、表单、活动、广告点击需统一事件口径。
- 跨渠道归因：Email / Social / Ads / Organic 需可比较与可归因。
- 可扩展集成：后续新站点/新活动可低成本接入。
- 数据可追溯：关键指标可追溯到来源与原始事件。

## 漏斗阶段与指标框架（Funnel Stages & Metrics Framework）
当前漏斗阶段定义：Awareness → Consideration → Lead Generation。

### 渠道指标清单（合并版）
说明：若指标由外部平台产出，需同步进 HubSpot 或数据仓，并与来源字段对齐。

| 渠道 | 指标 | 漏斗阶段 | 指标定义 / 追踪目标 | 重要性 | 建议频率 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| LinkedIn（Organic） | Impressions（曝光量） | Awareness | 帖子展示次数 | 内容曝光 | 周/月 | - |
| LinkedIn（Organic） | Engagement Rate（互动率） | Consideration | 互动率（点赞/评论/分享） | 内容质量 | 周/月 | - |
| LinkedIn（Organic） | Clicks（贴文→链接） | Consideration | 贴文到链接点击 | 引流能力 | 周/月 | - |
| LinkedIn（Organic） | Followers / Followers Growth（粉丝量/增长） | Consideration | 粉丝及增长 | 品牌增长 | 月 | - |
| LinkedIn（Organic） | Shares（分享量） | Awareness/Consideration | 分享次数 | 内容扩散 | 周/月 | - |
| LinkedIn（Paid） | Impressions（曝光量） | Awareness | 展示次数 | 投放覆盖 | 周/月 | - |
| LinkedIn（Paid） | CTR（点击率） | Consideration | 点击率 | 素材吸引力 | 周/月 | - |
| LinkedIn（Paid） | CPL（单条线索成本） | Lead gen | 单条线索成本 | 获客效率 | 周/月 | - |
| LinkedIn（Paid） | Leads（线索数） | Lead gen | 广告线索数 | 线索产出 | 周/月 | - |
| LinkedIn（Paid） | Ads spend（广告消耗） | N/A | 总花费 | 成本核算 | 周/月 | - |
| YouTube | Impressions（曝光量） | Awareness | 展示次数 | 触达规模 | 月 | - |
| YouTube | Video views（观看次数） | Awareness/Consideration | 观看次数 | 内容吸引 | 月 | - |
| YouTube | Avg. video duration / Watch time（观看时长） | Consideration | 平均观看时长 | 内容深度 | 月 | - |
| YouTube | Subscribers（粉丝量） | Consideration | 订阅数 | 品牌沉淀 | 月 | - |
| YouTube | Traffic to Website / CTA clicks（引流/CTA 点击） | Consideration | 引流至官网 | 转化前置 | 月 | - |
| EDM | Deliverability rate（送达率） | Awareness | 送达率 | 基础可达 | 周/月 | - |
| EDM | Open rate（打开率） | Awareness/Consideration | 打开率 | 内容吸引 | 周/月 | - |
| EDM | CTR（点击率） | Consideration | 点击率 | 引流能力 | 周/月 | - |
| EDM | Subscribers（订阅数） | Consideration | 订阅数 | 私域积累 | 月 | - |
| EDM | Conversion rate（邮件转化率） | Lead gen | 邮件到目标转化 | 线索产出 | 周/月 | - |
| Google Ads | Total impressions（曝光量） | Awareness | 展示次数 | 覆盖 | 周/月 | - |
| Google Ads | Total clicks（点击量） | Consideration | 点击量 | 引流 | 周/月 | - |
| Google Ads | CTR（点击率） | Consideration | 点击率 | 素材质量 | 周/月 | - |
| Google Ads | CPA（获客成本） | Lead gen | 获客成本 | 效率 | 周/月 | - |
| Google Ads | Leads（线索数） | Lead gen | 线索数 | 产出 | 周/月 | - |
| Google Ads | Conversion rate（转化率） | Lead gen | 转化率 | 效果 | 周/月 | - |
| Google Ads | Ads spend（广告消耗） | N/A | 总花费 | 成本核算 | 周/月 | - |
| Website（GA4） | Users（用户数） | Awareness | 独立访客量 | 流量基础 | 周/月 | - |
| Website（GA4） | Sessions（会话数） | Awareness/Consideration | 会话数 | 流量 | 周/月 | - |
| Website（GA4） | Engagement Rate（参与率） | Consideration | 参与率 | 内容留存能力 | 周/月 | - |
| Website（GA4） | Pageviews（页面浏览） | Consideration | 页面浏览 | 内容消费 | 周/月 | - |
| Website（GA4） | Avg. session duration（平均停留） | Consideration | 平均停留 | 内容质量 | 周/月 | - |
| Website（GA4） | Bounce rate（跳出率） | Consideration | 跳出率 | 页面匹配度 | 周/月 | - |
| Website（GA4） | Conversion / Key Events（转化/关键事件） | Lead gen | 表单提交、咨询点击等 | 线索产出 | 周/月 | - |
| Website（GA4） | By-source metrics（来源拆分） | N/A | 来源拆分 | 渠道归因 | 周/月 | - |
| Events | Registration（Google Form） | Lead gen | 活动报名量 | 活动引流 | 视活动节奏 | - |

### 追踪实现要求
- 统一 URL 生成：由 Angela、Jessie、Judy 一起确认链接生成规则与归因参数策略（短链/UTM）。
- 来源分层：明确 Channel / Source / Medium / Campaign 的命名与写入规则。
- 指标落地：将上述指标对齐到 HubSpot 报表或数据仓仪表盘，确保可计算二次指标。

## 待确认事项
- Breeze AI 是否有额外费用、具体定价与套餐差异。
- Content Hub 需要的具体模块与权限范围（是否满足 6 Core Seats 使用需求）。
