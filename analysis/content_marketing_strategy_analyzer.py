#!/usr/bin/env python3
"""
内容营销策略和执行分析器
从网站数据中提取内容营销策略和执行细节
"""

import pandas as pd
import re
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
import json
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent))


class ContentMarketingStrategyAnalyzer:
    """内容营销策略分析器"""
    
    def __init__(self):
        """初始化分析器"""
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        
        self.output_data_dir = project_root / "output_data"
        self.reference_dir = self.output_data_dir / "reference"
        self.insight_dir = project_root / "insight"
        self.insight_reports_dir = self.insight_dir / "reports"
        self.insight_data_dir = self.insight_dir / "data"
        
        # 内容营销漏斗阶段
        self.funnel_stages = {
            'awareness': ['blog', 'article', 'news', 'press-release', 'whitepaper', 'ebook', 'report'],
            'consideration': ['webinar', 'demo', 'case-study', 'customer-story', 'success-story', 'video'],
            'conversion': ['datasheet', 'specification', 'pricing', 'trial', 'contact', 'request-demo'],
            'loyalty': ['documentation', 'guide', 'tutorial', 'support', 'community', 'training']
        }
        
        # 内容类型映射
        self.content_type_mapping = {
            'blog': 'blog',
            'article': 'blog',
            'news': 'news',
            'press-release': 'news',
            'webinar': 'webinar',
            'whitepaper': 'resource',
            'ebook': 'resource',
            'case-study': 'case-study',
            'customer-story': 'case-study',
            'datasheet': 'resource',
            'documentation': 'documentation',
            'guide': 'resource',
            'video': 'video',
            'demo': 'demo',
            'trial': 'demo'
        }
    
    def analyze_content_distribution(self, df: pd.DataFrame) -> Dict:
        """分析内容分布策略"""
        total = len(df)
        
        # 内容类型分布
        content_type_dist = df['content_type'].value_counts().to_dict()
        content_type_pct = {k: v/total*100 for k, v in content_type_dist.items()}
        
        # 内容深度分布
        depth_dist = df['depth'].value_counts().to_dict()
        avg_depth = df['depth'].mean()
        
        # 多语言策略
        language_dist = df['language'].value_counts().to_dict()
        language_pct = {k: v/total*100 for k, v in language_dist.items()}
        
        # 内容更新频率（基于lastmod）
        df_with_date = df[df['year'].notna()]
        if len(df_with_date) > 0:
            year_dist = df_with_date['year'].value_counts().sort_index().to_dict()
            recent_years = {k: v for k, v in year_dist.items() if k >= 2020}
        else:
            year_dist = {}
            recent_years = {}
        
        return {
            'total_content': total,
            'content_type_distribution': content_type_dist,
            'content_type_percentage': content_type_pct,
            'depth_distribution': depth_dist,
            'average_depth': float(avg_depth),
            'language_distribution': language_dist,
            'language_percentage': language_pct,
            'year_distribution': year_dist,
            'recent_content_years': recent_years,
            'content_update_activity': len(recent_years) > 0
        }
    
    def analyze_content_funnel(self, df: pd.DataFrame) -> Dict:
        """分析内容营销漏斗"""
        funnel_counts = defaultdict(int)
        
        for _, row in df.iterrows():
            content_type = str(row.get('content_type', '')).lower()
            path = str(row.get('path', '')).lower()
            url = str(row.get('url', '')).lower()
            
            # 判断漏斗阶段
            for stage, keywords in self.funnel_stages.items():
                if any(kw in content_type or kw in path or kw in url for kw in keywords):
                    funnel_counts[stage] += 1
                    break
        
        total_funnel = sum(funnel_counts.values())
        funnel_pct = {k: v/total_funnel*100 if total_funnel > 0 else 0 
                      for k, v in funnel_counts.items()}
        
        return {
            'funnel_distribution': dict(funnel_counts),
            'funnel_percentage': funnel_pct,
            'funnel_balance': self._calculate_funnel_balance(funnel_pct)
        }
    
    def _calculate_funnel_balance(self, funnel_pct: Dict) -> str:
        """计算漏斗平衡度"""
        awareness = funnel_pct.get('awareness', 0)
        consideration = funnel_pct.get('consideration', 0)
        decision = funnel_pct.get('decision', 0)
        
        if awareness > 40 and consideration > 20:
            return "balanced"
        elif awareness > 50:
            return "awareness-heavy"
        elif consideration > 40:
            return "consideration-heavy"
        elif decision > 30:
            return "decision-heavy"
        else:
            return "unbalanced"
    
    def analyze_content_organization(self, df: pd.DataFrame) -> Dict:
        """分析内容组织策略"""
        # 主要分类体系
        section_dist = df['section'].value_counts().head(10).to_dict()
        subsection_dist = df['subsection'].value_counts().head(10).to_dict()
        
        # URL结构模式
        path_patterns = []
        for path in df['path'].head(1000):
            if pd.notna(path):
                segments = str(path).split('/')
                if len(segments) >= 3:
                    pattern = '/'.join(segments[:3])
                    path_patterns.append(pattern)
        
        top_patterns = Counter(path_patterns).most_common(10)
        
        # 内容层级深度
        depth_stats = {
            'min': int(df['depth'].min()),
            'max': int(df['depth'].max()),
            'mean': float(df['depth'].mean()),
            'median': float(df['depth'].median())
        }
        
        return {
            'main_sections': section_dist,
            'subsections': subsection_dist,
            'url_patterns': dict(top_patterns),
            'depth_statistics': depth_stats,
            'organization_style': self._infer_organization_style(depth_stats, section_dist)
        }
    
    def _infer_organization_style(self, depth_stats: Dict, sections: Dict) -> str:
        """推断组织风格"""
        avg_depth = depth_stats['mean']
        num_sections = len(sections)
        
        if avg_depth > 4 and num_sections > 5:
            return "deep-hierarchical"
        elif avg_depth > 3:
            return "hierarchical"
        elif num_sections > 8:
            return "flat-broad"
        else:
            return "simple-flat"
    
    def analyze_content_themes(self, df: pd.DataFrame) -> Dict:
        """分析内容主题策略"""
        # 从section和subsection提取主题
        themes = []
        for _, row in df.iterrows():
            section = str(row.get('section', ''))
            subsection = str(row.get('subsection', ''))
            
            if section and section != 'nan':
                themes.append(section.lower())
            if subsection and subsection != 'nan':
                themes.append(subsection.lower())
        
        theme_counts = Counter(themes)
        
        # 行业聚焦
        industry_keywords = ['industry', 'industries', 'sector', 'vertical', 
                           'automation', 'manufacturing', 'industrial']
        industry_content = df[df['path'].str.contains('|'.join(industry_keywords), 
                                                      case=False, na=False)]
        industry_ratio = len(industry_content) / len(df) * 100 if len(df) > 0 else 0
        
        # 产品聚焦
        product_keywords = ['product', 'products', 'solution', 'platform']
        product_content = df[df['path'].str.contains('|'.join(product_keywords), 
                                                     case=False, na=False)]
        product_ratio = len(product_content) / len(df) * 100 if len(df) > 0 else 0
        
        return {
            'top_themes': dict(theme_counts.most_common(15)),
            'industry_focus_ratio': float(industry_ratio),
            'product_focus_ratio': float(product_ratio),
            'theme_diversity': len(theme_counts)
        }
    
    def analyze_content_execution(self, df: pd.DataFrame) -> Dict:
        """分析内容执行细节"""
        # 内容更新频率
        df_with_date = df[df['year'].notna() & (df['year'] >= 2020)]
        
        if len(df_with_date) > 0:
            # 按年份统计
            yearly_counts = df_with_date.groupby('year').size().to_dict()
            
            # 计算更新趋势
            if len(yearly_counts) >= 2:
                years = sorted(yearly_counts.keys())
                recent_trend = 'increasing' if yearly_counts[years[-1]] > yearly_counts[years[-2]] else 'decreasing'
            else:
                recent_trend = 'stable'
            
            # 月度分布
            df_with_month = df_with_date[df_with_date['month'].notna()]
            if len(df_with_month) > 0:
                monthly_dist = df_with_month.groupby('month').size().to_dict()
            else:
                monthly_dist = {}
        else:
            yearly_counts = {}
            recent_trend = 'unknown'
            monthly_dist = {}
        
        # 内容类型执行
        content_execution = {}
        for content_type in df['content_type'].unique():
            if pd.notna(content_type):
                type_df = df[df['content_type'] == content_type]
                content_execution[content_type] = {
                    'count': len(type_df),
                    'avg_depth': float(type_df['depth'].mean()),
                    'has_recent_updates': len(type_df[type_df['year'] >= 2023]) > 0 if 'year' in type_df.columns else False
                }
        
        return {
            'yearly_content_count': yearly_counts,
            'recent_trend': recent_trend,
            'monthly_distribution': monthly_dist,
            'content_type_execution': content_execution,
            'update_frequency': self._infer_update_frequency(yearly_counts)
        }
    
    def _infer_update_frequency(self, yearly_counts: Dict) -> str:
        """推断更新频率"""
        if not yearly_counts:
            return "unknown"
        
        total = sum(yearly_counts.values())
        num_years = len(yearly_counts)
        
        if num_years == 0:
            return "unknown"
        
        avg_per_year = total / num_years
        
        if avg_per_year > 500:
            return "very-active"
        elif avg_per_year > 200:
            return "active"
        elif avg_per_year > 50:
            return "moderate"
        else:
            return "low"
    
    def analyze_company(self, company_name: str, csv_file: Path, is_reference: bool = False) -> Dict:
        """分析单个公司的内容营销策略"""
        if not csv_file.exists():
            return None
        
        df = pd.read_csv(csv_file)
        
        # 执行各项分析
        content_dist = self.analyze_content_distribution(df)
        content_funnel = self.analyze_content_funnel(df)
        content_org = self.analyze_content_organization(df)
        content_themes = self.analyze_content_themes(df)
        content_execution = self.analyze_content_execution(df)
        
        # 判断公司类别
        if is_reference:
            if company_name in ['apple', 'xiaomi', 'byd']:
                category = 'To C消费品'
            else:
                category = 'To B科技/软件'
        else:
            category = 'To B工业自动化'
        
        return {
            'company': company_name,
            'category': category,
            'content_distribution': content_dist,
            'content_funnel': content_funnel,
            'content_organization': content_org,
            'content_themes': content_themes,
            'content_execution': content_execution
        }
    
    def generate_strategy_summary(self, result: Dict) -> Dict:
        """生成策略总结"""
        dist = result['content_distribution']
        funnel = result['content_funnel']
        org = result['content_organization']
        themes = result['content_themes']
        execution = result['content_execution']
        
        # 主要策略
        top_content_types = sorted(dist['content_type_percentage'].items(), 
                                   key=lambda x: x[1], reverse=True)[:3]
        main_strategy = ', '.join([f"{k}({v:.1f}%)" for k, v in top_content_types])
        
        # 漏斗策略
        funnel_strategy = funnel['funnel_balance']
        
        # 组织策略
        org_strategy = org['organization_style']
        
        # 主题策略
        top_themes = sorted(themes['top_themes'].items(), 
                           key=lambda x: x[1], reverse=True)[:3]
        theme_strategy = ', '.join([f"{k}({v})" for k, v in top_themes])
        
        # 执行策略
        update_freq = execution['update_frequency']
        trend = execution['recent_trend']
        
        return {
            'main_content_strategy': main_strategy,
            'funnel_strategy': funnel_strategy,
            'organization_strategy': org_strategy,
            'theme_strategy': theme_strategy,
            'update_frequency': update_freq,
            'recent_trend': trend
        }
    
    def analyze_all_companies(self):
        """分析所有公司"""
        print("=" * 80)
        print("内容营销策略和执行分析")
        print("=" * 80)
        print()
        
        results = []
        
        # 分析竞品公司
        print("分析竞品公司...")
        competitor_files = sorted(self.output_data_dir.glob("*_analyzed.csv"))
        competitor_files = [f for f in competitor_files if 'reference' not in str(f)]
        
        for csv_file in competitor_files:
            company = csv_file.stem.replace('_analyzed', '')
            print(f"  分析 {company}...")
            result = self.analyze_company(company, csv_file, is_reference=False)
            if result:
                result['strategy_summary'] = self.generate_strategy_summary(result)
                results.append(result)
        
        print()
        
        # 分析参考公司
        print("分析参考公司...")
        if self.reference_dir.exists():
            reference_files = sorted(self.reference_dir.glob("*_analyzed.csv"))
            
            for csv_file in reference_files:
                company = csv_file.stem.replace('_analyzed', '')
                print(f"  分析 {company}...")
                result = self.analyze_company(company, csv_file, is_reference=True)
                if result:
                    result['strategy_summary'] = self.generate_strategy_summary(result)
                    results.append(result)
        
        print()
        
        # 保存数据
        data_file = self.insight_data_dir / "内容营销策略分析数据.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        print(f"✅ 数据已保存: {data_file}")
        
        # 生成报告
        self.generate_report(results)
        
        print()
        print("=" * 80)
        print("分析完成")
        print("=" * 80)
    
    def generate_report(self, results: List[Dict]):
        """生成分析报告"""
        report_file = self.insight_reports_dir / "内容营销策略和执行分析报告.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 内容营销策略和执行分析报告\n\n")
            f.write("=" * 80 + "\n\n")
            f.write("**说明**: 本报告基于网站sitemap数据，分析各公司的内容营销策略和执行情况\n")
            f.write("**数据来源**: output_data/*_analyzed.csv\n\n")
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
                    company = result['company']
                    dist = result['content_distribution']
                    funnel = result['content_funnel']
                    org = result['content_organization']
                    themes = result['content_themes']
                    execution = result['content_execution']
                    summary = result['strategy_summary']
                    
                    f.write(f"### {company}\n\n")
                    
                    # 策略总结
                    f.write("#### 策略总结\n\n")
                    f.write(f"- **主要内容策略**: {summary['main_content_strategy']}\n")
                    f.write(f"- **漏斗策略**: {summary['funnel_strategy']}\n")
                    f.write(f"- **组织策略**: {summary['organization_strategy']}\n")
                    f.write(f"- **主题策略**: {summary['theme_strategy']}\n")
                    f.write(f"- **更新频率**: {summary['update_frequency']}\n")
                    f.write(f"- **近期趋势**: {summary['recent_trend']}\n\n")
                    
                    # 内容分布
                    f.write("#### 内容分布策略\n\n")
                    f.write(f"- **总内容数**: {dist['total_content']:,}\n")
                    f.write(f"- **平均深度**: {dist['average_depth']:.1f}\n")
                    f.write(f"- **主要语言**: {list(dist['language_distribution'].keys())[:3]}\n\n")
                    
                    f.write("**内容类型分布（Top 5）**:\n")
                    top_types = sorted(dist['content_type_percentage'].items(), 
                                      key=lambda x: x[1], reverse=True)[:5]
                    for content_type, pct in top_types:
                        f.write(f"- {content_type}: {pct:.1f}%\n")
                    f.write("\n")
                    
                    # 内容漏斗
                    f.write("#### 内容营销漏斗\n\n")
                    funnel_dist = funnel['funnel_distribution']
                    funnel_pct = funnel['funnel_percentage']
                    f.write("| 阶段 | 数量 | 占比 |\n")
                    f.write("|------|------|------|\n")
                    for stage in ['awareness', 'consideration', 'conversion', 'loyalty']:
                        count = funnel_dist.get(stage, 0)
                        pct = funnel_pct.get(stage, 0)
                        stage_name = {'awareness': 'Awareness (认知)', 'consideration': 'Consideration (考虑)', 
                                     'conversion': 'Conversion (转化)', 'loyalty': 'Loyalty (忠诚)'}.get(stage, stage)
                        f.write(f"| {stage_name} | {count:,} | {pct:.1f}% |\n")
                    f.write(f"\n**漏斗平衡度**: {funnel['funnel_balance']}\n\n")
                    
                    # 内容组织
                    f.write("#### 内容组织策略\n\n")
                    f.write(f"- **组织风格**: {org['organization_style']}\n")
                    f.write(f"- **深度统计**: 最小{org['depth_statistics']['min']}, "
                           f"最大{org['depth_statistics']['max']}, "
                           f"平均{org['depth_statistics']['mean']:.1f}\n\n")
                    
                    f.write("**主要分类（Top 5）**:\n")
                    for section, count in list(org['main_sections'].items())[:5]:
                        f.write(f"- {section}: {count:,}\n")
                    f.write("\n")
                    
                    # 内容主题
                    f.write("#### 内容主题策略\n\n")
                    f.write(f"- **主题多样性**: {themes['theme_diversity']} 个不同主题\n")
                    f.write(f"- **行业聚焦**: {themes['industry_focus_ratio']:.1f}%\n")
                    f.write(f"- **产品聚焦**: {themes['product_focus_ratio']:.1f}%\n\n")
                    
                    f.write("**Top 5主题**:\n")
                    for theme, count in list(themes['top_themes'].items())[:5]:
                        f.write(f"- {theme}: {count:,}\n")
                    f.write("\n")
                    
                    # 执行细节
                    f.write("#### 内容执行细节\n\n")
                    f.write(f"- **更新频率**: {execution['update_frequency']}\n")
                    f.write(f"- **近期趋势**: {execution['recent_trend']}\n\n")
                    
                    if execution['yearly_content_count']:
                        f.write("**年度内容产出**:\n")
                        for year, count in sorted(execution['yearly_content_count'].items()):
                            f.write(f"- {year}: {count:,}\n")
                        f.write("\n")
                    
                    f.write("---\n\n")
            
            # 对比分析
            f.write("## 策略对比分析\n\n")
            
            # 按类别统计
            for category, companies in categories.items():
                f.write(f"### {category} - 平均指标\n\n")
                
                avg_total = sum(r['content_distribution']['total_content'] for r in companies) / len(companies)
                avg_depth = sum(r['content_distribution']['average_depth'] for r in companies) / len(companies)
                
                # 计算平均漏斗分布
                avg_funnel = defaultdict(float)
                for r in companies:
                    for stage, pct in r['content_funnel']['funnel_percentage'].items():
                        avg_funnel[stage] += pct
                for stage in avg_funnel:
                    avg_funnel[stage] /= len(companies)
                
                f.write(f"- **平均内容数**: {avg_total:,.0f}\n")
                f.write(f"- **平均深度**: {avg_depth:.1f}\n")
                f.write(f"- **平均漏斗分布**:\n")
                for stage in ['awareness', 'consideration', 'conversion', 'loyalty']:
                    stage_name = {'awareness': 'Awareness (认知)', 'consideration': 'Consideration (考虑)', 
                                 'conversion': 'Conversion (转化)', 'loyalty': 'Loyalty (忠诚)'}.get(stage, stage)
                    f.write(f"  - {stage_name}: {avg_funnel[stage]:.1f}%\n")
                f.write("\n")
            
            f.write("=" * 80 + "\n")
        
        print(f"✅ 报告已保存: {report_file}")


if __name__ == "__main__":
    analyzer = ContentMarketingStrategyAnalyzer()
    analyzer.analyze_all_companies()

