# Content Library 设计说明

## 1. 结论：用维表就对了

**Content Library 在本系统中就是一张维表：`content`。**

- **事件里只放“坐标”**（铁律 B）：`event_log` 只存 `content_id`，不存标题、类型、链接等详情。
- **详情放在维表**：所有“这份内容是什么、在哪里、谁维护”的信息都在 **content** 表里；报表、归因、培育规则需要内容信息时，通过 `content_id` 关联即可。
- **与架构图一致**：Marketing Data Layer 里的 “Content + Resource Library (Whitepaper, Blog, Video)” 即这张维表。

因此：**Content Library = content 维表**，不需要再单独建一套“库”表；若有“文件夹/分类”等层级，可用本表自关联或扩展字段表达。

---

## 2. 设计原则

| 原则 | 做法 |
|------|------|
| 一条内容 = 一条记录 | 每份可被下载/观看/分享的资产（白皮书、案例、视频、博客文章等）对应一个 `content_id`。 |
| 多源统一 | 来自 Teams、OneDrive、网站后台、手动录入的内容，都落同一张表，用 `source_system`（及可选 `source`）区分来源。 |
| 可追溯 | 有 `created_at`、`updated_at`；若将来做版本，可加 `version` 或 content_version 子表，v0 不强制。 |
| 便于事件关联 | event_log 的 `content_downloaded`、`content_viewed` 等通过 `content_id` 连到本表，做归因、内容效果分析。 |

---

## 3. 维表字段与用途（当前 + 建议）

### 3.1 已有字段（v0）

| 字段 | 用途 |
|------|------|
| content_id | 主键；event_log 只存此 ID |
| title | 展示用标题 |
| content_type | whitepaper / case_study / blog / video / webinar / ebook / …，用于筛选与报表 |
| tags | 标签（数组或 jsonb），便于分类与推荐 |
| owner_team | 负责团队，便于维护归属 |
| file_url | 实际资源地址（OneDrive/Teams 链接或站内 URL） |
| thumbnail_url | 缩略图，列表/卡片展示 |
| published_at | 上线时间，用于“最近发布”等 |
| source_system | teams / onedrive / manual / cms，区分来源 |
| created_at | 入库时间 |

### 3.2 业务类型 vs 文件/媒体格式（能否“直接存储”）

- **content_type**（业务类型）：whitepaper / case_study / blog / video / webinar / ebook … — 表示“是什么内容”，**直接存在库里**。
- **format**（文件/媒体格式）：pdf / text / image / video 等（或 **mime_type**：application/pdf、text/plain、image/png、image/jpeg、video/mp4）— 表示“文件是什么格式”，也**直接存在库里**，便于按 PDF/图片/文本筛选、展示图标、校验下载方式。

**关于“直接存储”的两种含义**：

| 含义 | 能否在库里“直接存储” | 建议做法 |
|------|------------------------|----------|
| **类型/格式等元数据**（PDF、text、picture、video） | ✅ 可以 | 用 **content_type** + **format**（或 mime_type）字段存；库里只存这些描述信息。 |
| **文件本体**（PDF 二进制、图片二进制、视频文件） | ⚠️ 不推荐 | 文件放在 **对象存储/OneDrive/Teams**，库里只存 **file_url** 指向实际地址；数据库存元数据 + 链接，不存大二进制。 |

因此：**PDF、text、picture 等“类型”都可以在 content 表里直接存**（作为 format 或 mime_type）；**文件本身**不落库，通过 file_url 访问。

### 3.3 链接里的内容存在哪儿？

| 存什么 | 存在哪儿 |
|--------|----------|
| **链接本身**（file_url、thumbnail_url） | 本系统数据库 **content** 表里；库里只存 URL 字符串。 |
| **链接指向的内容**（PDF、图片、视频等文件本体） | **外部存储**，由你们实际使用的系统决定，不在本库。 |

**常见外部存储**（任选或组合）：

- **OneDrive / SharePoint / Teams**：文档、表格、PDF 等，适合已有 Microsoft 体系。
- **对象存储**：如 AWS S3、阿里云 OSS、Azure Blob、MinIO；适合图片、视频、大文件，可配合 CDN。
- **公司文件服务器 / NAS**：内网共享盘，file_url 可为 `file://` 或内部 HTTP 路径。
- **网站 / CMS**：若内容本身在官网或 CMS 上，file_url 就是该页或资源地址。
- **Sanity**：也是这种方式。内容与资源（图片、PDF 等）存在 **Sanity 的存储与 CDN** 上；你们库里只存**指向 Sanity 的 URL**（例如 Sanity 资源 URL 或通过 document id 解析出的 CDN 地址）。即：链接在 content 表，文件在 Sanity，和用 S3/OneDrive 同理。

本系统**不规定**具体用哪一种；只要在 **content** 表里把可访问的 **file_url** 填对，实际文件在哪儿由你们运维与现有 IT 环境决定。

**当前实现（已就绪）**：**Supabase 已接 Teams**。内容元数据与 file_url 存 Supabase **content** 表，文件本体上传到 Teams（底层 OneDrive for Business / SharePoint）；上传后得到的可分享链接写入 **content.file_url**。

### Teams 除了数据引入以外还有什么作用？

在本套数据结构里，Teams 的**唯一正式角色**是：**内容文件的存储位置**，通过“上传 → 拿链接 → 写入 content.file_url”完成**数据引入**（文件本体在 Teams，元数据与链接在 Supabase）。

**除此以外**，Teams 在你们日常业务里还可以承担（这些不写进 event_log，按需使用即可）：

| 作用 | 说明 |
|------|------|
| **内容协作与存放** | 市场/内容团队在 Teams 频道里创作、审阅、定稿；定稿后再在 Supabase 侧建一条 content 记录、把 Teams 分享链接填进 file_url，供前台与归因使用。 |
| **内部流程与审批** | 如活动上线、内容发布前的审批在 Teams 里走（讨论、@人、通过），不进入本系统事件表；需要的话可日后把“发布/上线”作为一条运营事件落 event_log（可选）。 |
| **与 Sales 的协同** | 培育效果好的 leads 推给 Sales 后，沟通、跟单可能在 Teams 里进行；本系统只负责“推 leads + 收 feedback”，不把 Teams 内的聊天或会议当作事件写入。 |
| **统一文件与权限** | 公司已有 Teams/OneDrive 权限体系，内容文件放在 Teams 即可沿用现有权限与审计，无需再建一套文件权限。 |

总结：**数据层面** Teams = 内容文件存储 + 链接引入；**业务层面** Teams = 协作、审批、与 Sales 协同等，由你们在 Teams 里用即可，本系统不强制把这些行为落库。若将来希望“谁在 Teams 里看了/下载了某文件”也进 event_log，再单独设计 Connector 与 event_type 即可。

### 3.4 前端 CMS 用什么比较好？（Supabase + Teams 栈）

你们之前用 **Sanity**，现在库在 **Supabase**、文件在 **Teams**，前端 CMS 可以这样选：

| 方案 | 做法 | 优点 | 注意点 |
|------|------|------|--------|
| **继续用 Sanity** | 编辑在 Sanity，通过同步任务把内容元数据（及资源链接）写到 Supabase **content** 表；file_url 可存 Sanity CDN 地址，或同步时改为 Teams 链接（若文件也迁到 Teams）。 | 沿用现有编辑体验和流程，无需换习惯。 | 两套系统：Sanity 为创作层，Supabase 为 GTM/分析用；需维护同步逻辑与一致性。 |
| **Supabase 当唯一内容源 + 自建/轻量 Admin** | 不做独立 CMS，用 Supabase 的 **content** 表直接做内容源；编辑端用自建管理页（Next/React + 表单写 Supabase），文件上传走 **Microsoft Graph API** 到 Teams/OneDrive，把返回的分享链接写入 file_url。 | 单一数据源、和 event_log/培育逻辑同库，简单。 | 需要自己或低代码搭管理界面；富文本/媒体体验需自己选组件。 |
| **Directus** | Directus 连接你们现有 **Supabase Postgres**，把 **content** 表映射为 collection；编辑在 Directus 里完成，文件可配置为“存 URL”（手动贴 Teams 链接）或接插件/自定义存 Teams。 | 现成的后台 UI、权限、API，且直接复用 Supabase 表结构。 | 需确认 Directus 对“文件只存 URL、实体在 Teams”的用法是否顺手；必要时自定义存储适配。 |
| **Payload CMS** | 用 Postgres（Supabase）作数据库，content 用 Payload collection；上传可走自定义 storage adapter（例如上传到 Teams 后只把 link 存 Payload）。 | 类型安全、React 生态、可自扩展。 | 需写或选 Teams 的 storage 适配；部署与运维自管。 |

**建议**：  
- 若**非常依赖现有 Sanity 流程、暂时不想动编辑侧**：可继续用 Sanity，把 Sanity 当成“创作 CMS”，用定时或事件同步把内容推到 Supabase **content** 表（及 event 用到的 content_id），file_url 用 Sanity 资源链接或后续改为 Teams 链接均可。  
- 若**希望内容与 GTM 数据同库、减少系统数**：**可以不用 Sanity**；用 Supabase + 自建/轻量 Admin 或 Directus 连 Supabase 即可，文件统一用 Teams 链接存 **content.file_url**。

**文件上传到哪儿？**  
→ **上传到 Teams**（已实现 Supabase 接 Teams）。上传后得到的分享链接写入 **content.file_url**；内容元数据（标题、类型、format、status 等）在 Supabase **content** 表，文件本体只在 Teams，库里只存链接。

以上仅作选型参考，不约束实现；选定后可在本仓库补充「内容同步方式」或「CMS 与 content 表对接说明」。

### 3.5 其他建议补充（便于 Content Library 运营）

| 字段 | 类型 | 用途 |
|------|------|------|
| **format** | text | pdf / text / image / video / audio；或存 mime_type（application/pdf, image/png, …） |
| **status** | text | draft / published / archived，控制是否在前台可见、是否参与统计 |
| **language** | text | 语言（如 zh / en），多语言内容库时必用 |
| **slug** | text | URL 友好标识，用于生成固定链接、去重 |
| **updated_at** | timestamptz | 最近一次元数据或状态变更时间 |

若内容有**层级**（如“某白皮书属于某主题/文件夹”），可加 **parent_content_id**（自关联）或 **category** 文本；v0 也可用 tags 表达分类。

---

## 4. 常见 format / mime_type 示例

| 展示类型 | format 取值 | mime_type 取值（可选） |
|----------|-------------|-------------------------|
| PDF | pdf | application/pdf |
| 纯文本 | text | text/plain |
| 图片 | image | image/png, image/jpeg, image/gif, image/webp |
| 视频 | video | video/mp4, video/webm |
| 音频 | audio | audio/mpeg, audio/wav |
| 网页/HTML | html | text/html |

v0 用 **format** 一个字段即可（pdf / text / image / video / audio）；若需要更细（如区分 png 与 jpeg），可再加 **mime_type** 或把 format 存成 mime_type。

---

## 5. 是否需要拆成多张表？

- **v0：一张维表足够**  
  所有“可被引用”的内容资产一条记录一个 `content_id`，简单清晰；event 只认 content_id，语义层只读这一张表即可。

- **可选扩展（按需再加）**  
  - **内容版本**：若同一标题有多版（v1/v2 白皮书），可加 `content_version` 子表（content_id + version + file_url + published_at），或当前表加 `version` 字段；v0 可先不建。  
  - **文件夹/分类**：用 `parent_content_id` 自关联或 `category`/`tags` 即可，不必为“库”单独建 folder 表，除非有复杂权限/层级导航需求。

---

## 6. 与 event_log 的配合

- 行为事件（如 `content_downloaded`、`content_viewed`）在 **event_log** 里只存 `content_id`（+ person_id、campaign_id 等）。
- 报表/归因/培育规则需要“下了哪份白皮书、标题是什么、类型是什么”时：**JOIN content** 即可。
- 这样 Content Library 的增删改（新加资源、下架、改标题）只动维表，历史事件不变，符合“事件只放坐标”的设计。

---

## 7. 小结

| 问题 | 答案 |
|------|------|
| Content Library 要不要单独建表？ | 不需要；**就是 content 维表**。 |
| 作为维表够用吗？ | 够用；事件只存 content_id，详情全在 content，便于归因与运营。 |
| 建议再补哪些字段？ | status、language、slug、updated_at；若有层级再考虑 parent_content_id 或 category。 |

建表与字段定义见 [schema_v0.md](schema_v0.md) 第 2.3 节、[schema_v0.sql](schema_v0.sql)、[schema_v0.yaml](schema_v0.yaml)。  
若此前已建过 content 表且无 **format** 列，可执行：`ALTER TABLE content ADD COLUMN format TEXT;`
