# 参考公司Sitemap数据

本目录包含参考公司的sitemap.xml文件，用于对比分析和参考。

## 公司列表

| 公司 | 状态 | 文件大小 | 说明 |
|------|------|----------|------|
| stripe | ✅ | 577 字节 | 索引文件 (6个sitemap引用) |
| samsara | ✅ | 968 字节 | 索引文件 (8个sitemap引用) |
| palantir | ✅ | 116,565 字节 | 635个URLs |
| apple | ✅ | 3,776 字节 | 索引文件 (47个sitemap引用) |
| tesla | ❌ | - | 未找到sitemap (403 Forbidden) |
| xiaomi | ✅ | 2,665,927 字节 | 16,741个URLs (已修复XML格式) |
| huawei | ❌ | - | 未找到sitemap (robots.txt中注释掉) |
| BYD | ✅ | 8,554 字节 | 索引文件 (78个sitemap引用) |

## 文件结构

```
reference/
├── README.md
├── stripe/
│   └── stripe.xml
├── samsara/
│   └── samsara.xml
├── palantir/
│   └── palantir.xml
├── apple/
│   └── apple.xml
├── xiaomi/
│   └── xiaomi.xml
├── byd/
│   └── byd.xml
└── huawei/
    └── huawei.xml (如果找到)
```

## 注意事项

1. **索引文件**: stripe, samsara, apple, byd 是sitemap索引文件，需要展开才能获取所有URL
2. **XML格式**: xiaomi的文件已修复URL中的未转义&符号
3. **访问限制**: tesla的网站返回403，可能需要其他方法获取
4. **文件格式**: 所有文件统一命名为 `{company}.xml`

## 数据收集日期

2026-01-05

## 用途

这些参考公司的数据用于：
- 对比分析不同行业的网站结构
- 研究不同公司的内容策略
- 作为benchmark参考

