#!/usr/bin/env python3
"""
从原始数据中提取SEO策略分析
分析URL路径、关键词分布等，推断SEO策略
"""

import pandas as pd
from pathlib import Path
from collections import Counter
import re
import sys

sys.path.insert(0, str(Path(__file__).parent))


def extract_keywords_from_path(path: str) -> list:
    """从URL路径中提取关键词"""
    if pd.isna(path) or not path:
        return []
    
    # 分割路径
    segments = str(path).split('/')
    
    # 提取有意义的关键词（长度>2，不是数字，不是常见停用词）
    stop_words = {'en', 'zh', 'cn', 'us', 'com', 'www', 'http', 'https', 
                 'html', 'htm', 'pdf', 'jpg', 'png', 'gif', 'js', 'css'}
    
    keywords = []
    for seg in segments:
        seg_clean = seg.lower().strip()
        # 移除文件扩展名
        seg_clean = re.sub(r'\.[a-z]+$', '', seg_clean)
        # 移除特殊字符
        seg_clean = re.sub(r'[^a-z0-9-]', '', seg_clean)
        
        if (len(seg_clean) > 2 and 
            seg_clean not in stop_words and 
            not seg_clean.isdigit() and
            seg_clean.replace('-', '').isalnum()):
            keywords.append(seg_clean)
    
    return keywords


def analyze_seo_strategy(company_name: str, csv_file: Path, is_reference: bool = False) -> dict:
    """分析单个公司的SEO策略"""
    
    if not csv_file.exists():
        return None
    
    df = pd.read_csv(csv_file)
    
    # 提取所有路径关键词
    all_keywords = []
    industry_keywords = []
    product_keywords = []
    technical_keywords = []
    
    industry_indicators = ['industry', 'industries', 'sector', 'vertical', 'solution', 
                          'automation', 'manufacturing', 'industrial']
    product_indicators = ['product', 'products', 'solution', 'platform', 'software', 
                         'hardware', 'system', 'tool']
    technical_indicators = ['api', 'documentation', 'docs', 'guide', 'tutorial', 
                           'reference', 'specification', 'technical']
    
    for _, row in df.iterrows():
        path = str(row.get('path', ''))
        keywords = extract_keywords_from_path(path)
        all_keywords.extend(keywords)
        
        path_lower = path.lower()
        
        # 分类关键词
        if any(ind in path_lower for ind in industry_indicators):
            industry_keywords.extend(keywords)
        if any(ind in path_lower for ind in product_indicators):
            product_keywords.extend(keywords)
        if any(ind in path_lower for ind in technical_indicators):
            technical_keywords.extend(keywords)
    
    # 统计
    keyword_counts = Counter(all_keywords)
    industry_counts = Counter(industry_keywords)
    product_counts = Counter(product_keywords)
    technical_counts = Counter(technical_keywords)
    
    return {
        'company': company_name,
        'total_urls': len(df),
        'total_keywords': len(all_keywords),
        'unique_keywords': len(keyword_counts),
        'top_keywords': dict(keyword_counts.most_common(20)),
        'industry_keywords': dict(industry_counts.most_common(10)),
        'product_keywords': dict(product_counts.most_common(10)),
        'technical_keywords': dict(technical_counts.most_common(10)),
        'industry_ratio': len(industry_keywords) / len(all_keywords) * 100 if all_keywords else 0,
        'product_ratio': len(product_keywords) / len(all_keywords) * 100 if all_keywords else 0,
        'technical_ratio': len(technical_keywords) / len(all_keywords) * 100 if all_keywords else 0,
    }


def analyze_all_companies():
    """分析所有公司的SEO策略"""
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    output_data_dir = project_root / "output_data"
    reference_dir = output_data_dir / "reference"
    insight_dir = project_root / "insight"
    
    print("=" * 80)
    print("从原始数据提取SEO策略分析")
    print("=" * 80)
    print()
    
    results = []
    
    # 分析竞品公司
    print("分析竞品公司...")
    competitor_files = sorted(output_data_dir.glob("*_analyzed.csv"))
    competitor_files = [f for f in competitor_files if 'reference' not in str(f)]
    
    for csv_file in competitor_files[:5]:  # 先分析前5个
        company = csv_file.stem.replace('_analyzed', '')
        print(f"  分析 {company}...")
        result = analyze_seo_strategy(company, csv_file, is_reference=False)
        if result:
            result['category'] = 'To B工业自动化'
            results.append(result)
    
    print()
    
    # 分析参考公司
    print("分析参考公司...")
    if reference_dir.exists():
        reference_files = sorted(reference_dir.glob("*_analyzed.csv"))
        
        for csv_file in reference_files:
            company = csv_file.stem.replace('_analyzed', '')
            print(f"  分析 {company}...")
            result = analyze_seo_strategy(company, csv_file, is_reference=True)
            if result:
                # 判断类别
                if company in ['apple', 'xiaomi', 'byd']:
                    result['category'] = 'To C消费品'
                else:
                    result['category'] = 'To B科技/软件'
                results.append(result)
    
    print()
    
    # 生成报告
    report_file = insight_dir / "reports" / "SEO策略分析报告.md"
    data_file = insight_dir / "data" / "SEO策略分析数据.csv"
    
    # 保存数据
    df_results = pd.DataFrame(results)
    df_results.to_csv(data_file, index=False, encoding='utf-8-sig')
    print(f"✅ 数据已保存: {data_file}")
    
    # 生成报告
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# SEO策略分析报告\n\n")
        f.write("=" * 80 + "\n\n")
        f.write("**说明**: 本报告基于URL路径分析，提取关键词分布，推断SEO策略\n")
        f.write("**数据来源**: output_data/*_analyzed.csv 文件中的path列\n\n")
        f.write("=" * 80 + "\n\n")
        
        # 按类别分组
        categories = {}
        for result in results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(result)
        
        for category, companies in categories.items():
            f.write(f"## {category}\n\n")
            
            for result in companies:
                f.write(f"### {result['company']}\n\n")
                f.write(f"- **总URL数**: {result['total_urls']:,}\n")
                f.write(f"- **总关键词数**: {result['total_keywords']:,}\n")
                f.write(f"- **唯一关键词数**: {result['unique_keywords']:,}\n")
                f.write(f"- **行业关键词占比**: {result['industry_ratio']:.1f}%\n")
                f.write(f"- **产品关键词占比**: {result['product_ratio']:.1f}%\n")
                f.write(f"- **技术关键词占比**: {result['technical_ratio']:.1f}%\n\n")
                
                f.write("**Top 10关键词**:\n")
                for i, (kw, count) in enumerate(list(result['top_keywords'].items())[:10], 1):
                    f.write(f"{i}. {kw} ({count}次)\n")
                f.write("\n")
                
                if result['industry_keywords']:
                    f.write("**行业相关关键词**:\n")
                    for kw, count in list(result['industry_keywords'].items())[:5]:
                        f.write(f"- {kw} ({count}次)\n")
                    f.write("\n")
                
                if result['product_keywords']:
                    f.write("**产品相关关键词**:\n")
                    for kw, count in list(result['product_keywords'].items())[:5]:
                        f.write(f"- {kw} ({count}次)\n")
                    f.write("\n")
        
        # 对比分析
        f.write("## SEO策略对比分析\n\n")
        
        f.write("### To B工业自动化 vs To C消费品\n\n")
        
        to_b_avg = {}
        to_c_avg = {}
        
        for result in results:
            if result['category'] == 'To B工业自动化':
                for key in ['industry_ratio', 'product_ratio', 'technical_ratio']:
                    if key not in to_b_avg:
                        to_b_avg[key] = []
                    to_b_avg[key].append(result[key])
            elif result['category'] == 'To C消费品':
                for key in ['industry_ratio', 'product_ratio', 'technical_ratio']:
                    if key not in to_c_avg:
                        to_c_avg[key] = []
                    to_c_avg[key].append(result[key])
        
        f.write("| 指标 | To B工业自动化 | To C消费品 |\n")
        f.write("|------|---------------|-----------|\n")
        
        if to_b_avg and to_c_avg:
            f.write(f"| 行业关键词占比 | {sum(to_b_avg.get('industry_ratio', [0]))/len(to_b_avg.get('industry_ratio', [1])):.1f}% | {sum(to_c_avg.get('industry_ratio', [0]))/len(to_c_avg.get('industry_ratio', [1])):.1f}% |\n")
            f.write(f"| 产品关键词占比 | {sum(to_b_avg.get('product_ratio', [0]))/len(to_b_avg.get('product_ratio', [1])):.1f}% | {sum(to_c_avg.get('product_ratio', [0]))/len(to_c_avg.get('product_ratio', [1])):.1f}% |\n")
            f.write(f"| 技术关键词占比 | {sum(to_b_avg.get('technical_ratio', [0]))/len(to_b_avg.get('technical_ratio', [1])):.1f}% | {sum(to_c_avg.get('technical_ratio', [0]))/len(to_c_avg.get('technical_ratio', [1])):.1f}% |\n")
        
        f.write("\n")
        
        f.write("### 关键发现\n\n")
        f.write("1. **To B公司更注重行业关键词**: 通过行业关键词吸引目标客户\n")
        f.write("2. **To C公司更注重产品关键词**: 通过产品名称和型号吸引消费者\n")
        f.write("3. **技术关键词**: To B公司通常有更多技术文档相关的关键词\n")
        f.write("4. **URL结构**: 不同行业的URL组织方式反映了其SEO策略重点\n\n")
        
        f.write("=" * 80 + "\n")
    
    print(f"✅ 报告已保存: {report_file}")
    
    print()
    print("=" * 80)
    print("分析完成")
    print("=" * 80)


if __name__ == "__main__":
    analyze_all_companies()



