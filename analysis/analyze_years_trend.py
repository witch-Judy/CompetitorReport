#!/usr/bin/env python3
"""
年份趋势分析
分析各竞品的内容发布年份分布和趋势
"""

import pandas as pd
import os
import sys
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class YearsTrendAnalyzer:
    """年份趋势分析器"""
    
    def __init__(self, output_data_dir: str = None, knowledge_dir: str = None):
        """
        初始化分析器
        
        Args:
            output_data_dir: output_data目录路径
            knowledge_dir: Knowledge目录路径
        """
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
    
    def analyze_all_companies(self) -> pd.DataFrame:
        """分析所有公司的年份分布"""
        print("=" * 80)
        print("年份趋势分析")
        print("=" * 80)
        print()
        
        results = []
        
        csv_files = sorted(self.output_data_dir.glob("*_analyzed.csv"))
        
        for csv_file in csv_files:
            company_name = csv_file.stem.replace('_analyzed', '')
            print(f"分析: {company_name}")
            
            try:
                df = pd.read_csv(csv_file)
                
                # 检查是否有year列
                if 'year' not in df.columns:
                    print(f"  ⚠️  缺少year列，跳过")
                    results.append({
                        'company': company_name,
                        'total_urls': len(df),
                        'has_year_data': False,
                        'year_data_ratio': 0.0,
                        'years_count': 0,
                        'earliest_year': None,
                        'latest_year': None,
                        'most_active_year': None,
                        'most_active_year_count': 0
                    })
                    continue
                
                # 统计年份分布
                year_counts = df['year'].value_counts()
                valid_years = df['year'].dropna()
                
                has_year_data = len(valid_years) > 0
                year_data_ratio = len(valid_years) / len(df) * 100 if len(df) > 0 else 0
                
                if has_year_data:
                    # 转换为数值类型以便排序
                    valid_years_numeric = pd.to_numeric(valid_years, errors='coerce').dropna()
                    
                    if len(valid_years_numeric) > 0:
                        earliest_year = int(valid_years_numeric.min())
                        latest_year = int(valid_years_numeric.max())
                        most_active_year = int(year_counts.index[0])
                        most_active_year_count = int(year_counts.iloc[0])
                    else:
                        earliest_year = None
                        latest_year = None
                        most_active_year = None
                        most_active_year_count = 0
                else:
                    earliest_year = None
                    latest_year = None
                    most_active_year = None
                    most_active_year_count = 0
                
                results.append({
                    'company': company_name,
                    'total_urls': len(df),
                    'has_year_data': has_year_data,
                    'year_data_ratio': round(year_data_ratio, 1),
                    'years_count': len(year_counts),
                    'earliest_year': earliest_year,
                    'latest_year': latest_year,
                    'most_active_year': most_active_year,
                    'most_active_year_count': most_active_year_count
                })
                
                if has_year_data:
                    print(f"  ✅ 有年份数据: {len(valid_years)}/{len(df)} ({year_data_ratio:.1f}%)")
                    print(f"     年份范围: {earliest_year} - {latest_year}")
                    print(f"     最活跃年份: {most_active_year} ({most_active_year_count}个URL)")
                    print(f"     年份分布: {dict(year_counts.head(5))}")
                else:
                    print(f"  ❌ 无年份数据")
                print()
                
            except Exception as e:
                print(f"  ❌ 分析出错: {e}")
                print()
        
        return pd.DataFrame(results)
    
    def generate_detailed_year_analysis(self) -> dict:
        """生成详细的年份分析报告"""
        print("=" * 80)
        print("生成详细年份分析")
        print("=" * 80)
        print()
        
        csv_files = sorted(self.output_data_dir.glob("*_analyzed.csv"))
        
        detailed_results = {}
        
        for csv_file in csv_files:
            company_name = csv_file.stem.replace('_analyzed', '')
            
            try:
                df = pd.read_csv(csv_file)
                
                if 'year' not in df.columns:
                    continue
                
                # 年份分布
                year_counts = df['year'].value_counts().sort_index()
                
                # 按内容类型统计年份
                content_type_by_year = {}
                if 'content_type' in df.columns:
                    for year in df['year'].dropna().unique():
                        year_df = df[df['year'] == year]
                        content_type_by_year[str(year)] = year_df['content_type'].value_counts().to_dict()
                
                # 按行业统计年份（如果有）
                industry_by_year = {}
                if 'is_industry' in df.columns:
                    for year in df['year'].dropna().unique():
                        year_df = df[df['year'] == year]
                        industry_count = year_df['is_industry'].sum()
                        industry_by_year[str(year)] = int(industry_count)
                
                detailed_results[company_name] = {
                    'year_distribution': year_counts.to_dict(),
                    'content_type_by_year': content_type_by_year,
                    'industry_by_year': industry_by_year,
                    'total_with_year': len(df[df['year'].notna()]),
                    'total_urls': len(df)
                }
                
            except Exception as e:
                print(f"  ⚠️  {company_name} 分析出错: {e}")
        
        return detailed_results
    
    def generate_year_trend_report(self, output_file: str = None):
        """生成年份趋势报告"""
        if output_file is None:
            output_file = self.knowledge_dir / "年份趋势分析报告.md"
        else:
            output_file = Path(output_file)
        
        # 分析所有公司
        summary_df = self.analyze_all_companies()
        detailed_results = self.generate_detailed_year_analysis()
        
        # 生成报告
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 竞品年份趋势分析报告\n\n")
            f.write("=" * 80 + "\n\n")
            
            # 总体统计
            f.write("## 总体统计\n\n")
            f.write("| 公司 | 总URL数 | 有年份数据 | 年份数据占比 | 年份数 | 最早年份 | 最新年份 | 最活跃年份 |\n")
            f.write("|------|---------|------------|--------------|--------|----------|----------|------------|\n")
            
            for _, row in summary_df.iterrows():
                has_data = "✅" if row['has_year_data'] else "❌"
                f.write(f"| {row['company']} | {row['total_urls']} | {has_data} | "
                       f"{row['year_data_ratio']:.1f}% | {row['years_count']} | "
                       f"{row['earliest_year'] or 'N/A'} | {row['latest_year'] or 'N/A'} | "
                       f"{row['most_active_year'] or 'N/A'} ({row['most_active_year_count']}) |\n")
            
            f.write("\n")
            
            # 详细分析
            f.write("## 详细年份分布\n\n")
            
            for company, data in detailed_results.items():
                f.write(f"### {company}\n\n")
                f.write(f"- **总URL数**: {data['total_urls']}\n")
                f.write(f"- **有年份数据的URL**: {data['total_with_year']} ({data['total_with_year']/data['total_urls']*100:.1f}%)\n\n")
                
                f.write("**年份分布**:\n\n")
                f.write("| 年份 | URL数量 |\n")
                f.write("|------|----------|\n")
                
                # 按年份排序
                year_dist = data['year_distribution']
                sorted_years = sorted(year_dist.items(), key=lambda x: int(x[0]) if str(x[0]).isdigit() else 0, reverse=True)
                
                for year, count in sorted_years[:10]:  # 显示前10年
                    f.write(f"| {year} | {count} |\n")
                
                if len(sorted_years) > 10:
                    f.write(f"| ... | ... |\n")
                
                f.write("\n")
                
                # 内容类型按年份
                if data['content_type_by_year']:
                    f.write("**内容类型按年份分布** (前5年):\n\n")
                    recent_years = sorted(data['content_type_by_year'].keys(), reverse=True)[:5]
                    for year in recent_years:
                        f.write(f"- **{year}**: {data['content_type_by_year'][year]}\n")
                    f.write("\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("## 发现\n\n")
            
            # 统计有年份数据的公司
            has_data_companies = summary_df[summary_df['has_year_data'] == True]
            no_data_companies = summary_df[summary_df['has_year_data'] == False]
            
            f.write(f"- **有年份数据的公司**: {len(has_data_companies)} 个\n")
            f.write(f"- **无年份数据的公司**: {len(no_data_companies)} 个\n\n")
            
            if len(no_data_companies) > 0:
                f.write("**无年份数据的公司列表**:\n")
                for _, row in no_data_companies.iterrows():
                    f.write(f"- {row['company']} ({row['total_urls']} 个URL)\n")
                f.write("\n")
                f.write("**原因分析**: 这些公司的XML sitemap文件中可能没有`<lastmod>`标签，或者标签格式不同。\n\n")
        
        print(f"✅ 年份趋势分析报告已保存: {output_file}")
        
        # 保存CSV
        csv_file = self.knowledge_dir / "年份趋势分析.csv"
        summary_df.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"✅ 年份趋势数据已保存: {csv_file}")
        
        return str(output_file)


def main():
    """主函数"""
    analyzer = YearsTrendAnalyzer()
    analyzer.generate_year_trend_report()


if __name__ == "__main__":
    main()




