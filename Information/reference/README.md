# 参考公司数据分析

本目录包含参考公司的网站结构分析结果，按照标准SOP流程处理。

## 处理流程

1. **原始数据** (`raw_data/reference/`) - 从各公司官网下载的sitemap.xml文件
2. **结构化数据** (`output_data/reference/`) - 解析后的CSV格式数据
3. **信息数据** (`Information/reference/`) - 带业务含义的导航树结构

## 公司列表

| 公司 | 状态 | URL数量 | 说明 |
|------|------|---------|------|
| stripe | ✅ | 4,457 | 已处理完成 |
| samsara | ✅ | 5,731 | 已处理完成 |
| palantir | ✅ | 635 | 已处理完成 |
| apple | ✅ | - | 主站sitemap（已处理） |
| xiaomi | ✅ | 16,741 | 已处理完成 |
| byd | ✅ | 4,019 | 已处理完成 |

**总计**: 5个公司成功处理，共 **31,583个URLs**

## 文件结构

### output_data/reference/

包含解析后的CSV数据文件：
- `stripe_analyzed.csv` - Stripe网站结构数据
- `samsara_analyzed.csv` - Samsara网站结构数据
- `palantir_analyzed.csv` - Palantir网站结构数据
- `xiaomi_analyzed.csv` - 小米网站结构数据
- `byd_analyzed.csv` - BYD网站结构数据

### Information/reference/

包含导航树结构文件：
- `stripe_analyzed_complete_tree.txt` - Stripe完整导航树
- `samsara_analyzed_complete_tree.txt` - Samsara完整导航树
- `palantir_analyzed_complete_tree.txt` - Palantir完整导航树
- `xiaomi_analyzed_complete_tree.txt` - 小米完整导航树
- `byd_analyzed_complete_tree.txt` - BYD完整导航树

## 数据特点

### Stripe (4,457 URLs)
- 支付和金融科技公司
- 网站结构清晰，以产品和服务为主

### Samsara (5,731 URLs)
- IoT和车队管理公司
- 内容类型丰富，包含产品、资源、案例等

### Palantir (635 URLs)
- 大数据分析公司
- 网站结构相对简洁，专注于核心产品

### Xiaomi (16,741 URLs)
- 消费电子公司
- 网站规模最大，包含大量产品页面和内容

### BYD (4,019 URLs)
- 新能源汽车公司
- 网站结构完整，包含产品、新闻、服务等

## 用途

这些参考公司的数据用于：
- **对比分析**: 与竞品公司进行横向对比
- **行业参考**: 了解不同行业的网站结构特点
- **最佳实践**: 学习优秀公司的内容组织方式
- **策略研究**: 分析不同公司的内容营销策略

## 处理日期

2026-01-05

## 注意事项

- Apple的sitemap是索引文件，如需完整数据需要展开所有47个sitemap引用
- 所有数据已按照标准SOP流程处理，与竞品公司数据格式一致
- 可用于与竞品公司进行对比分析

