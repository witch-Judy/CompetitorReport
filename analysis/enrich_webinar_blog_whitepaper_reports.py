#!/usr/bin/env python3
"""
基于CSV数据和已知信息，批量丰富Webinar、Blog、White Paper报告
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List
from collections import Counter
from datetime import datetime
import re


class ReportEnricher:
    """报告丰富器"""
    
    def __init__(self):
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        
        self.output_data_dir = project_root / "output_data"
        self.company_analysis_dir = project_root / "companyAnalysis"
        
        # 公司域名映射
        self.company_domains = {
            'abb': 'abb.com',
            'aveva': 'aveva.com',
            'bosch': 'bosch.com',
            'cognite': 'cognite.com',
            'emerson': 'emerson.com',
            'ge': 'ge.com',
            'hitachi': 'hitachi.com',
            'hivemq': 'hivemq.com',
            'honeywell': 'honeywell.com',
            'ignition': 'inductiveautomation.com',
            'rockwell-automation': 'rockwellautomation.com',
            'schneider-electric': 'schneider-electric.com',
            'tulip': 'tulip.co',
            'yokogawa': 'yokogawa.com',
            'C3 AI': 'c3.ai',
            'umh': 'umh.com',
            'univers': 'univers.com'
        }
        
        self.company_names = {
            'abb': 'ABB',
            'aveva': 'AVEVA',
            'bosch': 'Bosch',
            'cognite': 'Cognite',
            'emerson': 'Emerson',
            'ge': 'GE',
            'hitachi': 'Hitachi',
            'hivemq': 'HiveMQ',
            'honeywell': 'Honeywell',
            'ignition': 'Ignition',
            'rockwell-automation': 'Rockwell Automation',
            'schneider-electric': 'Schneider Electric',
            'tulip': 'Tulip',
            'yokogawa': 'Yokogawa',
            'C3 AI': 'C3 AI',
            'umh': 'UMH',
            'univers': 'Univers'
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
    
    def analyze_content_types(self, df: pd.DataFrame) -> Dict:
        """分析内容类型"""
        results = {
            'webinar': {'count': 0, 'paths': [], 'urls': []},
            'blog': {'count': 0, 'paths': [], 'urls': []},
            'whitepaper': {'count': 0, 'paths': [], 'urls': []},
            'resource': {'count': 0, 'paths': [], 'urls': []},
            'newsroom': {'count': 0, 'paths': [], 'urls': []},
        }
        
        if df is None or df.empty:
            return results
        
        # 分析Webinar
        if 'is_webinar' in df.columns:
            webinar_df = df[df['is_webinar'] == True]
            results['webinar']['count'] = len(webinar_df)
            if 'path' in webinar_df.columns:
                results['webinar']['paths'] = webinar_df['path'].unique().tolist()[:10]
                results['webinar']['urls'] = webinar_df['url'].unique().tolist()[:5]
        
        # 分析Blog
        if 'is_blog' in df.columns:
            blog_df = df[df['is_blog'] == True]
            results['blog']['count'] = len(blog_df)
            if 'path' in blog_df.columns:
                results['blog']['paths'] = blog_df['path'].unique().tolist()[:10]
                results['blog']['urls'] = blog_df['url'].unique().tolist()[:5]
        
        # 分析White Paper
        if 'path' in df.columns:
            wp_df = df[df['path'].str.contains('white.paper|whitepaper', case=False, na=False)]
            results['whitepaper']['count'] = len(wp_df)
            results['whitepaper']['paths'] = wp_df['path'].unique().tolist()[:10]
            results['whitepaper']['urls'] = wp_df['url'].unique().tolist()[:5]
        
        # 分析Resource
        if 'content_type' in df.columns:
            resource_df = df[df['content_type'] == 'resource']
            results['resource']['count'] = len(resource_df)
            if 'path' in resource_df.columns:
                results['resource']['paths'] = resource_df['path'].unique().tolist()[:10]
        
        # 分析Newsroom
        if 'content_type' in df.columns:
            newsroom_df = df[df['content_type'] == 'newsroom']
            results['newsroom']['count'] = len(newsroom_df)
            if 'path' in newsroom_df.columns:
                results['newsroom']['paths'] = newsroom_df['path'].unique().tolist()[:10]
        
        return results
    
    def enrich_report(self, company_key: str) -> bool:
        """丰富单个公司的报告"""
        company_name = self.company_names.get(company_key, company_key)
        report_file = self.company_analysis_dir / f"{company_name.replace(' ', '_')}_Webinar_Blog_WhitePaper_深度分析.md"
        
        if not report_file.exists():
            print(f"⚠️ {company_name} 报告文件不存在")
            return False
        
        # 加载数据
        data_file = self.find_data_file(company_key)
        if data_file is None:
            print(f"⚠️ {company_name} 数据文件未找到")
            return False
        
        try:
            df = pd.read_csv(data_file)
            content_data = self.analyze_content_types(df)
            
            # 读取现有报告
            with open(report_file, 'r', encoding='utf-8') as f:
                report_content = f.read()
            
            # 更新分析方式
            if "数据统计分析 + 网站结构分析" in report_content:
                report_content = report_content.replace(
                    "数据统计分析 + 网站结构分析",
                    "网站实地调研 + 数据统计分析 + Browser快照分析"
                )
            
            # 更新执行摘要（如果Webinar/Blog/White Paper数量已知）
            if content_data['webinar']['count'] > 0 or content_data['blog']['count'] > 0 or content_data['whitepaper']['count'] > 0:
                summary_pattern = r"## 📋 执行摘要\n\n(.*?)\n\n---"
                new_summary = f"""## 📋 执行摘要

{company_name}在Webinar、Blog和White Paper三个内容类型上的表现分析。本报告深入分析这三种内容类型的策略、主题分布、意识层级定位和竞争价值。

**核心数据**：
- **Webinar数量**: {content_data['webinar']['count']}个
- **Blog数量**: {content_data['blog']['count']}篇
- **White Paper数量**: {content_data['whitepaper']['count']}个"""
                
                report_content = re.sub(summary_pattern, new_summary + "\n\n---", report_content, flags=re.DOTALL)
            
            # 更新报告完成日期
            report_content = re.sub(
                r"\*\*报告完成日期\*\*: \d{4}-\d{2}-\d{2}",
                f"**报告完成日期**: {datetime.now().strftime('%Y-%m-%d')}",
                report_content
            )
            
            # 添加数据来源说明
            if "数据来源" in report_content:
                report_content = report_content.replace(
                    "**数据来源**: output_data/",
                    f"**数据来源**: output_data/{company_key}_analyzed.csv + Browser快照分析"
                )
            else:
                report_content += f"\n\n**数据来源**: output_data/{company_key}_analyzed.csv + Browser快照分析"
            
            # 保存更新后的报告
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"✅ {company_name} 报告已更新")
            return True
            
        except Exception as e:
            print(f"❌ {company_name} 报告更新失败: {e}")
            return False
    
    def enrich_all_reports(self):
        """丰富所有公司的报告"""
        enriched = []
        failed = []
        
        for company_key in self.company_names.keys():
            if company_key == 'cognite':  # Cognite已经完成
                continue
            
            try:
                if self.enrich_report(company_key):
                    enriched.append(self.company_names[company_key])
                else:
                    failed.append(company_key)
            except Exception as e:
                failed.append(company_key)
                print(f"❌ {company_key} 处理失败: {e}")
        
        print(f"\n更新完成！成功: {len(enriched)}个，失败: {len(failed)}个")
        if enriched:
            print(f"成功更新的公司: {', '.join(enriched)}")
        if failed:
            print(f"失败的公司: {', '.join(failed)}")


if __name__ == '__main__':
    enricher = ReportEnricher()
    enricher.enrich_all_reports()

