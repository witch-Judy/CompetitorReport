#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量提取BuiltWith技术栈数据

使用浏览器工具自动访问所有公司的BuiltWith页面并提取技术栈信息
"""

import re
import pandas as pd
import time
from pathlib import Path
from typing import Dict, List, Set
from extract_builtwith_data import BuiltWithExtractor


class BatchBuiltWithExtractor:
    """批量BuiltWith数据提取器"""
    
    def __init__(self):
        self.extractor = BuiltWithExtractor()
        self.project_root = Path(__file__).parent.parent
        self.tech_data_dir = self.project_root / "Website Technology Profile Data"
        self.output_file = self.tech_data_dir / "builtwith_technology_profiles.csv"
    
    def parse_snapshot_for_techs(self, snapshot_content: str) -> Dict[str, List[str]]:
        """
        从浏览器快照内容中解析技术栈信息
        
        Args:
            snapshot_content: 浏览器快照的文本内容
            
        Returns:
            包含各技术类别的字典
        """
        content_lower = snapshot_content.lower()
        result = {category: [] for category in self.extractor.tech_keywords.keys()}
        
        # 技术名称映射（从BuiltWith页面提取的实际技术名称）
        tech_name_mapping = {
            # Analytics
            'omniture sitecatalyst': 'Omniture SiteCatalyst (Adobe Analytics)',
            'omniture': 'Omniture SiteCatalyst (Adobe Analytics)',
            'sitecatalyst': 'Omniture SiteCatalyst (Adobe Analytics)',
            'adobe analytics': 'Adobe Analytics',
            'matomo': 'Matomo',
            'piwik': 'Matomo',
            'google analytics': 'Google Analytics',
            
            # Marketing Automation
            'adobe marketing cloud': 'Adobe Marketing Cloud',
            'marketo': 'Marketo',
            'hubspot': 'HubSpot',
            'eloqua': 'Eloqua',
            'pardot': 'Pardot',
            'salesforce marketing cloud': 'Salesforce Marketing Cloud',
            
            # Tag Management
            'adobe launch': 'Adobe Launch',
            'adobe dynamic tag management': 'Adobe Dynamic Tag Management',
            'adobe dtm': 'Adobe Dynamic Tag Management',
            'google tag manager': 'Google Tag Manager',
            'gtm': 'Google Tag Manager',
            'tealium': 'Tealium',
            'matomo tag manager': 'Matomo Tag Manager',
            
            # JavaScript Libraries
            'sentry': 'Sentry',
            'javascript modules': 'JavaScript Modules',
            'javascript module': 'JavaScript Modules',
            'jquery': 'jQuery',
            'react': 'React',
            'vue': 'Vue.js',
            'angular': 'Angular',
            
            # CDN
            'azure edge': 'Azure Edge',
            'aws cloudfront': 'AWS CloudFront',
            'cloudflare': 'Cloudflare',
            'akamai': 'Akamai',
            
            # Hosting
            'azure': 'Azure',
            'aws': 'AWS',
            'amazon web services': 'AWS',
            'google cloud': 'Google Cloud',
            
            # Payment
            'adyen': 'Adyen',
            'stripe': 'Stripe',
            'paypal': 'PayPal',
            
            # Other
            'amazon api gateway': 'Amazon API Gateway',
            'api gateway': 'Amazon API Gateway',
        }
        
        # 按类别提取技术
        for category, keywords in self.extractor.tech_keywords.items():
            found_techs = set()
            
            for keyword in keywords:
                pattern = rf'\b{re.escape(keyword)}\b'
                if re.search(pattern, content_lower, re.IGNORECASE):
                    # 使用映射获取标准化的技术名称
                    tech_name = tech_name_mapping.get(keyword.lower(), keyword.title())
                    found_techs.add(tech_name)
            
            result[category] = sorted(list(found_techs))
        
        # 特殊处理：从CDN推断Hosting
        if 'Azure Edge' in result['CDN']:
            result['Hosting'].append('Azure (inferred from Azure Edge)')
        if 'AWS CloudFront' in result['CDN']:
            if 'AWS' not in result['Hosting']:
                result['Hosting'].append('AWS (inferred from AWS CloudFront)')
        
        return result
    
    def extract_company_tech_stack(self, company_name: str, domain: str) -> Dict[str, List[str]]:
        """
        提取单个公司的技术栈
        
        Args:
            company_name: 公司名称
            domain: 公司域名
            
        Returns:
            技术栈字典
        """
        print(f"\\n正在处理: {company_name} ({domain})")
        
        # 构建BuiltWith URL
        builtwith_url = f"https://builtwith.com/{domain}"
        
        try:
            # 使用浏览器工具访问页面
            # 注意：这里需要在实际调用时使用browser工具
            # 目前返回空结果，等待实际浏览器调用
            print(f"  URL: {builtwith_url}")
            print("  ⚠️  需要手动调用浏览器工具访问页面")
            
            return {category: [] for category in self.extractor.tech_keywords.keys()}
            
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            return {category: [] for category in self.extractor.tech_keywords.keys()}
    
    def batch_extract(self, companies: List[str] = None):
        """
        批量提取所有公司的技术栈
        
        Args:
            companies: 要处理的公司列表（None表示处理所有公司）
        """
        if companies is None:
            companies = list(self.extractor.company_domains.keys())
        
        print("=" * 80)
        print("批量提取BuiltWith技术栈数据")
        print("=" * 80)
        print(f"\\n共 {len(companies)} 个公司待处理")
        print()
        
        # 加载现有数据
        df = self.extractor.load_existing_data()
        
        for company_name in companies:
            if company_name not in self.extractor.company_domains:
                print(f"⚠️  跳过 {company_name}（未找到域名）")
                continue
            
            domain = self.extractor.company_domains[company_name]
            
            # 检查是否已有数据
            if company_name in df['Company'].values:
                existing_row = df[df['Company'] == company_name].iloc[0]
                has_data = any(pd.notna(existing_row[col]) and str(existing_row[col]).strip() 
                              for col in df.columns[1:])
                if has_data:
                    print(f"⏭️  跳过 {company_name}（已有数据）")
                    continue
            
            # 提取技术栈
            tech_profile = self.extract_company_tech_stack(company_name, domain)
            
            # 更新数据框
            self.extractor.update_company_data(company_name, tech_profile)
            
            # 延迟以避免请求过快
            time.sleep(2)
        
        print("\\n" + "=" * 80)
        print("✅ 批量提取完成")
        print("=" * 80)


if __name__ == "__main__":
    extractor = BatchBuiltWithExtractor()
    
    print("=" * 80)
    print("BuiltWith批量提取工具")
    print("=" * 80)
    print()
    print("📋 公司域名列表:")
    for company, domain in extractor.extractor.company_domains.items():
        print(f"  {company:20s} -> {domain}")
    print()
    print("💡 使用方法:")
    print("  此脚本需要配合浏览器工具使用")
    print("  请使用以下命令逐个处理公司，或修改脚本添加浏览器工具调用")
    print()
    print("  示例:")
    print("    python3 -c \"from analysis.batch_extract_builtwith import *; extractor = BatchBuiltWithExtractor(); extractor.extract_company_tech_stack('Siemens', 'siemens.com')\"")


