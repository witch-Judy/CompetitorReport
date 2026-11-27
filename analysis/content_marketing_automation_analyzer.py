#!/usr/bin/env python3
"""
Content Marketing + Automation 深度分析器
三个阶段：流量入口侦察、转化机制拆解、自动化培育逻辑
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict
from typing import Dict, List
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent))


class ContentMarketingAutomationAnalyzer:
    """内容营销自动化分析器"""
    
    def __init__(self):
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        
        self.output_data_dir = project_root / "output_data"
        self.information_dir = project_root / "Information"
        self.insight_dir = project_root / "insight"
        self.reports_dir = self.insight_dir / "reports" / "content-marketing"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # 公司列表
        self.companies = [
            'abb', 'aveva', 'bosch', 'cognite', 'emerson', 'ge', 'hitachi',
            'hivemq', 'honeywell', 'ignition', 'rockwell-automation',
            'schneider-electric', 'siemens', 'tulip', 'yokogawa', 'c3-ai'
        ]
        
        # 公司名称映射
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
            'siemens': 'Siemens',
            'tulip': 'Tulip',
            'yokogawa': 'Yokogawa',
            'c3-ai': 'C3 AI'
        }
    
    def load_company_data(self, company_key: str) -> Dict:
        """加载公司数据"""
        company_name = self.company_names.get(company_key, company_key)
        
        data = {
            'company': company_key,
            'company_name': company_name,
            'navigation_tree': None,
            'seo_keywords': [],
            'content_types': {},
            'webinar_count': 0,
            'blog_count': 0,
            'total_pages': 0
        }
        
        # 加载导航树数据
        csv_file = self.output_data_dir / f"{company_name}_navigation_tree.csv"
        if csv_file.exists():
            df = pd.read_csv(csv_file)
            data['navigation_tree'] = df
            data['total_pages'] = len(df)
            
            # 提取SEO关键词（从URL路径）
            all_keywords = []
            
            # 尝试多种列名
            path_col = None
            for col in ['path', 'path_segments', 'url_path', 'segments', 'full_path']:
                if col in df.columns:
                    path_col = col
                    break
            
            if path_col:
                for path_seg in df[path_col].dropna():
                    path_str = str(path_seg).lower()
                    # 处理不同的分隔符
                    if '|' in path_str:
                        segments = path_str.split('|')
                    elif '/' in path_str:
                        segments = path_str.split('/')
                    else:
                        segments = [path_str]
                    
                    for s in segments:
                        s = s.strip()
                        # 过滤掉语言代码和常见路径
                        if s and len(s) > 2 and s not in ['en', 'us', 'mx', 'br', 'html', 'htm', 'www', 'com', 'org', 'net']:
                            # 移除文件扩展名和参数
                            s = s.split('.')[0].split('?')[0].split('#')[0]
                            if s and len(s) > 2:
                                all_keywords.append(s)
            
            # 也从URL中提取关键词
            url_col = None
            for col in ['page_url', 'url', 'link']:
                if col in df.columns:
                    url_col = col
                    break
            
            if url_col:
                for url in df[url_col].dropna():
                    url_str = str(url).lower()
                    # 提取URL路径部分
                    if '/' in url_str:
                        # 移除协议和域名
                        if '://' in url_str:
                            url_str = url_str.split('://', 1)[1]
                        if '/' in url_str:
                            url_str = url_str.split('/', 1)[1]
                        
                        url_parts = url_str.split('/')
                        for part in url_parts:
                            if part and len(part) > 2:
                                # 移除文件扩展名和参数
                                part = part.split('.')[0].split('?')[0].split('#')[0]
                                # 过滤掉语言代码和常见路径
                                if part and len(part) > 2 and part not in ['en', 'us', 'mx', 'br', 'html', 'htm', 'www', 'com', 'org', 'net']:
                                    all_keywords.append(part)
            
            # 统计关键词频率
            if all_keywords:
                from collections import Counter
                keyword_counts = Counter(all_keywords)
                data['seo_keywords'] = [{'keyword': k, 'count': v} for k, v in keyword_counts.most_common(50)]
            
            # 统计内容类型
            content_type_col = None
            for col in ['content_type', 'type', 'contentType', 'node_type']:
                if col in df.columns:
                    content_type_col = col
                    break
            
            if content_type_col:
                content_type_counts = df[content_type_col].value_counts().to_dict()
                data['content_types'] = content_type_counts
            
            # 统计Webinar和Blog
            if url_col:
                df_lower = df[url_col].astype(str).str.lower()
                data['webinar_count'] = len(df[df_lower.str.contains('webinar', na=False)])
                data['blog_count'] = len(df[df_lower.str.contains('blog', na=False)])
        
        return data
    
    def analyze_stage1_traffic_entry(self, company_data: Dict) -> Dict:
        """阶段一：流量入口侦察 (Top of Funnel)"""
        analysis = {
            'seo_strategy': {},
            'content_topics': {},
            'entry_points': []
        }
        
        # SEO关键词分析
        seo_keywords = company_data.get('seo_keywords', [])
        if seo_keywords:
            # 分类关键词
            industry_keywords = []
            product_keywords = []
            technical_keywords = []
            
            for kw_data in seo_keywords[:30]:  # Top 30
                kw = kw_data['keyword']
                count = kw_data['count']
                
                # 简单的关键词分类逻辑
                if any(term in kw for term in ['industry', 'sector', 'manufacturing', 'automation', 'industrial']):
                    industry_keywords.append({'keyword': kw, 'count': count})
                elif any(term in kw for term in ['product', 'solution', 'platform', 'system', 'software']):
                    product_keywords.append({'keyword': kw, 'count': count})
                elif any(term in kw for term in ['api', 'sdk', 'integration', 'developer', 'technical']):
                    technical_keywords.append({'keyword': kw, 'count': count})
                else:
                    industry_keywords.append({'keyword': kw, 'count': count})  # 默认归为行业关键词
            
            analysis['seo_strategy'] = {
                'industry_keywords': industry_keywords[:15],
                'product_keywords': product_keywords[:15],
                'technical_keywords': technical_keywords[:15],
                'total_unique_keywords': len(seo_keywords)
            }
        
        # 内容选题分析
        content_types = company_data.get('content_types', {})
        navigation_tree = company_data.get('navigation_tree')
        
        if navigation_tree is not None:
            df = navigation_tree
            
            # 找到URL列
            url_col = None
            for col in ['page_url', 'url', 'link']:
                if col in df.columns:
                    url_col = col
                    break
            
            # 找到content_type列
            content_type_col = None
            for col in ['content_type', 'type', 'contentType', 'node_type']:
                if col in df.columns:
                    content_type_col = col
                    break
            
            if url_col:
                # 分析内容类型分布（按销售漏斗）
                awareness_content = []
                consideration_content = []
                conversion_content = []
                loyalty_content = []
                
                awareness_keywords = ['blog', 'article', 'news', 'press-release', 'whitepaper', 'ebook', 'report']
                consideration_keywords = ['webinar', 'demo', 'case-study', 'customer-story', 'success-story', 'video']
                conversion_keywords = ['datasheet', 'specification', 'pricing', 'trial', 'contact', 'request-demo']
                loyalty_keywords = ['documentation', 'guide', 'tutorial', 'support', 'community', 'training']
                
                for _, row in df.iterrows():
                    url = str(row.get(url_col, '')).lower()
                    content_type = str(row.get(content_type_col, '') if content_type_col else '').lower()
                    combined = url + ' ' + content_type
                    
                    if any(kw in combined for kw in awareness_keywords):
                        awareness_content.append(url)
                    elif any(kw in combined for kw in consideration_keywords):
                        consideration_content.append(url)
                    elif any(kw in combined for kw in conversion_keywords):
                        conversion_content.append(url)
                    elif any(kw in combined for kw in loyalty_keywords):
                        loyalty_content.append(url)
                
                analysis['content_topics'] = {
                    'awareness': {
                        'count': len(awareness_content),
                        'percentage': len(awareness_content) / len(df) * 100 if len(df) > 0 else 0,
                        'types': ['blog', 'article', 'news', 'whitepaper', 'ebook']
                    },
                    'consideration': {
                        'count': len(consideration_content),
                        'percentage': len(consideration_content) / len(df) * 100 if len(df) > 0 else 0,
                        'types': ['webinar', 'demo', 'case-study', 'video']
                    },
                    'conversion': {
                        'count': len(conversion_content),
                        'percentage': len(conversion_content) / len(df) * 100 if len(df) > 0 else 0,
                        'types': ['datasheet', 'pricing', 'trial', 'contact']
                    },
                    'loyalty': {
                        'count': len(loyalty_content),
                        'percentage': len(loyalty_content) / len(df) * 100 if len(df) > 0 else 0,
                        'types': ['documentation', 'guide', 'support', 'training']
                    }
                }
                
                # 流量入口点分析
                entry_points = []
                
                df_lower = df[url_col].astype(str).str.lower()
                
                # Blog入口
                blog_urls = df[df_lower.str.contains('blog', na=False)]
                if len(blog_urls) > 0:
                    entry_points.append({
                        'type': 'Blog',
                        'count': len(blog_urls),
                        'description': '博客内容入口，用于SEO和思想领导力'
                    })
                
                # Webinar入口
                webinar_urls = df[df_lower.str.contains('webinar', na=False)]
                if len(webinar_urls) > 0:
                    entry_points.append({
                        'type': 'Webinar',
                        'count': len(webinar_urls),
                        'description': '网络研讨会入口，用于线索捕获'
                    })
                
                # Resource入口
                resource_urls = df[df_lower.str.contains('resource|download|whitepaper|ebook', na=False)]
                if len(resource_urls) > 0:
                    entry_points.append({
                        'type': 'Resource',
                        'count': len(resource_urls),
                        'description': '资源下载入口，用于内容营销'
                    })
            
            analysis['entry_points'] = entry_points
        
        return analysis
    
    def analyze_stage2_conversion_tech(self, company_data: Dict) -> Dict:
        """阶段二：转化与技术拆解 (Middle of Funnel)"""
        analysis = {
            'conversion_tools': [],
            'tech_stack': [],
            'engagement_mechanisms': [],
            'marketing_automation_tools': [],
            'detection_limitations': {}
        }
        
        navigation_tree = company_data.get('navigation_tree')
        
        if navigation_tree is not None:
            df = navigation_tree
            
            # 找到URL列
            url_col = None
            for col in ['page_url', 'url', 'link']:
                if col in df.columns:
                    url_col = col
                    break
            
            if url_col:
                df_lower = df[url_col].astype(str).str.lower()
                
                # 检测转化工具
                conversion_tools = []
                
                # 表单/联系页面
                form_urls = df[df_lower.str.contains('contact|form|request|register|signup|subscribe', na=False)]
                if len(form_urls) > 0:
                    conversion_tools.append({
                        'tool': 'Contact Forms',
                        'count': len(form_urls),
                        'purpose': '线索捕获和联系请求',
                        'detected': True
                    })
                
                # Demo/Trial页面
                demo_urls = df[df_lower.str.contains('demo|trial|try|test-drive', na=False)]
                if len(demo_urls) > 0:
                    conversion_tools.append({
                        'tool': 'Demo/Trial',
                        'count': len(demo_urls),
                        'purpose': '产品演示和试用',
                        'detected': True
                    })
                
                # 下载/资源页面
                download_urls = df[df_lower.str.contains('download|resource|whitepaper|ebook|case-study', na=False)]
                if len(download_urls) > 0:
                    conversion_tools.append({
                        'tool': 'Content Downloads',
                        'count': len(download_urls),
                        'purpose': '内容下载（通常需要表单填写）',
                        'detected': True
                    })
                
                # 计算器/工具页面
                tool_urls = df[df_lower.str.contains('calculator|tool|configurator|selector|wizard', na=False)]
                if len(tool_urls) > 0:
                    conversion_tools.append({
                        'tool': 'Interactive Tools',
                        'count': len(tool_urls),
                        'purpose': '交互式工具，用于用户参与和线索捕获',
                        'detected': True
                    })
            
                analysis['conversion_tools'] = conversion_tools
                
                # 技术栈推测（基于URL模式）
                tech_stack = []
                
                # API/SDK检测
                api_urls = df[df_lower.str.contains('api|sdk|developer|integration', na=False)]
                if len(api_urls) > 0:
                    tech_stack.append({
                        'technology': 'Developer API/SDK',
                        'evidence': f'{len(api_urls)}个API/SDK相关页面',
                        'purpose': '开发者集成和生态建设',
                        'confidence': 'high'
                    })
                
                # Portal检测
                portal_urls = df[df_lower.str.contains('portal|login|dashboard|my-account', na=False)]
                if len(portal_urls) > 0:
                    tech_stack.append({
                        'technology': 'Customer Portal',
                        'evidence': f'{len(portal_urls)}个Portal相关页面',
                        'purpose': '客户自助服务和账户管理',
                        'confidence': 'high'
                    })
                
                # 远程访问检测
                remote_urls = df[df_lower.str.contains('remote|iot|monitoring|cloud', na=False)]
                if len(remote_urls) > 0:
                    tech_stack.append({
                        'technology': 'Remote Access/IoT',
                        'evidence': f'{len(remote_urls)}个远程/IoT相关页面',
                        'purpose': '远程监控和IoT连接',
                        'confidence': 'medium'
                    })
                
                analysis['tech_stack'] = tech_stack
                
                # 参与机制
                engagement_mechanisms = []
                
                # Webinar注册
                if company_data.get('webinar_count', 0) > 0:
                    engagement_mechanisms.append({
                        'mechanism': 'Webinar Registration',
                        'count': company_data.get('webinar_count', 0),
                        'purpose': '通过Webinar捕获高质量线索',
                        'automation_level': 'high'
                    })
                
                # 内容下载
                if len(download_urls) > 0:
                    engagement_mechanisms.append({
                        'mechanism': 'Gated Content',
                        'count': len(download_urls),
                        'purpose': '通过内容下载获取联系信息',
                        'automation_level': 'high'
                    })
                
                # 社区/论坛
                community_urls = df[df_lower.str.contains('community|forum|discussion|support', na=False)]
                if len(community_urls) > 0:
                    engagement_mechanisms.append({
                        'mechanism': 'Community Engagement',
                        'count': len(community_urls),
                        'purpose': '用户社区和讨论',
                        'automation_level': 'medium'
                    })
                
                analysis['engagement_mechanisms'] = engagement_mechanisms
                
                # 营销自动化工具检测（基于URL模式）
                # ⚠️ 注意：这只是初步检测，无法检测实际使用的工具
                marketing_tools = []
                tool_keywords = {
                    'HubSpot': ['hubspot', 'hsforms', 'hs-script'],
                    'Marketo': ['marketo', 'munchkin', 'mktorest'],
                    'Salesforce': ['salesforce', 'pardot', 'exacttarget'],
                    'Pardot': ['pardot', 'pi.pardot'],
                    'Eloqua': ['eloqua', 'elq'],
                    'Mailchimp': ['mailchimp', 'list-manage'],
                    'Drift': ['drift'],
                    'Intercom': ['intercom']
                }
                
                for tool_name, keywords in tool_keywords.items():
                    tool_urls = df[df_lower.str.contains('|'.join(keywords), na=False)]
                    if len(tool_urls) > 0:
                        marketing_tools.append({
                            'tool': tool_name,
                            'detected_count': len(tool_urls),
                            'detection_method': 'URL模式匹配',
                            'confidence': 'low',  # URL匹配置信度低
                            'note': '⚠️ 仅基于URL路径检测，需要实际访问网站验证'
                        })
                
                analysis['marketing_automation_tools'] = marketing_tools
                
                # 检测限制说明
                analysis['detection_limitations'] = {
                    'current_method': 'URL路径模式匹配',
                    'limitations': [
                        '无法检测JavaScript代码中的工具',
                        '无法检测Cookie标识',
                        '无法检测表单代码',
                        '无法检测跟踪像素',
                        '无法检测API调用'
                    ],
                    'recommendations': [
                        '使用BuiltWith.com检测技术栈',
                        '使用Wappalyzer浏览器插件',
                        '手动访问网站检查开发者工具',
                        '检查Network请求和Cookie'
                    ]
                }
        
        return analysis
    
    def analyze_stage3_nurturing_logic(self, company_data: Dict) -> Dict:
        """阶段三：自动化培育逻辑 (Bottom of Funnel)"""
        # 这一部分留空，用户会手工来做
        analysis = {
            'nurturing_campaigns': [],
            'email_automation': [],
            'lead_scoring': [],
            'note': '此部分需要手工分析，包括：邮件自动化流程、线索评分逻辑、培育邮件序列等'
        }
        
        navigation_tree = company_data.get('navigation_tree')
        
        if navigation_tree is not None:
            df = navigation_tree
            
            # 找到URL列
            url_col = None
            for col in ['page_url', 'url', 'link']:
                if col in df.columns:
                    url_col = col
                    break
            
            if url_col:
                df_lower = df[url_col].astype(str).str.lower()
                
                # 可以检测一些可能的培育机制
                # 培训/认证页面
                training_urls = df[df_lower.str.contains('training|academy|learning|certification|course', na=False)]
                if len(training_urls) > 0:
                    analysis['nurturing_campaigns'].append({
                        'type': 'Training/Academy',
                        'count': len(training_urls),
                        'description': '培训和教育内容，用于客户培育'
                    })
                
                # 案例研究
                case_study_urls = df[df_lower.str.contains('case-study|customer-story|success-story', na=False)]
                if len(case_study_urls) > 0:
                    analysis['nurturing_campaigns'].append({
                        'type': 'Case Studies',
                        'count': len(case_study_urls),
                        'description': '案例研究，用于建立信任和展示价值'
                    })
        
        return analysis
    
    def generate_company_report(self, company_data: Dict, stage1: Dict, stage2: Dict, stage3: Dict) -> str:
        """生成单个公司的分析报告"""
        company_name = company_data['company_name']
        
        report = f"""# {company_name} - Content Marketing + Automation 深度分析

**分析日期**: {datetime.now().strftime('%Y-%m-%d')}
**数据来源**: 网站导航树结构分析

---

## 数据概览

- **总页面数**: {company_data.get('total_pages', 0):,}
- **Webinar数量**: {company_data.get('webinar_count', 0)}
- **Blog数量**: {company_data.get('blog_count', 0)}

---

## 阶段一：流量入口侦察 (Top of Funnel)

### SEO关键词策略

"""
        
        seo_strategy = stage1.get('seo_strategy', {})
        if seo_strategy:
            report += f"""
**总关键词数**: {seo_strategy.get('total_unique_keywords', 0)}

#### 行业关键词 (Top 15)
"""
            for kw_data in seo_strategy.get('industry_keywords', [])[:15]:
                report += f"- `{kw_data['keyword']}` ({kw_data['count']}次)\n"
            
            report += "\n#### 产品关键词 (Top 15)\n"
            for kw_data in seo_strategy.get('product_keywords', [])[:15]:
                report += f"- `{kw_data['keyword']}` ({kw_data['count']}次)\n"
            
            report += "\n#### 技术关键词 (Top 15)\n"
            for kw_data in seo_strategy.get('technical_keywords', [])[:15]:
                report += f"- `{kw_data['keyword']}` ({kw_data['count']}次)\n"
        
        report += "\n### 内容选题分布（按销售漏斗）\n\n"
        content_topics = stage1.get('content_topics', {})
        if content_topics:
            for stage, data in content_topics.items():
                stage_name = {
                    'awareness': 'Awareness (认知)',
                    'consideration': 'Consideration (考虑)',
                    'conversion': 'Conversion (转化)',
                    'loyalty': 'Loyalty (忠诚)'
                }.get(stage, stage)
                
                report += f"""
**{stage_name}**:
- 数量: {data.get('count', 0)}
- 占比: {data.get('percentage', 0):.1f}%
- 内容类型: {', '.join(data.get('types', []))}
"""
        
        report += "\n### 流量入口点\n\n"
        entry_points = stage1.get('entry_points', [])
        if entry_points:
            for ep in entry_points:
                report += f"""
- **{ep['type']}**: {ep['count']}个页面
  - {ep['description']}
"""
        else:
            report += "- 未检测到明显的流量入口点\n"
        
        report += "\n---\n\n## 阶段二：转化与技术拆解 (Middle of Funnel)\n\n"
        report += "> 💡 **数据解读说明**：这部分分析的是当访客进入网站后，公司用什么手段把他们留住并转化。包含4个维度：转化工具检测、技术栈推测、参与机制、营销自动化工具检测。\n\n"
        
        report += "### 转化工具检测\n\n"
        report += "> 📊 **含义解读**：\n"
        report += "> - **Contact Forms**: 网站上有多少个页面包含联系表单，用于线索捕获\n"
        report += "> - **Demo/Trial**: 有多少个页面提供产品演示或试用，让访客体验产品\n"
        report += "> - **Content Downloads**: 有多少个页面提供内容下载（白皮书、案例等），用内容换取联系信息（Gated Content）\n"
        report += "> - **Interactive Tools**: 有多少个页面包含交互式工具（计算器、配置器等），让访客参与互动\n\n"
        conversion_tools = stage2.get('conversion_tools', [])
        if conversion_tools:
            for tool in conversion_tools:
                report += f"""
- **{tool['tool']}**: {tool['count']}个页面
  - 用途: {tool['purpose']}
  - 检测状态: {'✅ 已检测' if tool.get('detected') else '❌ 未检测'}
"""
        else:
            report += "- 未检测到明显的转化工具\n"
        
        report += "\n### 技术栈推测\n\n"
        report += "> 📊 **含义解读**：\n"
        report += "> - **Developer API/SDK**: 有多少个页面涉及API/SDK，用于开发者集成和生态建设\n"
        report += "> - **Customer Portal**: 有多少个页面是客户门户（登录、账户管理等），用于客户自助服务\n"
        report += "> - **Remote Access/IoT**: 有多少个页面涉及远程访问和IoT，支持远程监控和管理\n\n"
        tech_stack = stage2.get('tech_stack', [])
        if tech_stack:
            for tech in tech_stack:
                confidence_icon = '🟢' if tech.get('confidence') == 'high' else '🟡' if tech.get('confidence') == 'medium' else '🔴'
                report += f"""
- **{tech['technology']}** {confidence_icon}
  - 证据: {tech['evidence']}
  - 用途: {tech['purpose']}
  - 置信度: {tech.get('confidence', 'unknown')}
"""
        else:
            report += "- 未检测到明显的技术栈特征\n"
        
        report += "\n### 参与机制\n\n"
        report += "> 📊 **含义解读**：\n"
        report += "> - **Webinar Registration**: 有多少个Webinar页面，通过Webinar捕获高质量线索。自动化程度high表示通常有自动化邮件跟进（注册确认、会前提醒、会后跟进等）\n"
        report += "> - **Gated Content**: 有多少个内容下载页面需要填写表单，用内容换取联系信息。自动化程度high表示下载后通常有自动化培育流程（感谢邮件、相关内容推荐、产品介绍等）\n"
        report += "> - **Community Engagement**: 有多少个社区/论坛页面，用于用户讨论和互动。自动化程度medium表示需要人工参与（社区管理、内容审核等）\n\n"
        engagement_mechanisms = stage2.get('engagement_mechanisms', [])
        if engagement_mechanisms:
            for mech in engagement_mechanisms:
                automation_level = mech.get('automation_level', 'unknown')
                automation_icon = '🟢' if automation_level == 'high' else '🟡' if automation_level == 'medium' else '🔴'
                report += f"""
- **{mech['mechanism']}** {automation_icon}
  - 数量: {mech['count']}
  - 用途: {mech['purpose']}
  - 自动化程度: {automation_level}
"""
        else:
            report += "- 未检测到明显的参与机制\n"
        
        report += "\n### 营销自动化工具检测\n\n"
        marketing_tools = stage2.get('marketing_automation_tools', [])
        if marketing_tools:
            report += "> ⚠️ **检测限制**：以下检测仅基于URL路径模式匹配，置信度较低。需要实际访问网站进行验证。\n\n"
            for tool in marketing_tools:
                confidence_icon = '🟡' if tool.get('confidence') == 'low' else '🟢' if tool.get('confidence') == 'high' else '🔴'
                report += f"""
- **{tool['tool']}** {confidence_icon}
  - 检测到: {tool['detected_count']}个相关URL
  - 检测方法: {tool['detection_method']}
  - 置信度: {tool['confidence']}
  - 说明: {tool.get('note', '')}
"""
        else:
            report += "> ⚠️ **未检测到营销自动化工具**\n\n"
            report += "**可能原因**：\n"
            report += "1. URL路径中不包含工具名称\n"
            report += "2. 工具通过JavaScript动态加载（无法从sitemap检测）\n"
            report += "3. 工具使用第三方域名（如hubspot.com、marketo.com）\n\n"
            report += "**建议检测方法**：\n"
            report += "- 使用BuiltWith.com或Wappalyzer进行检测\n"
            report += "- 手动访问网站检查开发者工具（F12）\n"
            report += "- 检查Network请求和Cookie\n"
            report += "- 查看页面源代码中的script标签\n"
        
        # 检测限制说明
        limitations = stage2.get('detection_limitations', {})
        if limitations:
            report += "\n### ⚠️ 检测方法限制说明\n\n"
            report += f"**当前检测方法**: {limitations.get('current_method', '未知')}\n\n"
            report += "**可以检测**:\n"
            report += "- URL中包含工具名称的情况（如 `/hubspot/`, `/marketo/`）\n"
            report += "- 域名匹配（如 `*.hubspot.com`）\n\n"
            report += "**无法检测的内容**:\n"
            for limitation in limitations.get('limitations', []):
                report += f"- {limitation}\n"
            report += "\n**推荐检测方法**:\n"
            report += "- **BuiltWith.com**: 访问 https://builtwith.com，输入公司域名查看技术栈\n"
            report += "- **Wappalyzer**: 安装浏览器插件，访问网站查看检测到的工具\n"
            report += "- **手动检测**: 访问网站，按F12打开开发者工具，检查Network请求、Cookie、HTML代码\n"
            report += "- **Network监控**: 检查第三方请求（如 `*.hubspot.com`, `*.marketo.com`）和Cookie（如 `hubspotutk`, `_mkto_trk`）\n"
        
        report += "\n---\n\n## 阶段三：自动化培育逻辑 (Bottom of Funnel)\n\n"
        report += "> ⚠️ 此部分需要手工分析，包括：邮件自动化流程、线索评分逻辑、培育邮件序列等\n\n"
        
        nurturing_campaigns = stage3.get('nurturing_campaigns', [])
        if nurturing_campaigns:
            report += "### 可检测的培育机制\n\n"
            for campaign in nurturing_campaigns:
                report += f"""
- **{campaign['type']}**: {campaign['count']}个页面
  - {campaign['description']}
"""
        else:
            report += "- 未检测到明显的培育机制（需要手工分析）\n"
        
        # 添加数据总结与竞争情报价值
        report += "\n---\n\n## 📊 数据总结与竞争情报价值\n\n"
        
        # 计算转化工具总数
        conversion_tools = stage2.get('conversion_tools', [])
        total_conversion_pages = sum(tool.get('count', 0) for tool in conversion_tools)
        
        # 计算技术栈特征
        tech_stack = stage2.get('tech_stack', [])
        has_api = any('API' in tech.get('technology', '') for tech in tech_stack)
        has_portal = any('Portal' in tech.get('technology', '') for tech in tech_stack)
        has_iot = any('IoT' in tech.get('technology', '') for tech in tech_stack)
        
        # 计算参与机制
        engagement_mechanisms = stage2.get('engagement_mechanisms', [])
        total_engagement = sum(mech.get('count', 0) for mech in engagement_mechanisms)
        
        report += f"### {company_name}的策略特点\n\n"
        
        if total_conversion_pages > 0:
            report += f"1. **转化工具丰富**：\n"
            tool_details = []
            for tool in conversion_tools:
                tool_details.append(f"{tool.get('count', 0)}个{tool.get('tool', '')}")
            report += f"   - {' + '.join(tool_details)} = {total_conversion_pages}个转化相关页面\n"
            report += "   - 说明：重视线索捕获和用户体验\n\n"
        
        if has_api or has_portal or has_iot:
            report += "2. **技术栈完善**：\n"
            tech_features = []
            if has_api:
                tech_features.append("API/SDK")
            if has_portal:
                tech_features.append("Portal")
            if has_iot:
                tech_features.append("IoT")
            if tech_features:
                report += f"   - {' + '.join(tech_features)} = 生态建设完善\n"
                report += "   - 说明：数字化程度高，重视生态建设\n\n"
        
        if total_engagement > 0:
            report += "3. **参与机制多样**：\n"
            engagement_details = []
            for mech in engagement_mechanisms:
                engagement_details.append(f"{mech.get('mechanism', '')} ({mech.get('count', 0)}个)")
            report += f"   - {' + '.join(engagement_details)} = 多渠道参与\n"
            report += "   - 说明：营销策略全面，重视内容营销\n\n"
        
        marketing_tools = stage2.get('marketing_automation_tools', [])
        if marketing_tools:
            report += "4. **自动化工具**：\n"
            report += "   - 需要进一步验证（当前检测置信度低）\n"
            report += "   - 建议使用BuiltWith或Wappalyzer验证\n\n"
        
        report += "### 竞争情报价值\n\n"
        report += "通过这些数据，可以：\n"
        report += "1. **识别转化策略**：了解公司如何捕获线索\n"
        report += "2. **学习技术栈**：了解公司的数字化能力\n"
        report += "3. **分析自动化程度**：了解公司的营销自动化水平\n"
        report += "4. **发现机会**：找到公司的薄弱环节或差异化机会\n"
        
        return report
    
    def generate_comprehensive_report(self):
        """生成综合分析报告"""
        print("=" * 80)
        print("Content Marketing + Automation 深度分析")
        print("=" * 80)
        print()
        
        all_analyses = []
        
        for company_key in self.companies:
            print(f"分析 {self.company_names.get(company_key, company_key)}...")
            
            # 加载数据
            company_data = self.load_company_data(company_key)
            
            # 三个阶段分析
            stage1 = self.analyze_stage1_traffic_entry(company_data)
            stage2 = self.analyze_stage2_conversion_tech(company_data)
            stage3 = self.analyze_stage3_nurturing_logic(company_data)
            
            # 生成单个公司报告
            company_report = self.generate_company_report(company_data, stage1, stage2, stage3)
            
            # 保存单个公司报告
            report_file = self.reports_dir / f"{company_data['company_name']}_Content_Marketing_Automation_分析.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(company_report)
            
            all_analyses.append({
                'company': company_data['company_name'],
                'company_key': company_key,
                'data': company_data,
                'stage1': stage1,
                'stage2': stage2,
                'stage3': stage3
            })
            
            print(f"  ✅ {company_data['company_name']}")
        
        print()
        print("生成综合分析报告...")
        
        # 生成综合对比报告
        comprehensive_report = self.generate_comparison_report(all_analyses)
        comprehensive_file = self.reports_dir / "Content_Marketing_Automation_综合分析报告.md"
        with open(comprehensive_file, 'w', encoding='utf-8') as f:
            f.write(comprehensive_report)
        
        print(f"  ✅ 综合分析报告: {comprehensive_file.name}")
        print()
        print("=" * 80)
        print("分析完成")
        print("=" * 80)
        print(f"共生成 {len(all_analyses) + 1} 份报告")
        print(f"报告位置: {self.reports_dir}")
    
    def generate_comparison_report(self, all_analyses: List[Dict]) -> str:
        """生成综合对比报告"""
        report = f"""# Content Marketing + Automation 综合分析报告

**分析日期**: {datetime.now().strftime('%Y-%m-%d')}
**分析公司数**: {len(all_analyses)}

---

## 执行摘要

本报告基于网站结构分析，对{len(all_analyses)}家竞品公司的Content Marketing + Automation策略进行了深度拆解。

### 分析框架

1. **阶段一：流量入口侦察 (Top of Funnel)**
   - SEO关键词策略
   - 内容选题分布
   - 流量入口点识别

2. **阶段二：转化与技术拆解 (Middle of Funnel)**
   - 转化工具检测
   - 技术栈推测
   - 参与机制分析

3. **阶段三：自动化培育逻辑 (Bottom of Funnel)**
   - 培育机制识别
   - ⚠️ 需要手工分析：邮件自动化、线索评分等

---

## 阶段一：流量入口侦察对比

### SEO关键词策略对比

| 公司 | 总关键词数 | 行业关键词占比 | 产品关键词占比 | 技术关键词占比 |
|------|-----------|--------------|--------------|--------------|
"""
        
        for analysis in all_analyses:
            company_name = analysis['company']
            stage1 = analysis['stage1']
            seo_strategy = stage1.get('seo_strategy', {})
            
            total_kw = seo_strategy.get('total_unique_keywords', 0)
            industry_kw = len(seo_strategy.get('industry_keywords', []))
            product_kw = len(seo_strategy.get('product_keywords', []))
            tech_kw = len(seo_strategy.get('technical_keywords', []))
            
            industry_pct = (industry_kw / total_kw * 100) if total_kw > 0 else 0
            product_pct = (product_kw / total_kw * 100) if total_kw > 0 else 0
            tech_pct = (tech_kw / total_kw * 100) if total_kw > 0 else 0
            
            report += f"| {company_name} | {total_kw} | {industry_pct:.1f}% | {product_pct:.1f}% | {tech_pct:.1f}% |\n"
        
        report += "\n### 内容漏斗分布对比\n\n"
        report += "| 公司 | Awareness | Consideration | Conversion | Loyalty |\n"
        report += "|------|-----------|--------------|-----------|----------|\n"
        
        for analysis in all_analyses:
            company_name = analysis['company']
            stage1 = analysis['stage1']
            content_topics = stage1.get('content_topics', {})
            
            awareness_pct = content_topics.get('awareness', {}).get('percentage', 0)
            consideration_pct = content_topics.get('consideration', {}).get('percentage', 0)
            conversion_pct = content_topics.get('conversion', {}).get('percentage', 0)
            loyalty_pct = content_topics.get('loyalty', {}).get('percentage', 0)
            
            report += f"| {company_name} | {awareness_pct:.1f}% | {consideration_pct:.1f}% | {conversion_pct:.1f}% | {loyalty_pct:.1f}% |\n"
        
        report += "\n---\n\n## 阶段二：转化与技术拆解对比\n\n"
        report += "### 转化工具使用情况\n\n"
        report += "| 公司 | Contact Forms | Demo/Trial | Content Downloads | Interactive Tools |\n"
        report += "|------|-------------|-----------|------------------|-----------------|\n"
        
        for analysis in all_analyses:
            company_name = analysis['company']
            stage2 = analysis['stage2']
            conversion_tools = stage2.get('conversion_tools', [])
            
            tools_dict = {tool['tool']: tool['count'] for tool in conversion_tools}
            
            contact = tools_dict.get('Contact Forms', 0)
            demo = tools_dict.get('Demo/Trial', 0)
            download = tools_dict.get('Content Downloads', 0)
            interactive = tools_dict.get('Interactive Tools', 0)
            
            report += f"| {company_name} | {contact} | {demo} | {download} | {interactive} |\n"
        
        report += "\n### 技术栈检测汇总\n\n"
        for analysis in all_analyses:
            company_name = analysis['company']
            stage2 = analysis['stage2']
            tech_stack = stage2.get('tech_stack', [])
            
            if tech_stack:
                report += f"\n**{company_name}**:\n"
                for tech in tech_stack:
                    report += f"- {tech['technology']}: {tech['evidence']}\n"
        
        report += "\n---\n\n## 阶段三：自动化培育逻辑\n\n"
        report += "> ⚠️ 此部分需要手工分析，包括：\n"
        report += "> - 邮件自动化流程（需要访问实际网站）\n"
        report += "> - 线索评分逻辑（需要CRM数据）\n"
        report += "> - 培育邮件序列（需要订阅测试）\n"
        report += "> - 行为触发机制（需要工具检测）\n\n"
        
        report += "### 可检测的培育机制\n\n"
        for analysis in all_analyses:
            company_name = analysis['company']
            stage3 = analysis['stage3']
            nurturing_campaigns = stage3.get('nurturing_campaigns', [])
            
            if nurturing_campaigns:
                report += f"\n**{company_name}**:\n"
                for campaign in nurturing_campaigns:
                    report += f"- {campaign['type']}: {campaign['count']}个页面\n"
        
        report += "\n---\n\n## 详细分析报告\n\n"
        report += "每个公司的详细分析报告请参考：\n\n"
        for analysis in all_analyses:
            company_name = analysis['company']
            report += f"- [{company_name}_Content_Marketing_Automation_分析.md](./{company_name}_Content_Marketing_Automation_分析.md)\n"
        
        report += "\n---\n"
        
        return report


if __name__ == "__main__":
    analyzer = ContentMarketingAutomationAnalyzer()
    analyzer.generate_comprehensive_report()

