#!/usr/bin/env python3
"""
生成参考公司的综合内容类型统计表
严格按照与竞品公司相同的分析模式
"""

import pandas as pd
import re
from pathlib import Path
from collections import Counter
import sys

sys.path.insert(0, str(Path(__file__).parent))


def classify_content_type(path: str) -> str:
    """分类内容类型（与竞品公司使用相同的逻辑）"""
    path_lower = path.lower()
    
    # 产品相关
    if any(keyword in path_lower for keyword in ['product', 'products', 'solutions', 'platform', 'software', 'hardware']):
        return 'product'
    
    # 公司信息
    if any(keyword in path_lower for keyword in ['company', 'about', 'team', 'careers', 'career', 'jobs']):
        return 'company'
    
    # 行业相关
    if any(keyword in path_lower for keyword in ['industry', 'industries', 'sector', 'verticals', 'use-case', 'usecase']):
        return 'industry'
    
    # 博客
    if any(keyword in path_lower for keyword in ['blog', 'news', 'article', 'post', 'insights', 'thought-leadership']):
        return 'blog'
    
    # Webinar
    if any(keyword in path_lower for keyword in ['webinar', 'webinars', 'event', 'events', 'workshop', 'workshops']):
        return 'webinar'
    
    # 资源
    if any(keyword in path_lower for keyword in ['resource', 'resources', 'whitepaper', 'whitepapers', 'ebook', 'ebooks', 
                                                 'guide', 'guides', 'case-study', 'case-studies', 'report', 'reports',
                                                 'download', 'downloads', 'library', 'documentation', 'docs']):
        return 'resource'
    
    # 客户案例
    if any(keyword in path_lower for keyword in ['customer', 'customers', 'client', 'clients', 'success-story', 
                                                 'success-stories', 'testimonial', 'testimonials']):
        return 'customer_story'
    
    # 新闻室
    if any(keyword in path_lower for keyword in ['newsroom', 'press', 'press-release', 'press-releases', 'media', 'announcement']):
        return 'newsroom'
    
    # 法律/政策
    if any(keyword in path_lower for keyword in ['legal', 'privacy', 'terms', 'policy', 'policies', 'cookie', 'gdpr', 'compliance']):
        return 'legal'
    
    # 首页
    if path_lower in ['/', '/en', '/en/', '/zh', '/zh/', '/zh-cn', '/zh-cn/'] or path_lower.count('/') <= 1:
        return 'home'
    
    return 'other'


def analyze_reference_companies():
    """分析参考公司的内容类型"""
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    output_data_dir = project_root / "output_data" / "reference"
    insight_dir = project_root / "insight"
    information_reference_dir = project_root / "Information" / "reference"
    
    # 确保目录存在
    insight_dir.mkdir(parents=True, exist_ok=True)
    information_reference_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取所有参考公司的CSV文件
    csv_files = sorted(output_data_dir.glob("*_analyzed.csv"))
    
    if not csv_files:
        print("❌ 未找到参考公司的CSV文件")
        return
    
    print("=" * 80)
    print("生成参考公司综合内容类型统计表")
    print("=" * 80)
    print()
    print(f"找到 {len(csv_files)} 个参考公司")
    print()
    
    # 统计每个公司的内容类型
    results = []
    
    for csv_file in csv_files:
        company_name = csv_file.stem.replace('_analyzed', '')
        print(f"分析 {company_name}...")
        
        try:
            df = pd.read_csv(csv_file)
            
            # 统计各内容类型
            # 优先使用CSV中的content_type列（如果存在），否则通过路径分析
            if 'content_type' in df.columns:
                content_type_counts = df['content_type'].value_counts().to_dict()
            else:
                content_type_counts = Counter()
                for _, row in df.iterrows():
                    path = str(row.get('path', ''))
                    content_type = classify_content_type(path)
                    content_type_counts[content_type] += 1
            
            # 计算总数
            total_urls = len(df)
            
            # 构建结果行
            result_row = {
                '公司': company_name,
                '总内容数': total_urls,
                'product': content_type_counts.get('product', 0),
                'company': content_type_counts.get('company', 0),
                'industry': content_type_counts.get('industry', 0),
                'blog': content_type_counts.get('blog', 0),
                'webinar': content_type_counts.get('webinar', 0),
                'resource': content_type_counts.get('resource', 0),
                'customer_story': content_type_counts.get('customer_story', 0),
                'newsroom': content_type_counts.get('newsroom', 0),
                'legal': content_type_counts.get('legal', 0),
                'other': content_type_counts.get('other', 0),
                'home': content_type_counts.get('home', 0),
            }
            
            results.append(result_row)
            print(f"  ✅ {total_urls:,} 个URL")
            
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            import traceback
            traceback.print_exc()
    
    if not results:
        print("❌ 没有成功分析任何公司")
        return
    
    # 创建DataFrame
    df_results = pd.DataFrame(results)
    
    # 保存CSV
    csv_output = insight_dir / "参考公司综合内容类型统计表.csv"
    df_results.to_csv(csv_output, index=False, encoding='utf-8-sig')
    print()
    print(f"✅ CSV已保存: {csv_output}")
    
    # 同时保存到Information/reference目录
    csv_output_ref = information_reference_dir / "参考公司综合内容类型统计表.csv"
    df_results.to_csv(csv_output_ref, index=False, encoding='utf-8-sig')
    print(f"✅ CSV已保存: {csv_output_ref}")
    
    # 生成Markdown报告
    md_output = insight_dir / "参考公司综合内容类型统计表.md"
    generate_markdown_report(df_results, md_output)
    print(f"✅ Markdown报告已保存: {md_output}")
    
    # 同时保存到Information/reference目录
    md_output_ref = information_reference_dir / "参考公司综合内容类型统计表.md"
    generate_markdown_report(df_results, md_output_ref)
    print(f"✅ Markdown报告已保存: {md_output_ref}")
    
    print()
    print("=" * 80)
    print("统计完成")
    print("=" * 80)
    print()
    print("关键发现:")
    print(f"  • 总公司数: {len(results)}")
    print(f"  • 总URL数: {df_results['总内容数'].sum():,}")
    print(f"  • 平均每公司URL数: {df_results['总内容数'].mean():.0f}")
    print()


def generate_markdown_report(df: pd.DataFrame, output_file: Path):
    """生成Markdown格式的统计报告"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 参考公司综合内容类型统计表\n\n")
        f.write("=" * 80 + "\n\n")
        f.write("**说明**: 本统计表包含参考公司的内容类型分布，这些公司来自不同行业（包括消费品行业），\n")
        f.write("虽然与主要竞品公司行业不同，但具有重要的参考价值。\n\n")
        f.write("=" * 80 + "\n\n")
        
        # 统计表
        f.write("## 内容类型统计表\n\n")
        f.write("| 公司 | 总内容数 | product | company | industry | blog | webinar | resource | customer_story | newsroom | legal | other | home |\n")
        f.write("|------|----------|---------|---------|----------|------|---------|----------|---------------|----------|-------|-------|------|\n")
        
        for _, row in df.iterrows():
            company = row['公司']
            total = int(row['总内容数'])
            product = int(row['product']) if pd.notna(row['product']) else 0
            company_ct = int(row['company']) if pd.notna(row['company']) else 0
            industry = int(row['industry']) if pd.notna(row['industry']) else 0
            blog = int(row['blog']) if pd.notna(row['blog']) else 0
            webinar = int(row['webinar']) if pd.notna(row['webinar']) else 0
            resource = int(row['resource']) if pd.notna(row['resource']) else 0
            customer_story = int(row['customer_story']) if pd.notna(row['customer_story']) else 0
            newsroom = int(row['newsroom']) if pd.notna(row['newsroom']) else 0
            legal = int(row['legal']) if pd.notna(row['legal']) else 0
            other = int(row['other']) if pd.notna(row['other']) else 0
            home = int(row['home']) if pd.notna(row['home']) else 0
            
            f.write(f"| {company} | {total:,} | {product:,} | {company_ct:,} | {industry:,} | {blog:,} | {webinar:,} | {resource:,} | {customer_story:,} | {newsroom:,} | {legal:,} | {other:,} | {home:,} |\n")
        
        f.write("\n")
        
        # 关键发现
        f.write("## 关键发现\n\n")
        
        # Top公司
        f.write("### Top 3 公司（按总内容数）\n\n")
        df_sorted = df.sort_values('总内容数', ascending=False)
        for i, (_, row) in enumerate(df_sorted.head(3).iterrows(), 1):
            f.write(f"{i}. **{row['公司']}**: {int(row['总内容数']):,} 个URL\n")
        f.write("\n")
        
        # 各内容类型Top 3
        f.write("### 各内容类型Top 3\n\n")
        content_types = ['product', 'company', 'industry', 'blog', 'webinar', 'resource', 'customer_story', 'newsroom']
        for ct in content_types:
            if ct in df.columns:
                top3 = df.nlargest(3, ct)
                f.write(f"**{ct}**:\n")
                for i, (_, row) in enumerate(top3.iterrows(), 1):
                    count = int(row[ct]) if pd.notna(row[ct]) and row[ct] > 0 else 0
                    if count > 0:
                        f.write(f"  {i}. {row['公司']}: {count:,} 个\n")
                f.write("\n")
        
        # 行业特点分析
        f.write("## 行业特点分析\n\n")
        f.write("参考公司来自不同行业，包括：\n\n")
        f.write("- **科技/软件**: Stripe, Samsara, Palantir\n")
        f.write("- **消费电子**: Apple, Xiaomi\n")
        f.write("- **新能源汽车**: BYD\n\n")
        f.write("这些公司的内容策略与工业自动化竞品公司有所不同，但提供了宝贵的参考：\n\n")
        f.write("1. **消费品行业**更注重产品展示和用户体验\n")
        f.write("2. **科技公司**更注重技术文档和开发者资源\n")
        f.write("3. **不同行业**的内容组织方式各有特色\n\n")
        
        f.write("=" * 80 + "\n")


if __name__ == "__main__":
    analyze_reference_companies()

