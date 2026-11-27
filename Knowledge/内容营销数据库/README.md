# 内容营销数据库

## 📋 概述

这是一个庞大的竞品内容营销数据库，用于研究不同公司的内容营销策略、材料分类方式和内容写作模式。

## 📁 文件结构

```
内容营销数据库/
├── content_database.csv          # 主数据库（CSV格式）
├── content_database.json         # 主数据库（JSON格式，便于程序访问）
├── content_templates.json        # 内容模板库
├── 内容营销深度分析报告.md        # 详细分析报告
└── README.md                     # 本文件
```

## 🎯 数据库内容

### 1. 内容元数据
- **URL**: 内容链接
- **公司**: 所属公司
- **内容类型**: whitepaper, case_study, webinar, blog, ebook, datasheet等
- **分类层级**: category, subcategory
- **材料名称**: material_name
- **年份/月份**: 发布时间
- **URL结构**: path_segments, depth

### 2. 内容详情（如果启用了fetch）
- **标题**: title
- **Meta描述**: meta_description
- **H1标题**: h1
- **正文预览**: body_preview（前500字符）
- **结构化数据**: structured_data（JSON-LD）
- **字数统计**: word_count

## 🔍 使用方法

### 基础分析（不爬取内容）

```bash
# 分析所有公司的所有内容类型
python3 analysis/content_database_builder.py

# 只分析特定内容类型
python3 analysis/content_database_builder.py --content-types whitepaper case_study

# 只分析特定公司
python3 analysis/content_database_builder.py --companies cognite aveva honeywell

# 限制每个公司的数量
python3 analysis/content_database_builder.py --limit 100
```

### 深度分析（爬取实际内容）

```bash
# 爬取内容详情（标题、描述等）
python3 analysis/content_database_builder.py --fetch

# 分析whitepaper并爬取内容
python3 analysis/content_database_builder.py --content-types whitepaper --fetch --limit 20
```

## 📊 分析维度

### 1. 内容分类体系
- 不同公司的内容分类方式
- 分类层级结构
- 分类命名约定

### 2. 内容类型分布
- 各公司偏好的内容类型
- 内容类型组合策略
- 内容类型与分类的关系

### 3. 命名约定
- URL命名模式（kebab-case, snake_case等）
- 材料命名规律
- 标题模式

### 4. 内容模板
- 不同类型内容的URL模式
- 分类结构模式
- 命名模式示例

## 💡 应用场景

### 1. 内容策略研究
- 了解竞品如何组织内容
- 学习最佳实践
- 发现内容空白

### 2. 内容创作参考
- 参考竞品的标题模式
- 学习内容结构
- 了解分类方式

### 3. SEO优化
- 分析URL结构
- 研究关键词使用
- 了解内容组织方式

### 4. 内容营销规划
- 规划内容类型组合
- 设计分类体系
- 制定内容命名规范

## ⚠️ 注意事项

1. **爬取内容**: 使用`--fetch`选项会实际访问网页，请遵守robots.txt和网站使用条款
2. **请求频率**: 默认有1秒延迟，避免对目标网站造成压力
3. **数据量**: 完整数据库可能包含数十万条记录，建议使用`--limit`限制
4. **内容类型**: 支持的内容类型包括：whitepaper, case_study, webinar, blog, ebook, datasheet, video, podcast, infographic, report

## 🔄 更新数据库

```bash
# 重新构建数据库
python3 analysis/content_database_builder.py

# 只更新特定内容类型
python3 analysis/content_database_builder.py --content-types whitepaper --fetch
```

## 📈 数据统计

运行分析后，查看`内容营销深度分析报告.md`了解：
- 各公司的内容数量
- 内容类型分布
- 分类体系对比
- 命名模式分析
- 内容模板示例



