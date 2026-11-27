#!/usr/bin/env python3
"""
Siemens 内容营销策略深度分析器
专门针对Siemens进行全面的内容营销策略分析
"""

import pandas as pd
import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List
import re


class SiemensContentStrategyAnalyzer:
    """Siemens内容营销策略分析器"""
    
    def __init__(self):
        """初始化分析器"""
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        
        self.output_data_dir = project_root / "output_data"
        self.knowledge_dir = project_root / "Knowledge"
        self.siemens_dir = self.knowledge_dir / "Siemens内容营销策略研究"
        self.siemens_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载数据
        self.df = pd.read_csv(self.output_data_dir / "siemens_analyzed.csv")
    
    def analyze_content_types(self) -> Dict:
        """分析内容类型分布"""
        analysis = {
            'total_urls': len(self.df),
            'content_type_distribution': {},
            'content_type_percentage': {},
        }
        
        type_counts = self.df['content_type'].value_counts()
        analysis['content_type_distribution'] = type_counts.to_dict()
        
        for ct, count in type_counts.items():
            analysis['content_type_percentage'][ct] = count / len(self.df) * 100
        
        return analysis
    
    def analyze_category_structure(self) -> Dict:
        """分析分类体系"""
        analysis = {
            'sections': {},
            'subsections': {},
            'section_subsection_pairs': defaultdict(int),
            'category_hierarchy': {},
        }
        
        # Section分析
        section_counts = self.df['section'].value_counts()
        analysis['sections'] = section_counts.to_dict()
        
        # Subsection分析
        subsection_counts = self.df['subsection'].value_counts()
        analysis['subsections'] = subsection_counts.to_dict()
        
        # Section-Subsection组合
        for _, row in self.df.iterrows():
            section = row.get('section', '')
            subsection = row.get('subsection', '')
            if pd.notna(section) and pd.notna(subsection) and section != '' and subsection != '':
                pair = f"{section}/{subsection}"
                analysis['section_subsection_pairs'][pair] += 1
        
        # 分类层级分析
        for section in self.df['section'].dropna().unique():
            if section:
                section_df = self.df[self.df['section'] == section]
                subsections = section_df['subsection'].dropna().unique()
                analysis['category_hierarchy'][section] = {
                    'count': len(section_df),
                    'subsections': list(subsections),
                    'subsection_count': len(subsections)
                }
        
        return analysis
    
    def analyze_url_structure(self) -> Dict:
        """分析URL结构"""
        analysis = {
            'avg_depth': 0,
            'max_depth': 0,
            'depth_distribution': {},
            'naming_patterns': Counter(),
            'url_patterns': [],
        }
        
        if 'depth' in self.df.columns:
            self.df['depth'] = pd.to_numeric(self.df['depth'], errors='coerce')
            analysis['avg_depth'] = self.df['depth'].mean()
            analysis['max_depth'] = self.df['depth'].max()
            analysis['depth_distribution'] = self.df['depth'].value_counts().sort_index().to_dict()
        
        # 命名模式分析
        for filename in self.df['filename'].dropna():
            filename_str = str(filename)
            if '-' in filename_str:
                analysis['naming_patterns']['kebab-case'] += 1
            elif '_' in filename_str:
                analysis['naming_patterns']['snake_case'] += 1
            elif any(c.isupper() for c in filename_str[1:]):
                analysis['naming_patterns']['camelCase'] += 1
            else:
                analysis['naming_patterns']['lowercase'] += 1
        
        # URL模式示例
        analysis['url_patterns'] = self.df['url'].head(20).tolist()
        
        return analysis
    
    def analyze_content_timeline(self) -> Dict:
        """分析内容时间线"""
        analysis = {
            'by_year': {},
            'by_month': {},
            'yearly_trend': {},
        }
        
        if 'year' in self.df.columns:
            year_counts = self.df['year'].value_counts().sort_index()
            analysis['by_year'] = {str(k): int(v) for k, v in year_counts.items() if pd.notna(k)}
        
        if 'month' in self.df.columns:
            month_counts = self.df['month'].value_counts().sort_index()
            analysis['by_month'] = {str(k): int(v) for k, v in month_counts.items() if pd.notna(k)}
        
        return analysis
    
    def analyze_language_strategy(self) -> Dict:
        """分析多语言策略"""
        analysis = {
            'languages': {},
            'language_distribution': {},
            'multilingual_ratio': 0,
        }
        
        if 'language' in self.df.columns:
            lang_counts = self.df['language'].value_counts()
            analysis['languages'] = lang_counts.to_dict()
            
            total = len(self.df)
            for lang, count in lang_counts.items():
                analysis['language_distribution'][lang] = count / total * 100
            
            # 多语言比例（非英语内容）
            non_en = self.df[self.df['language'] != 'en']
            analysis['multilingual_ratio'] = len(non_en) / total * 100 if total > 0 else 0
        
        return analysis
    
    def analyze_content_by_section(self) -> Dict:
        """按分类分析内容类型"""
        analysis = {}
        
        for section in self.df['section'].dropna().unique():
            if section:
                section_df = self.df[self.df['section'] == section]
                content_types = section_df['content_type'].value_counts()
                analysis[section] = {
                    'total': len(section_df),
                    'content_types': content_types.to_dict(),
                    'top_content_type': content_types.index[0] if len(content_types) > 0 else None
                }
        
        return analysis
    
    def generate_comprehensive_report(self) -> str:
        """生成综合策略报告"""
        report_file = self.siemens_dir / "Siemens内容营销策略深度分析.md"
        
        # 执行各项分析
        content_types = self.analyze_content_types()
        category_structure = self.analyze_category_structure()
        url_structure = self.analyze_url_structure()
        timeline = self.analyze_content_timeline()
        language = self.analyze_language_strategy()
        content_by_section = self.analyze_content_by_section()
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Siemens 内容营销策略深度分析报告\n\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"**分析日期**: {pd.Timestamp.now().strftime('%Y-%m-%d')}\n")
            f.write(f"**数据来源**: siemens_analyzed.csv\n")
            f.write(f"**总URL数**: {content_types['total_urls']:,}\n\n")
            f.write("=" * 80 + "\n\n")
            
            # 执行摘要
            f.write("## 执行摘要\n\n")
            f.write("### 关键发现\n\n")
            f.write(f"1. **内容规模**: {content_types['total_urls']:,} 个URL，内容类型丰富\n")
            f.write(f"2. **主要内容类型**: {list(content_types['content_type_distribution'].keys())[:3]}\n")
            f.write(f"3. **分类体系**: {len(category_structure['sections'])} 个主要分类\n")
            f.write(f"4. **多语言支持**: {len(language['languages'])} 种语言，多语言比例 {language['multilingual_ratio']:.1f}%\n")
            f.write(f"5. **URL结构**: 平均深度 {url_structure['avg_depth']:.1f} 层\n\n")
            
            # 内容类型分析
            f.write("## 1. 内容类型分布\n\n")
            f.write("| 内容类型 | 数量 | 占比 |\n")
            f.write("|----------|------|------|\n")
            for ct, count in list(content_types['content_type_distribution'].items())[:15]:
                pct = content_types['content_type_percentage'][ct]
                f.write(f"| {ct} | {count:,} | {pct:.1f}% |\n")
            f.write("\n")
            
            # 分类体系分析
            f.write("## 2. 内容分类体系\n\n")
            f.write("### 主要分类 (Top 20)\n\n")
            f.write("| 分类 | 内容数 | 占比 |\n")
            f.write("|------|--------|------|\n")
            for section, count in list(category_structure['sections'].items())[:20]:
                pct = count / content_types['total_urls'] * 100
                f.write(f"| {section} | {count:,} | {pct:.1f}% |\n")
            f.write("\n")
            
            # 分类层级结构
            f.write("### 分类层级结构\n\n")
            sorted_sections = sorted(category_structure['category_hierarchy'].items(), 
                                   key=lambda x: x[1]['count'], reverse=True)
            for section, info in sorted_sections[:10]:
                f.write(f"#### {section}\n\n")
                f.write(f"- **内容数**: {info['count']:,}\n")
                f.write(f"- **子分类数**: {info['subsection_count']}\n")
                if info['subsections']:
                    f.write(f"- **主要子分类**: {', '.join(info['subsections'][:5])}\n")
                f.write("\n")
            
            # URL结构分析
            f.write("## 3. URL结构分析\n\n")
            f.write(f"- **平均深度**: {url_structure['avg_depth']:.1f} 层\n")
            f.write(f"- **最大深度**: {url_structure['max_depth']:.0f} 层\n\n")
            f.write("### 深度分布\n\n")
            f.write("| 深度 | URL数 |\n")
            f.write("|------|-------|\n")
            for depth, count in list(url_structure['depth_distribution'].items())[:10]:
                if pd.notna(depth):
                    f.write(f"| {int(depth)} 层 | {count:,} |\n")
            f.write("\n")
            
            # 命名模式
            f.write("### 命名模式\n\n")
            total_naming = sum(url_structure['naming_patterns'].values())
            for pattern, count in url_structure['naming_patterns'].most_common():
                pct = count / total_naming * 100 if total_naming > 0 else 0
                f.write(f"- **{pattern}**: {count:,} ({pct:.1f}%)\n")
            f.write("\n")
            
            # 多语言策略
            f.write("## 4. 多语言策略\n\n")
            f.write(f"- **支持语言数**: {len(language['languages'])}\n")
            f.write(f"- **多语言比例**: {language['multilingual_ratio']:.1f}%\n\n")
            f.write("### 语言分布\n\n")
            f.write("| 语言 | 内容数 | 占比 |\n")
            f.write("|------|--------|------|\n")
            for lang, count in list(language['languages'].items())[:15]:
                pct = language['language_distribution'][lang]
                f.write(f"| {lang} | {count:,} | {pct:.1f}% |\n")
            f.write("\n")
            
            # 内容时间线
            f.write("## 5. 内容发布时间线\n\n")
            if timeline['by_year']:
                f.write("### 按年份分布\n\n")
                f.write("| 年份 | 内容数 |\n")
                f.write("|------|--------|\n")
                for year, count in sorted(timeline['by_year'].items()):
                    f.write(f"| {year} | {count:,} |\n")
                f.write("\n")
            else:
                f.write("(无年份数据)\n\n")
            
            # 按分类的内容类型分析
            f.write("## 6. 各分类的内容类型分布\n\n")
            sorted_sections = sorted(content_by_section.items(), 
                                   key=lambda x: x[1]['total'], reverse=True)
            for section, info in sorted_sections[:10]:
                f.write(f"### {section}\n\n")
                f.write(f"- **总内容数**: {info['total']:,}\n")
                f.write(f"- **主要内容类型**: {info['top_content_type']}\n")
                f.write(f"- **内容类型分布**:\n")
                for ct, count in list(info['content_types'].items())[:5]:
                    f.write(f"  - {ct}: {count}\n")
                f.write("\n")
            
            # 策略洞察
            f.write("## 7. 策略洞察\n\n")
            f.write("### 优势\n\n")
            f.write("1. **内容规模大**: 拥有 {:,} 个URL，内容资源丰富\n".format(content_types['total_urls']))
            f.write("2. **分类体系完善**: {:,} 个主要分类，组织结构清晰\n".format(len(category_structure['sections'])))
            f.write("3. **多语言覆盖**: 支持 {:,} 种语言，国际化程度高\n".format(len(language['languages'])))
            f.write("4. **内容类型多样**: 涵盖产品、行业、公司等多种类型\n\n")
            
            f.write("### 特点\n\n")
            f.write("1. **深度分类**: URL平均深度 {:.1f} 层，分类细致\n".format(url_structure['avg_depth']))
            f.write("2. **命名规范**: 主要使用 kebab-case 命名模式\n")
            f.write("3. **内容分布**: 产品相关内容占主导地位\n\n")
            
            f.write("### 建议\n\n")
            f.write("1. 继续保持多语言内容策略，扩大国际化影响\n")
            f.write("2. 优化URL结构，平衡深度与可访问性\n")
            f.write("3. 加强内容类型多样化，增加案例研究、白皮书等深度内容\n")
            f.write("4. 建立内容更新机制，保持内容新鲜度\n\n")
        
        print(f"✅ 综合策略报告已保存: {report_file}")
        return str(report_file)
    
    def generate_json_data(self) -> str:
        """生成JSON格式数据（便于程序化分析）"""
        json_file = self.siemens_dir / "siemens_content_strategy.json"
        
        # 转换numpy类型为Python原生类型
        def convert_to_native(obj):
            if isinstance(obj, dict):
                return {k: convert_to_native(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_native(item) for item in obj]
            elif pd.isna(obj):
                return None
            elif isinstance(obj, (pd.Int64Dtype, pd.Float64Dtype)):
                return None
            elif hasattr(obj, 'item'):  # numpy types
                return obj.item()
            elif isinstance(obj, (int, float)) and (isinstance(obj, pd.Int64Dtype) or isinstance(obj, pd.Float64Dtype)):
                return None
            else:
                return obj
        
        url_struct = self.analyze_url_structure()
        data = {
            'content_types': convert_to_native(self.analyze_content_types()),
            'category_structure': convert_to_native(self.analyze_category_structure()),
            'url_structure': {
                'avg_depth': float(url_struct['avg_depth']) if pd.notna(url_struct['avg_depth']) else 0,
                'max_depth': int(url_struct['max_depth']) if pd.notna(url_struct['max_depth']) else 0,
                'naming_patterns': {k: int(v) for k, v in url_struct['naming_patterns'].items()}
            },
            'timeline': convert_to_native(self.analyze_content_timeline()),
            'language': convert_to_native(self.analyze_language_strategy()),
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ JSON数据已保存: {json_file}")
        return str(json_file)


def main():
    """主函数"""
    analyzer = SiemensContentStrategyAnalyzer()
    analyzer.generate_comprehensive_report()
    analyzer.generate_json_data()
    
    print("\n" + "=" * 80)
    print("✅ Siemens 内容营销策略分析完成！")
    print("=" * 80)
    print(f"\n📁 分析结果保存在: {analyzer.siemens_dir}")


if __name__ == "__main__":
    main()

