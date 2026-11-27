#!/usr/bin/env python3
"""
内容营销分析器
分析竞品的内容营销策略、材料分类、内容结构等
"""

import pandas as pd
import re
import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Optional
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import time


class ContentMarketingAnalyzer:
    """内容营销分析器"""
    
    def __init__(self, output_data_dir: Path = None, knowledge_dir: Path = None):
        """初始化分析器"""
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        
        if output_data_dir is None:
            self.output_data_dir = project_root / "output_data"
        else:
            self.output_data_dir = Path(output_data_dir)
        
        if knowledge_dir is None:
            self.knowledge_dir = project_root / "Knowledge"
        else:
            self.knowledge_dir = Path(knowledge_dir)
        
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        
        # 内容类型关键词映射
        self.content_keywords = {
            'whitepaper': ['whitepaper', 'white-paper', 'white_paper', 'wp-', '/wp/', 'whitepapers'],
            'case_study': ['case-study', 'case_study', 'casestudy', 'customer-story', 'customer_story', 'success-story'],
            'webinar': ['webinar', 'webinars', 'on-demand', 'on_demand'],
            'blog': ['blog', 'blogs', 'article', 'articles', 'post', 'posts'],
            'ebook': ['ebook', 'e-book', 'e_book', 'guide', 'guides'],
            'datasheet': ['datasheet', 'data-sheet', 'data_sheet', 'specification', 'spec'],
            'video': ['video', 'videos', 'watch', 'youtube'],
            'podcast': ['podcast', 'podcasts'],
            'infographic': ['infographic', 'infographics'],
            'report': ['report', 'reports', 'research', 'study', 'analysis'],
            'demo': ['demo', 'demos', 'trial', 'try'],
            'webinar': ['webinar', 'webinars'],
            'newsletter': ['newsletter', 'newsletters'],
            'press_release': ['press-release', 'press_release', 'press', 'newsroom', 'news'],
        }
    
    def detect_content_type_from_url(self, url: str) -> List[str]:
        """从URL中检测内容类型"""
        if pd.isna(url) or not isinstance(url, str):
            return []
        
        url_lower = url.lower()
        detected_types = []
        
        for content_type, keywords in self.content_keywords.items():
            for keyword in keywords:
                if keyword in url_lower:
                    detected_types.append(content_type)
                    break
        
        return detected_types
    
    def extract_content_structure(self, url: str) -> Dict:
        """提取内容结构信息"""
        parsed = urlparse(url)
        path_segments = [seg for seg in parsed.path.split('/') if seg]
        
        structure = {
            'url': url,
            'domain': parsed.netloc,
            'path_segments': path_segments,
            'depth': len(path_segments),
            'content_types': self.detect_content_type_from_url(url),
            'category': None,
            'subcategory': None,
            'material_name': None,
        }
        
        # 尝试识别分类层级
        if len(path_segments) >= 2:
            structure['category'] = path_segments[0] if path_segments[0] else None
            structure['subcategory'] = path_segments[1] if len(path_segments) > 1 else None
        
        # 提取材料名称（通常是最后一个segment）
        if path_segments:
            structure['material_name'] = path_segments[-1]
        
        return structure
    
    def analyze_company_content_strategy(self, company_name: str) -> Dict:
        """分析单个公司的内容营销策略"""
        print(f"分析: {company_name}")
        
        csv_file = self.output_data_dir / f"{company_name}_analyzed.csv"
        if not csv_file.exists():
            print(f"  ❌ 文件不存在: {csv_file}")
            return {}
        
        df = pd.read_csv(csv_file)
        
        # 分析内容类型分布
        content_analysis = {
            'company': company_name,
            'total_urls': len(df),
            'content_types': {},
            'content_structures': [],
            'category_hierarchy': defaultdict(int),
            'material_naming_patterns': defaultdict(int),
        }
        
        # 分析每个URL
        for _, row in df.iterrows():
            url = row.get('url', '')
            if pd.isna(url):
                continue
            
            structure = self.extract_content_structure(url)
            content_analysis['content_structures'].append(structure)
            
            # 统计内容类型
            detected_types = structure['content_types']
            if detected_types:
                for ct in detected_types:
                    content_analysis['content_types'][ct] = content_analysis['content_types'].get(ct, 0) + 1
            else:
                # 使用已有的content_type
                existing_type = row.get('content_type', 'other')
                content_analysis['content_types'][existing_type] = content_analysis['content_types'].get(existing_type, 0) + 1
            
            # 统计分类层级
            if structure['category']:
                content_analysis['category_hierarchy'][structure['category']] += 1
            
            # 分析命名模式
            if structure['material_name']:
                # 提取命名模式（如：kebab-case, snake_case, camelCase等）
                name = structure['material_name']
                if '-' in name:
                    content_analysis['material_naming_patterns']['kebab-case'] += 1
                elif '_' in name:
                    content_analysis['material_naming_patterns']['snake_case'] += 1
                elif any(c.isupper() for c in name[1:]):
                    content_analysis['material_naming_patterns']['camelCase'] += 1
                else:
                    content_analysis['material_naming_patterns']['lowercase'] += 1
        
        print(f"  ✅ 分析完成: {len(content_analysis['content_structures'])} 个URL")
        return content_analysis
    
    def build_content_database(self, companies: List[str] = None) -> pd.DataFrame:
        """构建内容营销数据库"""
        print("=" * 80)
        print("构建内容营销数据库")
        print("=" * 80)
        print()
        
        if companies is None:
            # 自动发现所有公司
            csv_files = sorted(self.output_data_dir.glob("*_analyzed.csv"))
            companies = [f.stem.replace('_analyzed', '') for f in csv_files]
        
        all_content_data = []
        
        for company in companies:
            analysis = self.analyze_company_content_strategy(company)
            
            if not analysis:
                continue
            
            # 将结构数据扁平化
            for structure in analysis['content_structures']:
                row = {
                    'company': company,
                    'url': structure['url'],
                    'domain': structure['domain'],
                    'content_types': ','.join(structure['content_types']) if structure['content_types'] else 'other',
                    'category': structure['category'],
                    'subcategory': structure['subcategory'],
                    'material_name': structure['material_name'],
                    'path_depth': structure['depth'],
                }
                all_content_data.append(row)
        
        df = pd.DataFrame(all_content_data)
        
        # 保存数据库
        db_file = self.knowledge_dir / "content_marketing_database.csv"
        df.to_csv(db_file, index=False, encoding='utf-8')
        print(f"\n✅ 内容营销数据库已保存: {db_file}")
        print(f"   总记录数: {len(df):,}")
        
        return df
    
    def analyze_content_categories(self, df: pd.DataFrame) -> Dict:
        """分析内容分类体系"""
        print("\n" + "=" * 80)
        print("分析内容分类体系")
        print("=" * 80)
        print()
        
        analysis = {
            'category_distribution': {},
            'content_type_by_category': defaultdict(lambda: defaultdict(int)),
            'naming_conventions': {},
        }
        
        # 按公司分析
        for company in df['company'].unique():
            company_df = df[df['company'] == company]
            
            # 分类分布
            category_counts = company_df['category'].value_counts()
            analysis['category_distribution'][company] = category_counts.to_dict()
            
            # 内容类型在分类中的分布
            for _, row in company_df.iterrows():
                category = row['category'] or 'root'
                content_types = row['content_types'].split(',')
                for ct in content_types:
                    analysis['content_type_by_category'][company][f"{category}:{ct}"] += 1
        
        return analysis
    
    def generate_content_strategy_report(self, df: pd.DataFrame) -> str:
        """生成内容营销策略报告"""
        report_file = self.knowledge_dir / "内容营销策略分析报告.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 竞品内容营销策略分析报告\n\n")
            f.write("=" * 80 + "\n\n")
            
            # 总体统计
            f.write("## 总体统计\n\n")
            f.write(f"- **总URL数**: {len(df):,}\n")
            f.write(f"- **公司数**: {len(df['company'].unique())}\n")
            f.write(f"- **内容类型数**: {len(df['content_types'].unique())}\n\n")
            
            # 按公司分析
            f.write("## 按公司分析\n\n")
            
            for company in sorted(df['company'].unique()):
                company_df = df[df['company'] == company]
                
                f.write(f"### {company}\n\n")
                f.write(f"- **总URL数**: {len(company_df):,}\n")
                
                # 内容类型分布
                content_type_counts = Counter()
                for types_str in company_df['content_types']:
                    for ct in types_str.split(','):
                        content_type_counts[ct] += 1
                
                f.write("\n**内容类型分布**:\n\n")
                for ct, count in content_type_counts.most_common(10):
                    f.write(f"- {ct}: {count}\n")
                
                # 分类体系
                category_counts = company_df['category'].value_counts()
                f.write("\n**分类体系** (Top 10):\n\n")
                for category, count in category_counts.head(10).items():
                    if pd.notna(category):
                        f.write(f"- {category}: {count}\n")
                
                f.write("\n")
            
            # 内容类型对比
            f.write("## 内容类型对比\n\n")
            f.write("| 公司 | Whitepaper | Case Study | Webinar | Blog | Ebook | Datasheet |\n")
            f.write("|------|------------|------------|---------|------|-------|----------|\n")
            
            for company in sorted(df['company'].unique()):
                company_df = df[df['company'] == company]
                content_type_counts = Counter()
                for types_str in company_df['content_types']:
                    for ct in types_str.split(','):
                        content_type_counts[ct] += 1
                
                f.write(f"| {company} | "
                       f"{content_type_counts.get('whitepaper', 0)} | "
                       f"{content_type_counts.get('case_study', 0)} | "
                       f"{content_type_counts.get('webinar', 0)} | "
                       f"{content_type_counts.get('blog', 0)} | "
                       f"{content_type_counts.get('ebook', 0)} | "
                       f"{content_type_counts.get('datasheet', 0)} |\n")
            
            f.write("\n")
        
        print(f"✅ 内容营销策略报告已保存: {report_file}")
        return str(report_file)


def main():
    """主函数"""
    analyzer = ContentMarketingAnalyzer()
    
    # 构建数据库
    df = analyzer.build_content_database()
    
    # 生成报告
    analyzer.generate_content_strategy_report(df)
    
    print("\n" + "=" * 80)
    print("✅ 内容营销分析完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()



