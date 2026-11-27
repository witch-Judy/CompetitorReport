# Martech分析报告可视化图表

**生成日期**: 2026-01-09  
**图表风格**: Seaborn统一风格  
**图表格式**: PNG (300 DPI)

---

## 📊 综合Dashboard

### Dashboard Overview
**文件**: `dashboard.png`  
**类型**: 综合仪表板（合并所有图表）  
**位置**: 报告最开始  
**布局**: 4x4网格布局
- 左上2x2：内容数量热力图
- 右上：技术栈工具分布（饼图、条形图）
- 中间行：内容营销规模、意识层级、Webinar vs Blog、转化机制
- 底部：内容与技术栈关联

---

## 📊 单独图表列表

### 1. Marketing Automation工具分布
**文件**: `marketing_automation_distribution.png`  
**类型**: 饼图  
**数据**: 18家公司Marketing Automation工具使用情况  
**位置**: 报告第1.1节

### 2. Analytics工具分布
**文件**: `analytics_distribution.png`  
**类型**: 条形图（横向）  
**数据**: 18家公司Analytics工具使用情况  
**位置**: 报告第1.2节

### 3. Tag Management工具分布
**文件**: `tag_management_distribution.png`  
**类型**: 饼图  
**数据**: 18家公司Tag Management工具使用情况  
**位置**: 报告第1.3节

### 4. Email Service工具分布
**文件**: `email_service_distribution.png`  
**类型**: 条形图（横向）  
**数据**: 18家公司Email Service工具使用情况  
**位置**: 报告第1.4节

### 5. 转化机制对比
**文件**: `conversion_mechanisms_grouped.png`  
**类型**: 分组条形图  
**数据**: Top 5公司转化机制对比（Contact Forms、Demo/Trial、Content Downloads）  
**位置**: 报告第3节

### 6. 18家公司内容数量热力图
**文件**: `content_heatmap.png`  
**类型**: 热力图  
**数据**: 18家公司内容营销资产分布（Webinar、Blog、Customer Stories、Resources）  
**位置**: 报告第7节  
**说明**: 使用对数刻度处理大数值差异，颜色深度表示内容数量，实际数值显示在单元格中

### 7. 内容营销规模对比
**文件**: `content_marketing_scale.png`  
**类型**: 条形图（横向）  
**数据**: Top 10公司内容营销规模（Webinar + Blog）  
**位置**: 报告第11.2.1节

### 8. 意识层级覆盖度对比
**文件**: `awareness_level_radar.png`  
**类型**: 雷达图  
**数据**: Top 5公司意识层级覆盖度（基于《Breakthrough Advertising》）  
**位置**: 报告第11.2.2节

### 9. 内容营销规模与技术栈复杂度关联
**文件**: `content_tech_correlation.png`  
**类型**: 散点图  
**数据**: 10家公司内容营销规模与技术栈复杂度关联  
**位置**: 报告第11.2.3节

### 10. Webinar vs Blog 内容策略对比
**文件**: `webinar_blog_scatter.png`  
**类型**: 散点图  
**数据**: 10家公司Webinar和Blog数量对比  
**位置**: 报告第11.2.3节

---

## 🎨 图表风格说明

- **色系**: Seaborn "husl" 调色板（统一风格）
- **风格**: Seaborn "whitegrid" 风格
- **字体**: 支持中文显示（Arial Unicode MS、SimHei、DejaVu Sans）
- **分辨率**: 300 DPI（适合打印和展示）
- **格式**: PNG格式

---

## 📝 数据来源

- BuiltWith技术栈数据
- 内容营销转化机制数据
- Browser工具直接验证
- 18家公司内容营销策略深度分析报告

---

## 🔄 更新说明

如需更新图表，运行：
```bash
python3 analysis/create_martech_visualizations.py
```

图表将自动生成并保存到 `companyAnalysis/visualizations/` 目录。

