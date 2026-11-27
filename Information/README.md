# Information 目录说明

## 目录用途

`Information/` 目录用于存放**带有业务含义和分析的信息层级文件**，区别于 `output_data/` 目录中的原始数据文件。

## 文件分类

### 数据层级
- **`raw_data/`** - 原始XML文件（未处理）
- **`output_data/`** - 处理后的原始数据（CSV格式，结构化数据）

### 信息层级
- **`Information/`** - 带有业务含义和分析的信息文件（本目录）
  - 树形结构可视化
  - 业务分析报告
  - 统计摘要
  - 对比分析报告

## 文件类型

### 1. 树形结构可视化
- `*_tree_detailed.txt` - 详细树形结构（技术层级）
- `*_tree.html` - HTML格式的交互式树形图
- `*_meaningful_tree.txt` - 带业务含义的树形结构（**推荐查看**）

### 2. 分析摘要
- `*_summary.txt` - 数据统计摘要

### 3. 对比分析
- `competitive_analysis_report.txt` - 竞品对比分析报告
- `competitive_analysis_report.json` - JSON格式的对比数据
- `comparison_table.csv` - 对比表格

## 使用建议

1. **查看业务结构**：打开 `*_meaningful_tree.txt` 文件
2. **查看统计摘要**：打开 `*_summary.txt` 文件
3. **查看对比分析**：打开 `competitive_analysis_report.txt` 文件
4. **交互式浏览**：在浏览器中打开 `*_tree.html` 文件

## 文件命名规则

- `{公司名}_analyzed_meaningful_tree.txt` - 带业务含义的树形图
- `{公司名}_analyzed_tree_detailed.txt` - 详细树形图
- `{公司名}_analyzed_tree.html` - HTML树形图
- `{公司名}_analyzed_summary.txt` - 统计摘要

