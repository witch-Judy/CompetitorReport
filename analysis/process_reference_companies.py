#!/usr/bin/env python3
"""
批量处理参考公司的sitemap文件
按照SOP流程：raw_data -> output_data -> Information
"""

import sys
from pathlib import Path

# 添加analysis目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from sitemap_analyzer import SitemapAnalyzer
from batch_generate_cleaned_navigation_trees import CleanedNavigationTreeGenerator
from expand_sitemap_index import SitemapExpander


def process_reference_companies():
    """处理所有参考公司"""
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    raw_data_dir = project_root / "raw_data" / "reference"
    output_data_dir = project_root / "output_data" / "reference"
    information_dir = project_root / "Information" / "reference"
    
    # 创建输出目录
    output_data_dir.mkdir(parents=True, exist_ok=True)
    information_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print("处理参考公司Sitemap数据")
    print("=" * 80)
    print()
    print(f"原始数据: {raw_data_dir}")
    print(f"输出数据: {output_data_dir}")
    print(f"信息数据: {information_dir}")
    print()
    
    # 获取所有参考公司
    companies = []
    if raw_data_dir.exists():
        for company_dir in sorted(raw_data_dir.iterdir()):
            if company_dir.is_dir():
                xml_files = list(company_dir.glob("*.xml"))
                if xml_files:
                    companies.append(company_dir.name)
    
    if not companies:
        print("❌ 未找到任何参考公司的XML文件")
        return
    
    print(f"找到 {len(companies)} 个参考公司:")
    for company in companies:
        print(f"  - {company}")
    print()
    
    # 步骤0: 展开索引文件
    print("=" * 80)
    print("步骤0: 检查并展开sitemap索引文件")
    print("=" * 80)
    print()
    
    expander = SitemapExpander(timeout=30, delay=0.5)
    
    for company in companies:
        xml_file = raw_data_dir / company / f"{company}.xml"
        
        if not xml_file.exists():
            continue
        
        # 检查是否是索引文件
        if expander.is_sitemap_index(xml_file):
            print(f"展开 {company} 的索引文件...")
            try:
                expanded_file = expander.expand_sitemap(xml_file, max_sitemaps=50)
                if expanded_file != xml_file:
                    print(f"  ✅ 已展开: {expanded_file.name}")
                    # 替换原文件
                    xml_file.unlink()
                    expanded_file.rename(xml_file)
            except Exception as e:
                print(f"  ⚠️  展开失败: {e}")
            print()
    
    # 步骤1: 使用SitemapAnalyzer处理XML文件
    print("=" * 80)
    print("步骤1: 解析XML文件，生成CSV数据")
    print("=" * 80)
    print()
    
    analyzer = SitemapAnalyzer(output_dir=str(output_data_dir))
    
    processed_companies = []
    for company in companies:
        xml_file = raw_data_dir / company / f"{company}.xml"
        
        if not xml_file.exists():
            print(f"⚠️  {company}: XML文件不存在，跳过")
            continue
        
        print(f"处理 {company}...")
        try:
            output_file = output_data_dir / f"{company}_analyzed.csv"
            rows = analyzer.process_sitemap(str(xml_file), str(output_file))
            
            if rows:
                print(f"  ✅ 成功: {len(rows)} 个URL")
                processed_companies.append(company)
            else:
                print(f"  ⚠️  警告: 未提取到URL")
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            import traceback
            traceback.print_exc()
        print()
    
    print(f"步骤1完成: {len(processed_companies)}/{len(companies)} 个公司处理成功")
    print()
    
    # 步骤2: 生成导航树结构
    print("=" * 80)
    print("步骤2: 生成导航树结构")
    print("=" * 80)
    print()
    
    tree_generator = CleanedNavigationTreeGenerator(
        output_data_dir=str(output_data_dir),
        information_dir=str(information_dir)
    )
    
    tree_results = {}
    for company in processed_companies:
        print(f"生成 {company} 的导航树...")
        try:
            result = tree_generator.generate_cleaned_tree_for_company(company, verbose=False)
            if result:
                tree_results[company] = True
                print(f"  ✅ 成功")
            else:
                tree_results[company] = False
                print(f"  ⚠️  失败")
        except Exception as e:
            tree_results[company] = False
            print(f"  ❌ 错误: {e}")
            import traceback
            traceback.print_exc()
        print()
    
    print(f"步骤2完成: {sum(tree_results.values())}/{len(processed_companies)} 个公司生成成功")
    print()
    
    # 总结
    print("=" * 80)
    print("处理总结")
    print("=" * 80)
    print()
    print("成功处理的公司:")
    for company in processed_companies:
        csv_file = output_data_dir / f"{company}_analyzed.csv"
        tree_file = information_dir / f"{company}_analyzed_complete_tree.txt"
        
        csv_status = "✅" if csv_file.exists() else "❌"
        tree_status = "✅" if tree_file.exists() else "❌"
        
        print(f"  {company:15s} CSV: {csv_status}  Tree: {tree_status}")
    
    print()
    print(f"输出目录:")
    print(f"  - output_data/reference/")
    print(f"  - Information/reference/")


if __name__ == "__main__":
    process_reference_companies()

