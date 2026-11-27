# Website Technology Profile Data

本目录用于存储从 BuiltWith 获取的网站技术栈分析数据。

## 目录结构

```
Website Technology Profile Data/
├── README.md                          # 本说明文件
├── builtwith_technology_profile_template.csv  # 数据模板
├── builtwith_technology_profiles.csv         # 整理后的技术栈数据
└── raw_data/                          # 原始BuiltWith报告（可选）
    ├── cognite_builtwith.txt
    ├── aveva_builtwith.txt
    └── ...
```

## 数据字段说明

- **Company**: 公司名称
- **CMS**: 内容管理系统（如 WordPress, Drupal, Sitecore）
- **Web Server**: Web服务器（如 Nginx, Apache, IIS）
- **JavaScript Libraries**: JavaScript库（如 jQuery, React, Vue.js）
- **Analytics**: 分析工具（如 Google Analytics, Adobe Analytics）
- **Marketing Automation**: 营销自动化工具（如 Marketo, HubSpot, Eloqua）
- **CDN**: 内容分发网络（如 Cloudflare, Akamai, AWS CloudFront）
- **Hosting**: 托管服务（如 AWS, Azure, Google Cloud）
- **SSL Certificate**: SSL证书提供商
- **Email Service**: 邮件服务（如 SendGrid, Mailchimp, Amazon SES）
- **Tag Management**: 标签管理工具（如 Google Tag Manager, Tealium）
- **Other Technologies**: 其他技术（如支付网关、聊天工具等）

## 使用方法

1. 将 BuiltWith 报告内容复制到文本文件，保存到 `raw_data/` 目录
2. 运行数据整理脚本：
   ```bash
   python3 analysis/parse_builtwith_data.py
   ```
3. 检查整理后的数据：`builtwith_technology_profiles.csv`

## 数据来源

- BuiltWith: https://builtwith.com/
- 数据获取方式：手动复制 BuiltWith 报告页面内容


