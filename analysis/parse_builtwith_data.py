#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BuiltWith技术栈数据解析脚本

从BuiltWith报告文本中提取技术栈信息，整理到CSV表格中
"""

import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional


class BuiltWithParser:
    """BuiltWith报告解析器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.tech_data_dir = self.project_root / "Website Technology Profile Data"
        self.raw_data_dir = self.tech_data_dir / "raw_data"
        self.output_file = self.tech_data_dir / "builtwith_technology_profiles.csv"
        
        # 技术类别关键词映射
        self.tech_categories = {
            'CMS': ['wordpress', 'drupal', 'sitecore', 'contentful', 'strapi', 'ghost', 'joomla', 'typo3'],
            'Web Server': ['nginx', 'apache', 'iis', 'litespeed', 'caddy', 'tomcat'],
            'JavaScript Libraries': ['jquery', 'react', 'vue', 'angular', 'backbone', 'ember', 'svelte'],
            'Analytics': ['google analytics', 'adobe analytics', 'mixpanel', 'amplitude', 'segment', 'hotjar'],
            'Marketing Automation': ['marketo', 'hubspot', 'eloqua', 'pardot', 'salesforce marketing cloud', 'mailchimp'],
            'CDN': ['cloudflare', 'akamai', 'aws cloudfront', 'fastly', 'keycdn', 'maxcdn'],
            'Hosting': ['aws', 'azure', 'google cloud', 'heroku', 'digitalocean', 'linode', 'rackspace'],
            'SSL Certificate': ['let\'s encrypt', 'digicert', 'comodo', 'globalsign', 'sectigo'],
            'Email Service': ['sendgrid', 'mailchimp', 'amazon ses', 'mailgun', 'postmark', 'mandrill'],
            'Tag Management': ['google tag manager', 'tealium', 'adobe launch', 'segment', 'ensighten'],
            'Other Technologies': []
        }
        
        # 公司名称映射
        self.company_names = {
            'cognite': 'Cognite',
            'aveva': 'Aveva',
            'tulip': 'Tulip',
            'c3ai': 'C3 AI',
            'c3-ai': 'C3 AI',
            'yokogawa': 'Yokogawa',
            'emerson': 'Emerson',
            'abb': 'ABB',
            'siemens': 'Siemens',
            'rockwell': 'Rockwell Automation',
            'rockwell-automation': 'Rockwell Automation',
            'honeywell': 'Honeywell',
            'schneider': 'Schneider Electric',
            'schneider-electric': 'Schneider Electric',
            'bosch': 'Bosch',
            'ge': 'GE',
            'hitachi': 'Hitachi',
            'ignition': 'Ignition',
            'hivemq': 'HiveMQ',
            'umh': 'UMH',
            'univers': 'Univers'
        }
    
    def parse_builtwith_text(self, text: str) -> Dict[str, List[str]]:
        """
        解析BuiltWith报告文本，提取技术栈信息
        
        Args:
            text: BuiltWith报告文本内容
            
        Returns:
            包含各技术类别的字典
        """
        text_lower = text.lower()
        result = {
            'CMS': [],
            'Web Server': [],
            'JavaScript Libraries': [],
            'Analytics': [],
            'Marketing Automation': [],
            'CDN': [],
            'Hosting': [],
            'SSL Certificate': [],
            'Email Service': [],
            'Tag Management': [],
            'Other Technologies': []
        }
        
        # 按类别提取技术
        for category, keywords in self.tech_categories.items():
            if category == 'Other Technologies':
                continue
            
            found_techs = []
            for keyword in keywords:
                # 查找包含关键词的技术名称
                pattern = rf'\b{re.escape(keyword)}\b'
                if re.search(pattern, text_lower):
                    # 尝试提取完整的技术名称（可能需要根据实际格式调整）
                    found_techs.append(keyword.title())
            
            if found_techs:
                result[category] = list(set(found_techs))
        
        return result
    
    def load_raw_data(self) -> Dict[str, str]:
        """加载原始BuiltWith报告数据"""
        raw_data = {}
        
        if not self.raw_data_dir.exists():
            return raw_data
        
        for file_path in self.raw_data_dir.glob("*.txt"):
            company_key = file_path.stem.replace('_builtwith', '').replace('-builtwith', '')
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data[company_key] = f.read()
        
        return raw_data
    
    def process_all_companies(self) -> pd.DataFrame:
        """处理所有公司的BuiltWith数据"""
        raw_data = self.load_raw_data()
        
        if not raw_data:
            print("⚠️  未找到原始数据文件，请将BuiltWith报告保存到 raw_data/ 目录")
            return pd.DataFrame()
        
        results = []
        
        for company_key, text in raw_data.items():
            company_name = self.company_names.get(company_key.lower(), company_key.title())
            tech_profile = self.parse_builtwith_text(text)
            
            row = {'Company': company_name}
            for category, techs in tech_profile.items():
                row[category] = ', '.join(techs) if techs else ''
            
            results.append(row)
        
        df = pd.DataFrame(results)
        return df
    
    def save_to_csv(self, df: pd.DataFrame):
        """保存到CSV文件"""
        if df.empty:
            print("⚠️  没有数据可保存")
            return
        
        df.to_csv(self.output_file, index=False, encoding='utf-8-sig')
        print(f"✅ 数据已保存到: {self.output_file}")
        print(f"   共 {len(df)} 个公司的技术栈数据")
    
    def run(self):
        """运行解析流程"""
        print("=" * 80)
        print("BuiltWith技术栈数据解析")
        print("=" * 80)
        print()
        
        df = self.process_all_companies()
        
        if not df.empty:
            self.save_to_csv(df)
            print()
            print("📊 数据预览:")
            print(df.head())
        else:
            print()
            print("💡 使用说明:")
            print("1. 将BuiltWith报告内容复制到文本文件")
            print(f"2. 保存到: {self.raw_data_dir}/")
            print("3. 文件命名格式: {company}_builtwith.txt")
            print("4. 重新运行此脚本")


if __name__ == "__main__":
    parser = BuiltWithParser()
    parser.run()


