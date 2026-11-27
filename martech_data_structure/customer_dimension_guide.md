# Customer 维表维护说明

本文档说明如何用 **person** 与 **company** 两张维表承接「表单收集」与「手动上传历史客户库」的客户信息，并做好来源与更新维护。

---

## 1. 希望收集的客户信息与维表映射

以下为希望收集的字段（含必填 *）及写入维表的对应关系。

| 收集字段 | 必填 | 写入表 | 维表字段 |
|----------|------|--------|----------|
| Name* | ✓ | person | full_name（或拆填 first_name + last_name） |
| Company* | ✓ | company | company_name |
| Industry* | ✓ | company | industry |
| Position | | person | job_title |
| Country* | ✓ | company | country |
| Email* | ✓ | person | email（唯一，用于去重） |
| Mobile Number | | person | mobile_number |
| Website | | company | website（完整 URL）；可同时解析写入 domain |
| Interested products / solutions | | person | interested_products_solutions（如 Hardware / Software） |
| Notes | | person | notes |
| source | — | person + company | source（见下节） |

**说明**：一条「客户」通常对应一个 **person**（联系人） + 一个 **company**（公司）。表单提交或上传时：根据 Email 解析/创建 person，根据 Company（及 domain/website）解析/创建 company；在产生行为事件（如 form_submitted）时，**event_log** 同一行可同时填 `person_id` 与 `company_id`，以关联该客户与公司。

---

## 2. source 字段：区分来源，便于维护

大量**手动上传历史客户数据库**时，必须能区分数据来源，便于排查、去重与清洗。

| source 取值示例 | 含义 |
|-----------------|------|
| form | 线上表单提交 |
| manual_upload | 单次或少量手动录入 |
| hubspot | 从 HubSpot 同步 |
| import_202501 | 某次批量导入（建议带日期或批次标识） |

**建议**：每次批量上传历史库时使用固定 source（如 `import_YYYYMM` 或 `import_批次名`），便于后续按来源筛选、覆盖或回滚。  
**updated_at**：每次写入或更新该条 person/company 时更新，便于识别「最近一次被哪次导入/表单更新」。

---

## 3. 手动上传历史库时的维护要点

1. **去重**  
   - **person**：以 `email` 为业务唯一键；同一 email 若已存在可做更新（覆盖或按规则合并），并更新 `source`、`updated_at`。  
   - **company**：以 `company_name` 或 `domain`/`website` 做匹配；同一公司若已存在可更新并写 `source`、`updated_at`。

2. **必填项**  
   - 表单必填在库中对应：person 至少 email；company 至少 company_name、industry、country。  
   - 历史库若缺 Industry/Country，可先填空或「未填写」，后续由人工或规则补全。

3. **批次与审计**  
   - 用 `source` 标记批次（如 `import_202501`）；必要时可增加 `import_batch_id` 或单独导入日志表记录每次上传的文件名、行数、时间。

4. **与 event_log 的关系**  
   - 仅上传客户信息、无行为事件时，只写 person/company 维表，不写 event_log。  
   - 若历史库中带有「某日留资」「某日下载」等行为，可再转为 event_log 事件，并关联对应 person_id/company_id。

---

## 4. 表结构速查

- **person / company 完整字段**：见 [schema_v0.md](schema_v0.md) 第 2.1、2.2 节。  
- **建表 DDL**：见 [schema_v0.sql](schema_v0.sql)。  
- **可读配置**：见 [schema_v0.yaml](schema_v0.yaml) 中 `dimension_tables.person`、`dimension_tables.company`。

按上述方式维护 Customer 维表，即可统一支撑「表单收集」与「大量手动上传历史客户数据库」两类场景。
