#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BuiltWith技术栈数据自动提取脚本

使用浏览器工具访问BuiltWith页面并自动提取技术栈信息
"""

import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Set


class BuiltWithExtractor:
    """BuiltWith数据提取器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.tech_data_dir = self.project_root / "Website Technology Profile Data"
        self.output_file = self.tech_data_dir / "builtwith_technology_profiles.csv"
        
        # 技术类别关键词映射（更全面的列表）
        self.tech_keywords = {
            'CMS': {
                'wordpress', 'drupal', 'sitecore', 'contentful', 'strapi', 'ghost', 
                'joomla', 'typo3', 'squarespace', 'wix', 'shopify', 'magento'
            },
            'Web Server': {
                'nginx', 'apache', 'iis', 'litespeed', 'caddy', 'tomcat', 
                'gunicorn', 'uwsgi'
            },
            'JavaScript Libraries': {
                'jquery', 'react', 'vue', 'angular', 'backbone', 'ember', 
                'svelte', 'sentry', 'javascript modules', 'typescript'
            },
            'Analytics': {
                'google analytics', 'adobe analytics', 'omniture', 'sitecatalyst',
                'matomo', 'piwik', 'mixpanel', 'amplitude', 'segment', 'hotjar',
                'adobe experience cloud'
            },
            'Marketing Automation': {
                'marketo', 'hubspot', 'eloqua', 'pardot', 'salesforce marketing cloud',
                'adobe marketing cloud', 'mailchimp', 'constant contact', 'campaign monitor'
            },
            'CDN': {
                'cloudflare', 'akamai', 'aws cloudfront', 'azure edge', 'fastly',
                'keycdn', 'maxcdn', 'cdn', 'content delivery network'
            },
            'Hosting': {
                'aws', 'amazon web services', 'azure', 'microsoft azure', 
                'google cloud', 'gcp', 'heroku', 'digitalocean', 'linode',
                'rackspace', 'vultr', 'ovh'
            },
            'SSL Certificate': {
                'lets encrypt', 'let\'s encrypt', 'digicert', 'comodo', 
                'globalsign', 'sectigo', 'godaddy ssl'
            },
            'Email Service': {
                'sendgrid', 'mailchimp', 'amazon ses', 'mailgun', 'postmark',
                'mandrill', 'sparkpost', 'mailjet'
            },
            'Tag Management': {
                'google tag manager', 'gtm', 'adobe launch', 'adobe dtm',
                'adobe dynamic tag management', 'tealium', 'segment', 'ensighten',
                'matomo tag manager'
            },
            'Other Technologies': {
                'api gateway', 'adyen', 'stripe', 'paypal', 'facebook',
                'instagram', 'linkedin', 'twitter', 'youtube', 'dublin core',
                'utf-8', 'html5', 'open graph', 'twitter cards', 'google webmaster',
                'mobile compatible', 'responsive', 'pwa', 'service worker'
            }
        }
        
        # 公司域名映射
        self.company_domains = {
            'Cognite': 'cognite.com',
            'Aveva': 'aveva.com',
            'Tulip': 'tulip.co',
            'C3 AI': 'c3.ai',
            'Yokogawa': 'yokogawa.com',
            'Emerson': 'emerson.com',
            'ABB': 'abb.com',
            'Siemens': 'siemens.com',
            'Rockwell Automation': 'rockwellautomation.com',
            'Honeywell': 'honeywell.com',
            'Schneider Electric': 'schneider-electric.com',
            'Bosch': 'bosch.com',
            'GE': 'ge.com',
            'Hitachi': 'hitachi.com',
            'Ignition': 'inductiveautomation.com',
            'HiveMQ': 'hivemq.com',
            'UMH': 'umh.com',
            'Univers': 'univers.com'
        }
    
    def parse_snapshot_content(self, content: str) -> Dict[str, List[str]]:
        """
        从浏览器快照内容中解析技术栈信息
        
        Args:
            content: 浏览器快照的文本内容
            
        Returns:
            包含各技术类别的字典
        """
        content_lower = content.lower()
        result = {category: [] for category in self.tech_keywords.keys()}
        
        # 按类别提取技术
        for category, keywords in self.tech_keywords.items():
            found_techs = set()
            
            for keyword in keywords:
                # 使用正则表达式查找关键词（不区分大小写）
                pattern = rf'\b{re.escape(keyword)}\b'
                matches = re.finditer(pattern, content_lower, re.IGNORECASE)
                
                for match in matches:
                    # 尝试提取完整的技术名称
                    # 查找匹配前后的上下文，提取完整的技术名称
                    start = max(0, match.start() - 30)
                    end = min(len(content_lower), match.end() + 30)
                    context = content_lower[start:end]
                    
                    # 提取技术名称（可能需要根据实际格式调整）
                    tech_name = keyword.title()
                    
                    # 特殊处理一些技术名称
                    if keyword == 'omniture' or keyword == 'sitecatalyst':
                        tech_name = 'Omniture SiteCatalyst (Adobe Analytics)'
                    elif keyword == 'adobe marketing cloud':
                        tech_name = 'Adobe Marketing Cloud'
                    elif keyword == 'adobe launch':
                        tech_name = 'Adobe Launch'
                    elif keyword == 'adobe dtm' or keyword == 'adobe dynamic tag management':
                        tech_name = 'Adobe Dynamic Tag Management'
                    elif keyword == 'azure edge':
                        tech_name = 'Azure Edge'
                    elif keyword == 'api gateway':
                        tech_name = 'Amazon API Gateway'
                    
                    found_techs.add(tech_name)
            
            result[category] = sorted(list(found_techs))
        
        return result
    
    def load_existing_data(self) -> pd.DataFrame:
        """加载现有的技术栈数据"""
        if self.output_file.exists():
            return pd.read_csv(self.output_file)
        else:
            # 创建空的数据框
            companies = list(self.company_domains.keys())
            return pd.DataFrame({
                'Company': companies,
                **{category: [''] * len(companies) for category in self.tech_keywords.keys()}
            })
    
    def update_company_data(self, company_name: str, tech_profile: Dict[str, List[str]]):
        """更新指定公司的技术栈数据"""
        df = self.load_existing_data()
        
        if company_name not in df['Company'].values:
            # 添加新公司
            new_row = {'Company': company_name}
            for category in self.tech_keywords.keys():
                new_row[category] = ', '.join(tech_profile.get(category, []))
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            # 更新现有公司
            idx = df[df['Company'] == company_name].index[0]
            for category in self.tech_keywords.keys():
                techs = tech_profile.get(category, [])
                df.at[idx, category] = ', '.join(techs) if techs else ''
        
        df.to_csv(self.output_file, index=False, encoding='utf-8-sig')
        return df


if __name__ == "__main__":
    extractor = BuiltWithExtractor()
    print("BuiltWith数据提取器已初始化")
    print(f"输出文件: {extractor.output_file}")


