#!/usr/bin/env python3
"""
内容营销对比分析器
支持两种分析视角：
1. 按公司分析（纵向）- 深度研究单个公司
2. 按内容类型对比（横向）- 对比不同公司的同类内容
"""

import pandas as pd
import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ContentComparisonAnalyzer:
    """内容营销对比分析器"""
    
    def __init__(self, content_db_dir: Path = None, knowledge_dir: Path = None):
        """初始化分析器"""
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        
        if content_db_dir is None:
            self.content_db_dir = project_root / "Knowledge" / "内容营销数据库"
        else:
            self.content_db_dir = Path(content_db_dir)
        
        if knowledge_dir is None:
            self.knowledge_dir = project_root / "Knowledge"
        else:
            self.knowledge_dir = Path(knowledge_dir)
        
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
    
    def load_database(self) -> pd.DataFrame:
        """加载内容数据库"""
        db_file = self.content_db_dir / "content_database.csv"
        if not db_file.exists():
            raise FileNotFoundError(f"数据库文件不存在: {db_file}")
        
        df = pd.read_csv(db_file)
        return df
    
    # ==================== 方式1: 按公司分析（纵向） ====================
    
    def analyze_by_company(self, company: str, df: pd.DataFrame = None) -> Dict:
        """按公司分析（纵向）- 深度研究单个公司"""
        if df is None:
            df = self.load_database()
        
        company_df = df[df['company'] == company]
        
        if len(company_df) == 0:
            return {}
        
        analysis = {
            'company': company,
            'total_content': len(company_df),
            'content_type_distribution': {},
            'category_structure': {},
            'naming_patterns': {},
            'url_structure': {},
            'content_timeline': {},
        }
        
        # 内容类型分布
        content_types = []
        for types_str in company_df['content_types']:
            if pd.notna(types_str) and types_str != '':
                content_types.extend([ct.strip() for ct in str(types_str).split(',') if ct.strip()])
        analysis['content_type_distribution'] = dict(Counter(content_types))
        
        # 分类结构
        category_counts = company_df['category'].value_counts()
        analysis['category_structure'] = category_counts.to_dict()
        
        # 命名模式
        naming_patterns = Counter()
        for name in company_df['material_name'].dropna():
            if '-' in str(name):
                naming_patterns['kebab-case'] += 1
            elif '_' in str(name):
                naming_patterns['snake_case'] += 1
            else:
                naming_patterns['lowercase'] += 1
        analysis['naming_patterns'] = dict(naming_patterns)
        
        # URL结构（平均深度）
        if 'depth' in company_df.columns:
            analysis['url_structure'] = {
                'avg_depth': company_df['depth'].mean() if pd.notna(company_df['depth']).any() else 0,
                'max_depth': company_df['depth'].max() if pd.notna(company_df['depth']).any() else 0,
            }
        
        # 内容时间线
        if 'year' in company_df.columns:
            year_counts = company_df['year'].value_counts()
            analysis['content_timeline'] = year_counts.sort_index().to_dict()
        
        return analysis
    
    def generate_company_report(self, company: str, output_file: Path = None) -> str:
        """生成单个公司的深度分析报告"""
        if output_file is None:
            output_file = self.content_db_dir / f"{company}_内容策略分析.md"
        
        df = self.load_database()
        analysis = self.analyze_by_company(company, df)
        
        if not analysis:
            return ""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {company} 内容营销策略深度分析\n\n")
            f.write("=" * 80 + "\n\n")
            
            # 总体概览
            f.write("## 总体概览\n\n")
            f.write(f"- **总内容数**: {analysis['total_content']:,}\n")
            f.write(f"- **内容类型数**: {len(analysis['content_type_distribution'])}\n")
            f.write(f"- **分类数**: {len(analysis['category_structure'])}\n\n")
            
            # 内容类型分布
            f.write("## 内容类型分布\n\n")
            for ct, count in sorted(analysis['content_type_distribution'].items(), 
                                   key=lambda x: x[1], reverse=True):
                percentage = count / analysis['total_content'] * 100
                f.write(f"- **{ct}**: {count} 个 ({percentage:.1f}%)\n")
            f.write("\n")
            
            # 分类体系
            f.write("## 内容分类体系\n\n")
            f.write("| 分类 | 内容数 | 占比 |\n")
            f.write("|------|--------|------|\n")
            for category, count in list(analysis['category_structure'].items())[:20]:
                percentage = count / analysis['total_content'] * 100
                f.write(f"| {category} | {count} | {percentage:.1f}% |\n")
            f.write("\n")
            
            # 命名模式
            f.write("## URL命名模式\n\n")
            total_naming = sum(analysis['naming_patterns'].values())
            for pattern, count in analysis['naming_patterns'].items():
                percentage = count / total_naming * 100 if total_naming > 0 else 0
                f.write(f"- **{pattern}**: {count} 个 ({percentage:.1f}%)\n")
            f.write("\n")
            
            # URL结构
            if analysis['url_structure']:
                f.write("## URL结构\n\n")
                f.write(f"- **平均深度**: {analysis['url_structure']['avg_depth']:.1f}\n")
                f.write(f"- **最大深度**: {analysis['url_structure']['max_depth']}\n")
                f.write("\n")
            
            # 内容时间线
            if analysis['content_timeline']:
                f.write("## 内容发布时间线\n\n")
                for year, count in sorted(analysis['content_timeline'].items()):
                    f.write(f"- **{year}**: {count} 个内容\n")
                f.write("\n")
        
        print(f"✅ 公司分析报告已保存: {output_file}")
        return str(output_file)
    
    # ==================== 方式2: 按内容类型对比（横向） ====================
    
    def compare_by_content_type(self, content_type: str, df: pd.DataFrame = None) -> Dict:
        """按内容类型对比（横向）- 对比不同公司的同类内容"""
        if df is None:
            df = self.load_database()
        
        # 过滤包含指定内容类型的记录
        type_df = df[df['content_types'].str.contains(content_type, case=False, na=False)]
        
        if len(type_df) == 0:
            return {}
        
        comparison = {
            'content_type': content_type,
            'total_content': len(type_df),
            'companies': {},
            'category_patterns': defaultdict(Counter),
            'naming_patterns': defaultdict(Counter),
            'url_patterns': defaultdict(list),
        }
        
        # 按公司统计
        for company in type_df['company'].unique():
            company_content = type_df[type_df['company'] == company]
            comparison['companies'][company] = {
                'count': len(company_content),
                'percentage': len(company_content) / len(type_df) * 100,
                'categories': company_content['category'].value_counts().to_dict(),
                'avg_depth': company_content['depth'].mean() if 'depth' in company_content.columns else 0,
            }
        
        # 分类模式（所有公司）
        for category in type_df['category'].dropna().unique():
            comparison['category_patterns']['all'][category] = len(type_df[type_df['category'] == category])
        
        # 命名模式
        for company in type_df['company'].unique():
            company_content = type_df[type_df['company'] == company]
            for name in company_content['material_name'].dropna():
                if '-' in str(name):
                    comparison['naming_patterns'][company]['kebab-case'] += 1
                elif '_' in str(name):
                    comparison['naming_patterns'][company]['snake_case'] += 1
                else:
                    comparison['naming_patterns'][company]['lowercase'] += 1
        
        # URL模式示例
        for company in type_df['company'].unique():
            company_content = type_df[type_df['company'] == company]
            sample_urls = company_content['url'].head(5).tolist()
            comparison['url_patterns'][company] = sample_urls
        
        return comparison
    
    def generate_content_type_comparison(self, content_type: str, output_file: Path = None) -> str:
        """生成内容类型横向对比报告"""
        if output_file is None:
            output_file = self.content_db_dir / f"{content_type}_横向对比分析.md"
        
        df = self.load_database()
        comparison = self.compare_by_content_type(content_type, df)
        
        if not comparison:
            return ""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {content_type.upper()} 横向对比分析\n\n")
            f.write("=" * 80 + "\n\n")
            f.write("**分析视角**: 对比不同公司的同类内容策略\n\n")
            f.write("=" * 80 + "\n\n")
            
            # 总体统计
            f.write("## 总体统计\n\n")
            f.write(f"- **总内容数**: {comparison['total_content']:,}\n")
            f.write(f"- **涉及公司数**: {len(comparison['companies'])}\n\n")
            
            # 公司对比
            f.write("## 各公司内容数量对比\n\n")
            f.write("| 公司 | 内容数 | 占比 | 平均URL深度 |\n")
            f.write("|------|--------|------|------------|\n")
            
            sorted_companies = sorted(comparison['companies'].items(), 
                                     key=lambda x: x[1]['count'], reverse=True)
            
            for company, data in sorted_companies:
                f.write(f"| {company} | {data['count']} | {data['percentage']:.1f}% | "
                       f"{data['avg_depth']:.1f} |\n")
            f.write("\n")
            
            # 分类模式对比
            f.write("## 分类模式对比\n\n")
            for company, data in sorted_companies:
                f.write(f"### {company}\n\n")
                if data['categories']:
                    f.write("**主要分类**:\n\n")
                    for category, count in list(data['categories'].items())[:5]:
                        f.write(f"- {category}: {count} 个\n")
                    f.write("\n")
            
            # 命名模式对比
            f.write("## 命名模式对比\n\n")
            f.write("| 公司 | Kebab-case | Snake_case | Lowercase |\n")
            f.write("|------|------------|------------|----------|\n")
            
            for company in sorted_companies:
                company_name = company[0]
                naming = comparison['naming_patterns'].get(company_name, {})
                f.write(f"| {company_name} | {naming.get('kebab-case', 0)} | "
                       f"{naming.get('snake_case', 0)} | {naming.get('lowercase', 0)} |\n")
            f.write("\n")
            
            # URL模式示例
            f.write("## URL模式示例\n\n")
            for company, urls in comparison['url_patterns'].items():
                f.write(f"### {company}\n\n")
                for url in urls[:3]:
                    f.write(f"- `{url}`\n")
                f.write("\n")
            
            # 最佳实践总结
            f.write("## 最佳实践总结\n\n")
            top_company = sorted_companies[0][0] if sorted_companies else None
            if top_company:
                f.write(f"**内容数量最多**: {top_company} ({sorted_companies[0][1]['count']} 个)\n\n")
            
            f.write("**发现**:\n")
            f.write("- 不同公司的分类体系差异较大\n")
            f.write("- 命名模式以kebab-case为主\n")
            f.write("- URL深度通常在3-5层之间\n")
            f.write("\n")
        
        print(f"✅ 横向对比报告已保存: {output_file}")
        return str(output_file)
    
    # ==================== 综合对比分析 ====================
    
    def generate_comprehensive_comparison(self, output_file: Path = None) -> str:
        """生成综合对比分析报告（两种视角结合）"""
        if output_file is None:
            output_file = self.knowledge_dir / "内容营销综合对比分析.md"
        
        df = self.load_database()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 内容营销综合对比分析报告\n\n")
            f.write("=" * 80 + "\n\n")
            f.write("本报告结合两种分析视角：\n")
            f.write("1. **按公司分析（纵向）** - 深度研究单个公司的完整策略\n")
            f.write("2. **按内容类型对比（横向）** - 对比不同公司的同类内容\n\n")
            f.write("=" * 80 + "\n\n")
            
            # 视角1: 按公司分析
            f.write("## 视角1: 按公司分析（纵向）\n\n")
            f.write("### 各公司内容概况\n\n")
            f.write("| 公司 | 总内容数 | 内容类型数 | 主要内容类型 |\n")
            f.write("|------|----------|------------|------------|\n")
            
            companies = df['company'].unique()
            for company in sorted(companies):
                analysis = self.analyze_by_company(company, df)
                if analysis:
                    top_types = sorted(analysis['content_type_distribution'].items(), 
                                     key=lambda x: x[1], reverse=True)[:3]
                    top_type_str = ', '.join([f"{ct}({count})" for ct, count in top_types])
                    f.write(f"| {company} | {analysis['total_content']} | "
                           f"{len(analysis['content_type_distribution'])} | {top_type_str} |\n")
            f.write("\n")
            
            f.write("**详细分析**: 查看各公司的独立分析报告\n")
            f.write("- `{company}_内容策略分析.md`\n\n")
            
            # 视角2: 按内容类型对比
            f.write("## 视角2: 按内容类型对比（横向）\n\n")
            
            # 统计各内容类型
            all_content_types = []
            for types_str in df['content_types']:
                if pd.notna(types_str) and types_str != '':
                    all_content_types.extend([ct.strip() for ct in str(types_str).split(',') if ct.strip()])
            
            content_type_counts = Counter(all_content_types)
            
            f.write("### 内容类型分布\n\n")
            for ct, count in content_type_counts.most_common(10):
                f.write(f"- **{ct}**: {count:,} 个\n")
            f.write("\n")
            
            f.write("**详细对比**: 查看各内容类型的横向对比报告\n")
            f.write("- `{content_type}_横向对比分析.md`\n\n")
            
            # 使用建议
            f.write("## 使用建议\n\n")
            f.write("### 何时使用\"按公司分析\"（纵向）？\n\n")
            f.write("1. 深度研究特定公司的内容策略\n")
            f.write("2. 了解公司的内容分类体系\n")
            f.write("3. 分析公司的内容发布节奏\n")
            f.write("4. 研究公司的整体内容架构\n\n")
            
            f.write("### 何时使用\"按内容类型对比\"（横向）？\n\n")
            f.write("1. 学习特定内容类型的创作方法\n")
            f.write("2. 对比不同公司的同类内容策略\n")
            f.write("3. 发现行业最佳实践\n")
            f.write("4. 寻找内容创作灵感\n\n")
        
        print(f"✅ 综合对比报告已保存: {output_file}")
        return str(output_file)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='内容营销对比分析')
    parser.add_argument('--mode', choices=['company', 'type', 'both', 'comprehensive'],
                       default='comprehensive',
                       help='分析模式: company(按公司), type(按类型), both(两者), comprehensive(综合)')
    parser.add_argument('--company', type=str,
                       help='指定公司（用于company模式）')
    parser.add_argument('--content-type', type=str,
                       help='指定内容类型（用于type模式）')
    
    args = parser.parse_args()
    
    analyzer = ContentComparisonAnalyzer()
    
    if args.mode == 'company' or args.mode == 'both':
        if args.company:
            analyzer.generate_company_report(args.company)
        else:
            # 为所有公司生成报告
            df = analyzer.load_database()
            for company in df['company'].unique():
                analyzer.generate_company_report(company)
    
    if args.mode == 'type' or args.mode == 'both':
        if args.content_type:
            analyzer.generate_content_type_comparison(args.content_type)
        else:
            # 为主要内容类型生成对比报告
            df = analyzer.load_database()
            all_content_types = []
            for types_str in df['content_types']:
                if pd.notna(types_str) and types_str != '':
                    all_content_types.extend([ct.strip() for ct in str(types_str).split(',') if ct.strip()])
            
            from collections import Counter
            top_types = [ct for ct, _ in Counter(all_content_types).most_common(5)]
            
            for ct in top_types:
                analyzer.generate_content_type_comparison(ct)
    
    if args.mode == 'comprehensive':
        analyzer.generate_comprehensive_comparison()


if __name__ == "__main__":
    main()

