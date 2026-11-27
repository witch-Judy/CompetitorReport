# Structured Data Directory

本目录包含从导航树结构导出的结构化数据文件，用于画图和数据分析。

## 📁 目录结构

```
Information/structured_data/
├── {company}_navigation_tree.json      # JSON格式（树形结构，适合可视化）
├── {company}_navigation_tree.csv      # CSV格式（扁平化结构，适合数据分析）
└── {company}_navigation_tree.parquet   # Parquet格式（高效存储，适合大数据分析）
```

## 📊 数据格式说明

### JSON 格式
- **用途**: 树形可视化（D3.js, ECharts, Plotly等）
- **结构**: 嵌套的树形结构，包含完整的层级关系
- **字段**:
  - `company`: 公司名称
  - `structure`: 结构类型
  - `categories`: 分类数组，每个分类包含：
    - `name`: 分类名称
    - `key`: 分类键值
    - `type`: 节点类型（category/subcategory/page）
    - `children`: 子节点数组
    - `url`: 页面URL（仅page类型）
    - `languages`: 支持的语言列表
    - `all_urls`: 所有URL列表

### CSV 格式
- **用途**: 数据分析（Excel, Pandas, R等）
- **结构**: 扁平化的表格结构，每行代表一个页面节点
- **字段**:
  - `company`: 公司名称
  - `level1`, `level1_key`: 一级分类（名称和键）
  - `level2`, `level2_key`: 二级分类（名称和键）
  - `level3`, `level3_key`: 三级分类（名称和键）
  - `page_name`: 页面名称
  - `page_url`: 页面URL
  - `depth`: 层级深度（1-3）
  - `path`: 路径
  - `full_path`: 完整路径
  - `node_type`: 节点类型（page）
  - `languages`: 支持的语言（逗号分隔）
  - `url_count`: URL数量

### Parquet 格式
- **用途**: 高效存储和查询（Spark, Pandas, DuckDB等）
- **结构**: 与CSV相同，但使用列式存储，压缩效率更高
- **优势**: 
  - 文件大小通常比CSV小3-5倍
  - 读取速度更快
  - 支持列式查询优化

## 📈 数据统计

- **公司数量**: 18个
- **总文件数**: 54个（每个公司3种格式）
- **总数据量**: 约680MB

## 🔧 使用示例

### Python (Pandas)

```python
import pandas as pd

# 读取CSV
df = pd.read_csv('Information/structured_data/cognite_navigation_tree.csv')

# 读取Parquet（更高效）
df = pd.read_parquet('Information/structured_data/cognite_navigation_tree.parquet')

# 数据分析示例
print(f"总页面数: {len(df)}")
print(f"一级分类数: {df['level1'].nunique()}")
print(f"平均深度: {df['depth'].mean()}")
```

### Python (JSON可视化)

```python
import json

# 读取JSON
with open('Information/structured_data/cognite_navigation_tree.json') as f:
    tree_data = json.load(f)

# 使用D3.js或ECharts进行树形可视化
# tree_data['categories'] 包含所有分类
```

### JavaScript (D3.js)

```javascript
// 读取JSON文件
d3.json('Information/structured_data/cognite_navigation_tree.json')
  .then(data => {
    // 使用D3.js绘制树形图
    // data.categories 包含所有分类
  });
```

## 📝 数据来源

这些结构化数据基于 `output_data/{company}_analyzed.csv` 生成，这些CSV文件是从原始XML sitemap文件解析得到的。

## 🔄 更新数据

如果需要重新生成这些结构化数据，运行：

```bash
python3 analysis/export_information_structured_data.py --all
```

## 📌 注意事项

1. **数据源**: 这些数据基于**未清洗的原始数据**，包含所有页面（包括测试页、政策页等）
2. **语言合并**: 相同内容的不同语言版本已合并，只显示内容本身
3. **层级结构**: 最多支持3层分类（level1, level2, level3）
4. **文件命名**: 文件名中的公司名称可能与原始数据略有不同（大小写、连字符等）

## 📚 相关文件

- **原始数据**: `output_data/{company}_analyzed.csv`
- **文本导航树**: `Information/{company}_analyzed_complete_tree.txt`
- **生成脚本**: `analysis/export_information_structured_data.py`

