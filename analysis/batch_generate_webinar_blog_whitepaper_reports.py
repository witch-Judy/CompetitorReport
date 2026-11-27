#!/usr/bin/env python3
"""
批量生成所有公司的Webinar、Blog、White Paper深度分析报告
基于Siemens报告的结构模板
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List
from collections import Counter
from datetime import datetime
import re


class WebinarBlogWhitePaperReportGenerator:
    """Webinar、Blog、White Paper深度分析报告生成器"""
    
    def __init__(self):
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        
        self.output_data_dir = project_root / "output_data"
        self.company_analysis_dir = project_root / "companyAnalysis"
        self.company_analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # 18家公司列表（排除Siemens）
        self.companies = {
            'abb': {'name': 'ABB', 'domain': 'abb.com'},
            'aveva': {'name': 'AVEVA', 'domain': 'aveva.com'},
            'bosch': {'name': 'Bosch', 'domain': 'bosch.com'},
            'cognite': {'name': 'Cognite', 'domain': 'cognite.com'},
            'emerson': {'name': 'Emerson', 'domain': 'emerson.com'},
            'ge': {'name': 'GE', 'domain': 'ge.com'},
            'hitachi': {'name': 'Hitachi', 'domain': 'hitachi.com'},
            'hivemq': {'name': 'HiveMQ', 'domain': 'hivemq.com'},
            'honeywell': {'name': 'Honeywell', 'domain': 'honeywell.com'},
            'ignition': {'name': 'Ignition', 'domain': 'inductiveautomation.com'},
            'rockwell-automation': {'name': 'Rockwell Automation', 'domain': 'rockwellautomation.com'},
            'schneider-electric': {'name': 'Schneider Electric', 'domain': 'schneider-electric.com'},
            'tulip': {'name': 'Tulip', 'domain': 'tulip.co'},
            'yokogawa': {'name': 'Yokogawa', 'domain': 'yokogawa.com'},
            'C3 AI': {'name': 'C3 AI', 'domain': 'c3.ai'},
            'umh': {'name': 'UMH', 'domain': 'umh.com'},
            'univers': {'name': 'Univers', 'domain': 'univers.com'}
        }
    
    def find_data_file(self, company_key: str) -> Path:
        """查找公司的数据文件"""
        possible_files = [
            self.output_data_dir / f"{company_key}_analyzed.csv",
            self.output_data_dir / f"{company_key.lower()}_analyzed.csv",
            self.output_data_dir / f"{company_key.replace('-', '_')}_analyzed.csv",
        ]
        
        for file_path in possible_files:
            if file_path.exists():
                return file_path
        
        return None
    
    def load_company_data(self, company_key: str) -> pd.DataFrame:
        """加载公司数据"""
        file_path = self.find_data_file(company_key)
        if file_path is None:
            return None
        
        try:
            df = pd.read_csv(file_path)
            return df
        except Exception as e:
            print(f"Error loading {company_key}: {e}")
            return None
    
    def extract_keywords(self, text: str, min_length=3) -> List[str]:
        """从文本中提取关键词"""
        if pd.isna(text):
            return []
        
        # 过滤停用词
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'a', 'an', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
            'could', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
            'https', 'http', 'www', 'com', 'org', 'net', 'edu', 'gov',
            'about', 'contact', 'home', 'page', 'index', 'html', 'php', 'asp'
        }
        
        # 提取单词
        words = re.findall(r'\b[a-zA-Z]{3,}\b', str(text).lower())
        return [w for w in words if w not in stop_words and len(w) >= min_length]
    
    def analyze_webinar(self, df: pd.DataFrame, company_name: str) -> Dict:
        """分析Webinar内容"""
        webinar_df = df[df['content_type'] == 'webinar'].copy() if 'content_type' in df.columns else pd.DataFrame()
        
        if webinar_df.empty:
            return {
                'count': 0,
                'keywords': [],
                'paths': [],
                'themes': []
            }
        
        # 提取关键词
        all_keywords = []
        if 'path' in webinar_df.columns:
            for path in webinar_df['path'].dropna():
                all_keywords.extend(self.extract_keywords(str(path)))
        elif 'path_segments' in webinar_df.columns:
            for segments in webinar_df['path_segments'].dropna():
                all_keywords.extend(self.extract_keywords(str(segments)))
        
        keyword_counts = Counter(all_keywords)
        top_keywords = keyword_counts.most_common(20)
        
        # 路径分布
        paths = []
        if 'path' in webinar_df.columns:
            path_counts = webinar_df['path'].value_counts().head(10)
            paths = path_counts.to_dict()
        
        return {
            'count': len(webinar_df),
            'keywords': top_keywords,
            'paths': paths,
            'themes': []
        }
    
    def analyze_blog(self, df: pd.DataFrame, company_name: str) -> Dict:
        """分析Blog内容"""
        blog_df = df[df['content_type'] == 'blog'].copy() if 'content_type' in df.columns else pd.DataFrame()
        
        if blog_df.empty:
            return {
                'count': 0,
                'keywords': [],
                'paths': [],
                'themes': []
            }
        
        # 提取关键词
        all_keywords = []
        if 'path' in blog_df.columns:
            for path in blog_df['path'].dropna():
                all_keywords.extend(self.extract_keywords(str(path)))
        elif 'path_segments' in blog_df.columns:
            for segments in blog_df['path_segments'].dropna():
                all_keywords.extend(self.extract_keywords(str(segments)))
        
        keyword_counts = Counter(all_keywords)
        top_keywords = keyword_counts.most_common(20)
        
        # 路径分布
        paths = []
        if 'path' in blog_df.columns:
            path_counts = blog_df['path'].value_counts().head(10)
            paths = path_counts.to_dict()
        
        return {
            'count': len(blog_df),
            'keywords': top_keywords,
            'paths': paths,
            'themes': []
        }
    
    def analyze_whitepaper_alternatives(self, df: pd.DataFrame, company_name: str) -> Dict:
        """分析White Paper替代内容类型"""
        # 查找可能的White Paper替代类型
        alternative_types = ['resource', 'newsroom', 'industry', 'legal']
        
        results = {}
        for alt_type in alternative_types:
            alt_df = df[df['content_type'] == alt_type].copy() if 'content_type' in df.columns else pd.DataFrame()
            if not alt_df.empty:
                results[alt_type] = {
                    'count': len(alt_df),
                    'keywords': [],
                    'paths': []
                }
                
                # 提取关键词
                all_keywords = []
                if 'path' in alt_df.columns:
                    for path in alt_df['path'].dropna():
                        all_keywords.extend(self.extract_keywords(str(path)))
                
                keyword_counts = Counter(all_keywords)
                results[alt_type]['keywords'] = keyword_counts.most_common(15)
        
        return results
    
    def generate_report(self, company_key: str) -> str:
        """生成单个公司的报告"""
        company_info = self.companies[company_key]
        company_name = company_info['name']
        
        # 加载数据
        df = self.load_company_data(company_key)
        if df is None:
            return None
        
        # 分析数据
        webinar_data = self.analyze_webinar(df, company_name)
        blog_data = self.analyze_blog(df, company_name)
        whitepaper_data = self.analyze_whitepaper_alternatives(df, company_name)
        
        # 生成报告
        report = f"""# {company_name} Webinar、Blog、White Paper 深度分析

**分析日期**: {datetime.now().strftime('%Y-%m-%d')}  
**分析方式**: 数据统计分析 + 网站结构分析  
**分析框架**: 《Breakthrough Advertising》意识层级理论

---

## 📋 执行摘要

{company_name}在Webinar、Blog和White Paper三个内容类型上的表现分析。本报告深入分析这三种内容类型的策略、主题分布、意识层级定位和竞争价值。

---

## 🎯 一、Webinar深度分析

### 1.1 规模与分布

**核心数据**：
- **总Webinar数**: {webinar_data['count']}个
"""

        if webinar_data['count'] > 0:
            report += f"""
**主要路径分布**：
"""
            for path, count in list(webinar_data['paths'].items())[:10]:
                report += f"- {path}: {count}页\n"
            
            report += f"""
### 1.2 主题分布分析

**Webinar关键词Top 20**（基于URL分析）：
"""
            for i, (keyword, count) in enumerate(webinar_data['keywords'][:20], 1):
                report += f"{i}. {keyword}({count})\n"
        else:
            report += """
**说明**：未发现明确的Webinar内容，可能：
- Webinar内容整合在其他内容类型中（如Resources、Events）
- 使用不同的命名方式（如Webinars、Online Events、Virtual Events）
- 尚未建立Webinar内容体系
"""

        report += f"""
---

## 📝 二、Blog深度分析

### 2.1 规模与分布

**核心数据**：
- **Blog数量**: {blog_data['count']}篇
"""

        if blog_data['count'] > 0:
            report += f"""
**主要路径分布**：
"""
            for path, count in list(blog_data['paths'].items())[:10]:
                report += f"- {path}: {count}页\n"
            
            report += f"""
### 2.2 Blog关键词分析

**Blog关键词Top 20**（基于URL分析）：
"""
            for i, (keyword, count) in enumerate(blog_data['keywords'][:20], 1):
                report += f"{i}. {keyword}({count})\n"
        else:
            report += """
**说明**：未发现明确的Blog内容，可能：
- Blog内容整合在其他内容类型中（如News、Press、Insights）
- 使用不同的命名方式（如Articles、Stories、Perspectives）
- 尚未建立Blog内容体系
"""

        report += f"""
---

## 📄 三、White Paper深度分析

### 3.1 替代内容类型分析

虽然未找到明确的"White Paper"内容，但{company_name}可能有以下替代内容类型：
"""

        if whitepaper_data:
            for alt_type, alt_data in whitepaper_data.items():
                type_name = alt_type.replace('_', ' ').title()
                report += f"""
#### {type_name}（{alt_data['count']}个）

**核心数据**：
- **数量**: {alt_data['count']}个
- **说明**: 可能包含深度分析内容，类似White Paper

**关键词Top 15**：
"""
                for i, (keyword, count) in enumerate(alt_data['keywords'][:15], 1):
                    report += f"{i}. {keyword}({count})\n"
        else:
            report += """
**说明**：未发现明确的White Paper或替代内容类型，可能：
- White Paper内容整合在Resources、Newsroom或其他内容类型中
- 使用不同的命名方式（如Industry Reports、Technical Documentation、Research Papers）
- 尚未建立White Paper内容体系
"""

        report += f"""
---

## 📊 四、内容策略总结

### 4.1 内容资产规模

| 内容类型 | 数量 | 说明 |
|---------|------|------|
| **Webinar** | {webinar_data['count']}个 | {'已建立Webinar内容体系' if webinar_data['count'] > 0 else '未发现明确Webinar内容'} |
| **Blog** | {blog_data['count']}篇 | {'已建立Blog内容体系' if blog_data['count'] > 0 else '未发现明确Blog内容'} |
| **White Paper替代** | {sum([d['count'] for d in whitepaper_data.values()])}个 | {'已建立替代内容体系' if whitepaper_data else '未发现明确替代内容'} |

### 4.2 意识层级覆盖

基于《Breakthrough Advertising》的5个意识层级：

| 意识层级 | 内容类型 | 丰富度 | 评估 |
|---------|---------|--------|------|
| **Unaware（最不意识）** | Blog、News | {'⭐⭐⭐' if blog_data['count'] > 50 else '⭐⭐' if blog_data['count'] > 0 else '⭐'} | {'良好' if blog_data['count'] > 50 else '一般' if blog_data['count'] > 0 else '不足'} |
| **Problem Aware（问题意识）** | Industry Reports、Problem-Solution Content | {'⭐⭐⭐' if whitepaper_data else '⭐⭐'} | {'良好' if whitepaper_data else '一般'} |
| **Solution Aware（解决方案意识）** | Webinar、Resources | {'⭐⭐⭐' if webinar_data['count'] > 20 else '⭐⭐' if webinar_data['count'] > 0 else '⭐'} | {'良好' if webinar_data['count'] > 20 else '一般' if webinar_data['count'] > 0 else '不足'} |
| **Product Aware（产品意识）** | Product Pages、Resources | ⭐⭐⭐ | 良好 |
| **Most Aware（最意识）** | Contact Forms、Demo | ⭐⭐ | 一般 |

### 4.3 关键发现

"""
        
        findings = []
        if webinar_data['count'] > 0:
            findings.append(f"✅ **Webinar内容体系**：已建立{webinar_data['count']}个Webinar内容")
        else:
            findings.append("⚠️ **Webinar内容体系**：未发现明确的Webinar内容，建议建立Webinar计划")
        
        if blog_data['count'] > 0:
            findings.append(f"✅ **Blog内容体系**：已建立{blog_data['count']}篇Blog内容")
        else:
            findings.append("⚠️ **Blog内容体系**：未发现明确的Blog内容，建议建立Blog计划")
        
        if whitepaper_data:
            findings.append(f"✅ **White Paper替代内容**：已建立{sum([d['count'] for d in whitepaper_data.values()])}个替代内容")
        else:
            findings.append("⚠️ **White Paper替代内容**：未发现明确的替代内容，建议建立深度内容体系")
        
        report += "\n".join(findings)
        
        report += f"""

---

**报告完成日期**: {datetime.now().strftime('%Y-%m-%d')}  
**数据来源**: output_data/{company_key}_analyzed.csv  
**下一步**: 建议结合网站实地调研，进一步验证和丰富分析内容
"""
        
        return report
    
    def generate_all_reports(self):
        """生成所有公司的报告"""
        generated = []
        failed = []
        
        for company_key in self.companies.keys():
            try:
                print(f"正在生成 {self.companies[company_key]['name']} 的报告...")
                report = self.generate_report(company_key)
                
                if report:
                    # 保存报告
                    company_name = self.companies[company_key]['name']
                    filename = f"{company_name.replace(' ', '_')}_Webinar_Blog_WhitePaper_深度分析.md"
                    filepath = self.company_analysis_dir / filename
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(report)
                    
                    generated.append(company_name)
                    print(f"✅ {company_name} 报告已生成")
                else:
                    failed.append(company_key)
                    print(f"⚠️ {company_key} 数据文件未找到")
            except Exception as e:
                failed.append(company_key)
                print(f"❌ {company_key} 报告生成失败: {e}")
        
        print(f"\n生成完成！成功: {len(generated)}个，失败: {len(failed)}个")
        if generated:
            print(f"成功生成的公司: {', '.join(generated)}")
        if failed:
            print(f"失败的公司: {', '.join(failed)}")


if __name__ == '__main__':
    generator = WebinarBlogWhitePaperReportGenerator()
    generator.generate_all_reports()

