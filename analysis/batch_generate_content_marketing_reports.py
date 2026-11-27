#!/usr/bin/env python3
"""
批量生成内容营销策略深度分析报告
"""
import pandas as pd
import re
from collections import Counter
from pathlib import Path
from datetime import datetime

# 公司列表和域名映射
COMPANIES = {
    'Aveva': 'aveva.com',
    'Tulip': 'tulip.co',
    'C3 AI': 'c3.ai',
    'Yokogawa': 'yokogawa.com',
    'Emerson': 'emerson.com',
    'Rockwell Automation': 'rockwellautomation.com',
    'Honeywell': 'honeywell.com',
    'Schneider Electric': 'schneider-electric.com',
    'Bosch': 'bosch.com',
    'GE': 'ge.com',
    'Hitachi': 'hitachi.com',
    'Ignition': 'inductiveautomation.com',
    'HiveMQ': 'hivemq.com',
    'UMH': 'umh.com',
    'Univers': 'univers.com'
}

def extract_keywords(text, min_length=3):
    """提取关键词"""
    if pd.isna(text):
        return []
    text_str = str(text).lower()
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text_str)
    stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'let', 'put', 'say', 'she', 'too', 'use', 'www', 'com', 'html', 'https', 'http', 'with', 'from', 'this', 'that', 'have', 'been', 'more', 'than', 'what', 'when', 'where', 'which', 'while', 'will', 'would', 'global', 'en', 'de', 'es', 'fr', 'zh', 'cn', 'us', 'uk'}
    return [w for w in words if w not in stop_words and len(w) >= min_length]

def find_data_file(company_name, domain):
    """查找数据文件"""
    patterns = [
        f'{company_name.replace(" ", "_")}_analyzed.csv',
        f'{company_name.replace(" ", "-")}_analyzed.csv',
        f'{domain.replace(".", "-")}_analyzed.csv',
        f'{company_name.lower().replace(" ", "_")}_analyzed.csv',
    ]
    
    for pattern in patterns:
        file_path = Path(f'output_data/{pattern}')
        if file_path.exists():
            return file_path
    
    # 尝试查找包含公司名的文件
    output_dir = Path('output_data')
    for file in output_dir.glob('*analyzed.csv'):
        if company_name.lower().replace(' ', '') in file.stem.lower() or domain.replace('.', '') in file.stem.lower():
            return file
    
    return None

def analyze_company(company_name, domain):
    """分析单个公司"""
    print(f'\n{"="*60}')
    print(f'分析 {company_name} ({domain})')
    print(f'{"="*60}')
    
    # 查找数据文件
    csv_file = find_data_file(company_name, domain)
    if not csv_file:
        print(f'  ⚠️ 未找到数据文件')
        return None
    
    try:
        df = pd.read_csv(csv_file)
        print(f'  ✓ 加载数据: {len(df)} 个URL')
        
        # 基础统计
        total_urls = len(df)
        content_types = df['content_type'].value_counts().to_dict()
        
        # 内容营销资产统计
        blog_count = df['is_blog'].sum() if 'is_blog' in df.columns else 0
        webinar_count = df['is_webinar'].sum() if 'is_webinar' in df.columns else 0
        resource_count = df['is_resource'].sum() if 'is_resource' in df.columns else 0
        customer_story_count = df['is_customer_story'].sum() if 'is_customer_story' in df.columns else 0
        
        # 路径分析
        stories_df = df[df['path'].str.contains('stories|story', case=False, na=False)].copy() if 'path' in df.columns else pd.DataFrame()
        resources_df = df[df['path'].str.contains('resources|resource', case=False, na=False)].copy() if 'path' in df.columns else pd.DataFrame()
        webinar_df = df[df['path'].str.contains('webinar', case=False, na=False)].copy() if 'path' in df.columns else pd.DataFrame()
        blog_df = df[df['path'].str.contains('blog', case=False, na=False)].copy() if 'path' in df.columns else pd.DataFrame()
        
        # 关键词分析
        stories_keywords = []
        resources_keywords = []
        webinar_keywords = []
        blog_keywords = []
        
        if len(stories_df) > 0:
            for _, row in stories_df.head(100).iterrows():
                if 'url' in row and 'path' in row:
                    keywords = extract_keywords(row.get('url', '')) + extract_keywords(row.get('path', ''))
                    stories_keywords.extend(keywords)
        
        if len(resources_df) > 0:
            for _, row in resources_df.head(100).iterrows():
                if 'url' in row and 'path' in row:
                    keywords = extract_keywords(row.get('url', '')) + extract_keywords(row.get('path', ''))
                    resources_keywords.extend(keywords)
        
        if len(webinar_df) > 0:
            for _, row in webinar_df.head(100).iterrows():
                if 'url' in row and 'path' in row:
                    keywords = extract_keywords(row.get('url', '')) + extract_keywords(row.get('path', ''))
                    webinar_keywords.extend(keywords)
        
        if len(blog_df) > 0:
            for _, row in blog_df.head(100).iterrows():
                if 'url' in row and 'path' in row:
                    keywords = extract_keywords(row.get('url', '')) + extract_keywords(row.get('path', ''))
                    blog_keywords.extend(keywords)
        
        return {
            'company_name': company_name,
            'domain': domain,
            'total_urls': total_urls,
            'content_types': content_types,
            'blog_count': blog_count,
            'webinar_count': webinar_count,
            'resource_count': resource_count,
            'customer_story_count': customer_story_count,
            'stories_path_count': len(stories_df),
            'resources_path_count': len(resources_df),
            'webinar_path_count': len(webinar_df),
            'blog_path_count': len(blog_df),
            'stories_keywords': Counter(stories_keywords).most_common(20),
            'resources_keywords': Counter(resources_keywords).most_common(20),
            'webinar_keywords': Counter(webinar_keywords).most_common(20),
            'blog_keywords': Counter(blog_keywords).most_common(20),
            'stories_paths': stories_df['path_segments'].value_counts().head(15).to_dict() if 'path_segments' in stories_df.columns and len(stories_df) > 0 else {},
            'resources_paths': resources_df['path_segments'].value_counts().head(15).to_dict() if 'path_segments' in resources_df.columns and len(resources_df) > 0 else {},
            'webinar_paths': webinar_df['path_segments'].value_counts().head(15).to_dict() if 'path_segments' in webinar_df.columns and len(webinar_df) > 0 else {},
            'blog_paths': blog_df['path_segments'].value_counts().head(15).to_dict() if 'path_segments' in blog_df.columns and len(blog_df) > 0 else {},
        }
        
    except Exception as e:
        print(f'  ❌ 错误: {e}')
        import traceback
        traceback.print_exc()
        return None

def generate_report(data):
    """生成分析报告"""
    if not data:
        return None
    
    company_name = data['company_name']
    domain = data['domain']
    
    # 评估意识层级
    unaware_score = 0
    problem_aware_score = 0
    solution_aware_score = 0
    product_aware_score = 0
    most_aware_score = 0
    
    # Unaware层评估
    if data['blog_count'] > 100:
        unaware_score = 5
    elif data['blog_count'] > 50:
        unaware_score = 4
    elif data['blog_count'] > 10:
        unaware_score = 3
    elif data['blog_count'] > 0:
        unaware_score = 2
    else:
        unaware_score = 1
    
    # Solution Aware层评估
    if data['webinar_count'] > 100:
        solution_aware_score = 5
    elif data['webinar_count'] > 50:
        solution_aware_score = 4
    elif data['webinar_count'] > 10:
        solution_aware_score = 3
    elif data['webinar_count'] > 0:
        solution_aware_score = 2
    else:
        solution_aware_score = 1
    
    # Product Aware层评估
    product_pages = data['content_types'].get('product', 0)
    if product_pages > 1000:
        product_aware_score = 5
    elif product_pages > 500:
        product_aware_score = 4
    elif product_pages > 100:
        product_aware_score = 3
    elif product_pages > 10:
        product_aware_score = 2
    else:
        product_aware_score = 1
    
    # 总体评分
    total_score = (unaware_score + problem_aware_score + solution_aware_score + product_aware_score + most_aware_score) / 5
    
    # 生成报告
    report = f"""# {company_name} 内容营销策略深度分析

**分析日期**: {datetime.now().strftime('%Y-%m-%d')}  
**分析方式**: 数据统计分析  
**分析框架**: 《Breakthrough Advertising》意识层级理论 + Content Marketing Funnel (ACCL)

---

## 📋 执行摘要

{company_name} 的内容营销策略分析基于网站数据统计，展现了其在内容资产构建和营销漏斗设计方面的特点。

### 意识层级覆盖度评估

基于《Breakthrough Advertising》的5个意识层级，{company_name}的内容分布：

| 意识层级 | 内容类型 | 丰富度 | 评估 |
|---------|---------|--------|------|
| **Unaware（最不意识）** | Blog ({data['blog_count']}篇)、News & Media | {'⭐' * unaware_score} | {'优秀' if unaware_score >= 4 else '良好' if unaware_score >= 3 else '一般' if unaware_score >= 2 else '较少'} |
| **Problem Aware（问题意识）** | Industry Solutions、Problem-Solution Content | {'⭐' * problem_aware_score} | {'优秀' if problem_aware_score >= 4 else '良好' if problem_aware_score >= 3 else '一般' if problem_aware_score >= 2 else '较少'} |
| **Solution Aware（解决方案意识）** | Webinar ({data['webinar_count']}个)、Customer Stories ({data['customer_story_count']}个) | {'⭐' * solution_aware_score} | {'优秀' if solution_aware_score >= 4 else '良好' if solution_aware_score >= 3 else '一般' if solution_aware_score >= 2 else '较少'} |
| **Product Aware（产品意识）** | Product Pages ({data['content_types'].get('product', 0)}页)、Resources ({data['resource_count']}页) | {'⭐' * product_aware_score} | {'优秀' if product_aware_score >= 4 else '良好' if product_aware_score >= 3 else '一般' if product_aware_score >= 2 else '较少'} |
| **Most Aware（最意识）** | Contact Forms、Services | {'⭐' * most_aware_score} | {'优秀' if most_aware_score >= 4 else '良好' if most_aware_score >= 3 else '一般' if most_aware_score >= 2 else '较少'} |

**总体评分**: {'⭐' * int(total_score)} ({total_score:.1f}/5) - **内容营销策略分析**

---

## 🎯 内容营销架构分析

### 核心数据统计

- **总URL数**: {data['total_urls']:,}
- **Blog数量**: {data['blog_count']}
- **Webinar数量**: {data['webinar_count']}
- **Resources数量**: {data['resource_count']}
- **Customer Stories数量**: {data['customer_story_count']}

### 内容类型分布

| 内容类型 | 数量 | 占比 |
|---------|------|------|
"""
    
    # 添加内容类型分布
    total = sum(data['content_types'].values())
    for ct, count in list(data['content_types'].items())[:10]:
        percentage = (count / total * 100) if total > 0 else 0
        report += f"| {ct} | {count:,} | {percentage:.1f}% |\n"
    
    report += f"""
---

## 📊 内容营销资产分析

### 1. Blog 分析

**核心数据**：
- **总数**: {data['blog_count']}篇
- **路径数量**: {data['blog_path_count']}个

"""
    
    if data['blog_path_count'] > 0 and data['blog_paths']:
        report += "**主要路径分布（Top 10）**:\n\n"
        for i, (path, count) in enumerate(list(data['blog_paths'].items())[:10], 1):
            report += f"{i}. `{path}`: {count}\n"
        
        if data['blog_keywords']:
            report += "\n**关键词分布（Top 20）**:\n\n"
            report += "| 关键词 | 频次 |\n|--------|------|\n"
            for word, count in data['blog_keywords'][:20]:
                report += f"| {word} | {count} |\n"
    else:
        report += "⚠️ Blog内容较少或未找到相关路径\n"
    
    report += f"""
### 2. Webinar 分析

**核心数据**：
- **总数**: {data['webinar_count']}个
- **路径数量**: {data['webinar_path_count']}个

"""
    
    if data['webinar_path_count'] > 0 and data['webinar_paths']:
        report += "**主要路径分布（Top 10）**:\n\n"
        for i, (path, count) in enumerate(list(data['webinar_paths'].items())[:10], 1):
            report += f"{i}. `{path}`: {count}\n"
        
        if data['webinar_keywords']:
            report += "\n**关键词分布（Top 20）**:\n\n"
            report += "| 关键词 | 频次 |\n|--------|------|\n"
            for word, count in data['webinar_keywords'][:20]:
                report += f"| {word} | {count} |\n"
    else:
        report += "⚠️ Webinar内容较少或未找到相关路径\n"
    
    report += f"""
### 3. Resources 分析

**核心数据**：
- **总数**: {data['resource_count']}个
- **路径数量**: {data['resources_path_count']}个

"""
    
    if data['resources_path_count'] > 0 and data['resources_paths']:
        report += "**主要路径分布（Top 10）**:\n\n"
        for i, (path, count) in enumerate(list(data['resources_paths'].items())[:10], 1):
            report += f"{i}. `{path}`: {count}\n"
        
        if data['resources_keywords']:
            report += "\n**关键词分布（Top 20）**:\n\n"
            report += "| 关键词 | 频次 |\n|--------|------|\n"
            for word, count in data['resources_keywords'][:20]:
                report += f"| {word} | {count} |\n"
    else:
        report += "⚠️ Resources内容较少或未找到相关路径\n"
    
    report += f"""
### 4. Stories 分析

**核心数据**：
- **路径数量**: {data['stories_path_count']}个
- **Customer Stories数量**: {data['customer_story_count']}个

"""
    
    if data['stories_path_count'] > 0 and data['stories_paths']:
        report += "**主要路径分布（Top 10）**:\n\n"
        for i, (path, count) in enumerate(list(data['stories_paths'].items())[:10], 1):
            report += f"{i}. `{path}`: {count}\n"
        
        if data['stories_keywords']:
            report += "\n**关键词分布（Top 20）**:\n\n"
            report += "| 关键词 | 频次 |\n|--------|------|\n"
            for word, count in data['stories_keywords'][:20]:
                report += f"| {word} | {count} |\n"
    else:
        report += "⚠️ Stories内容较少或未找到相关路径\n"
    
    report += f"""
---

## 💡 关键发现与洞察

### 内容资产规模

- **总URL数**: {data['total_urls']:,}个
- **Blog**: {data['blog_count']}篇
- **Webinar**: {data['webinar_count']}个
- **Resources**: {data['resource_count']}个
- **Customer Stories**: {data['customer_story_count']}个

### 内容营销漏斗分布（基于ACCL模型）

| 漏斗阶段 | 内容类型 | 数量 | 占比 | 评估 |
|---------|---------|------|------|------|
| **Awareness（认知）** | Blog、News & Media | {data['blog_count']} | {(data['blog_count']/data['total_urls']*100) if data['total_urls'] > 0 else 0:.1f}% | {'⭐' * unaware_score} |
| **Consideration（考虑）** | Webinar、Customer Stories | {data['webinar_count'] + data['customer_story_count']} | {((data['webinar_count'] + data['customer_story_count'])/data['total_urls']*100) if data['total_urls'] > 0 else 0:.1f}% | {'⭐' * solution_aware_score} |
| **Conversion（转化）** | Product Pages、Contact Forms | {data['content_types'].get('product', 0)} | {(data['content_types'].get('product', 0)/data['total_urls']*100) if data['total_urls'] > 0 else 0:.1f}% | {'⭐' * product_aware_score} |
| **Loyalty（忠诚）** | Resources、Training | {data['resource_count']} | {(data['resource_count']/data['total_urls']*100) if data['total_urls'] > 0 else 0:.1f}% | {'⭐' * most_aware_score} |

---

## 📈 总结

### 核心优势

1. **内容资产规模**: {data['total_urls']:,}个URL
2. **Blog内容**: {data['blog_count']}篇
3. **Webinar内容**: {data['webinar_count']}个
4. **Resources内容**: {data['resource_count']}个

### 总体评分

**总体评分**: {'⭐' * int(total_score)} ({total_score:.1f}/5)

---

**分析完成时间**: {datetime.now().strftime('%Y-%m-%d')}  
**分析框架**: 《Breakthrough Advertising》意识层级理论 + Content Marketing Funnel (ACCL)
"""
    
    return report

def main():
    """主函数"""
    output_dir = Path('companyAnalysis')
    output_dir.mkdir(exist_ok=True)
    
    results = []
    
    for company_name, domain in COMPANIES.items():
        data = analyze_company(company_name, domain)
        if data:
            report = generate_report(data)
            if report:
                # 保存报告
                filename = f"{company_name.replace(' ', '_')}_内容营销策略深度分析.md"
                filepath = output_dir / filename
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f'  ✓ 报告已保存: {filepath}')
                results.append(company_name)
    
    print(f'\n{"="*60}')
    print(f'完成！共生成 {len(results)} 份报告')
    print(f'{"="*60}')

if __name__ == '__main__':
    main()


