#!/usr/bin/env python3
"""
生成合并的内容营销+自动化分析报告
将所有公司的分析合并到一份报告中
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class MergedContentMarketingReportGenerator:
    """生成合并的内容营销报告"""
    
    def __init__(self):
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        
        self.output_data_dir = project_root / "output_data"
        self.insight_dir = project_root / "insight"
        self.reports_dir = self.insight_dir / "reports" / "content-marketing"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载SEM数据
        self.channel_data_file = project_root / "channel_data" / "competitor_marketing_channels1.csv"
        
        # 公司名称映射
        self.company_names = {
            'cognite': 'Cognite',
            'aveva': 'Aveva',
            'tulip': 'Tulip',
            'c3ai': 'C3 AI',
            'yokogawa': 'Yokogawa',
            'emerson': 'Emerson',
            'abb': 'ABB',
            'siemens': 'Siemens',
            'rockwell': 'Rockwell Automation',
            'honeywell': 'Honeywell',
            'schneider': 'Schneider Electric',
            'bosch': 'Bosch',
            'ge': 'GE',
            'hitachi': 'Hitachi',
            'ignition': 'Ignition',
            'hivemq': 'HiveMQ',
            'umh': 'UMH',
            'univers': 'Univers'
        }
        
        self.companies = list(self.company_names.keys())
        
        # 加载SEM数据
        self.sem_data = self.load_sem_data()
    
    def get_company_introductions(self) -> Dict:
        """获取公司简介"""
        return {
            'Cognite': {
                'description': 'Cognite是一家全球工业软件公司，专注于提供工业数据运营（Industrial DataOps）平台，帮助企业实现数字化转型。其核心产品Cognite Data Fusion®能够将工业数据进行整合和上下文化，支持实时决策和优化工作流程。',
                'summary': 'Cognite在工业数据运营领域具有领先优势，其数据融合平台为制造业数字化转型提供了强大的数据基础。'
            },
            'Aveva': {
                'description': 'AVEVA是一家全球领先的工程和工业软件公司，提供从设计、工程到运营的全生命周期解决方案。其产品广泛应用于能源、化工、海事等行业，帮助企业提高效率和可持续性。',
                'summary': 'AVEVA在工程软件和全生命周期解决方案方面具有深厚积累，为工业客户提供端到端的数字化支持。'
            },
            'Tulip': {
                'description': 'Tulip是一家专注于制造业的工业物联网（IIoT）平台提供商，旨在通过无代码应用程序帮助工厂实现数字化转型。其平台使一线工人能够创建和部署应用程序，以提高生产效率和质量。',
                'summary': 'Tulip的无代码IIoT平台降低了制造业数字化转型的门槛，让一线工人也能参与应用开发。'
            },
            'C3 AI': {
                'description': 'C3 AI是一家企业人工智能软件公司，提供用于开发、部署和运行AI应用程序的综合平台。其解决方案广泛应用于能源、制造、金融等行业，帮助企业实现数据驱动的决策和运营优化。',
                'summary': 'C3 AI在企业AI应用平台方面具有技术优势，为各行业提供端到端的AI解决方案。'
            },
            'Yokogawa': {
                'description': '横河电机（Yokogawa）是一家总部位于日本的跨国公司，专注于工业自动化和测试测量解决方案。其产品涵盖过程控制系统、测量仪器和工业服务，广泛应用于石油、化工、电力等行业。',
                'summary': 'Yokogawa在过程控制和测量仪器领域具有深厚技术积累，为工业客户提供可靠的自动化解决方案。'
            },
            'Emerson': {
                'description': '艾默生电气（Emerson Electric）是一家全球性的技术和工程公司，提供过程管理、工业自动化和商业及住宅解决方案。其产品和服务旨在帮助客户提高生产力和能源效率。',
                'summary': 'Emerson在过程管理和工业自动化领域具有全球影响力，为客户提供全面的技术和工程解决方案。'
            },
            'ABB': {
                'description': 'ABB是一家总部位于瑞士的跨国公司，专注于机器人、动力、重型电气设备和自动化技术领域。其产品和服务广泛应用于工业、交通、基础设施和电力等领域。',
                'summary': 'ABB在电气化和自动化领域具有全球领先地位，为工业、交通和基础设施提供全面的技术解决方案。'
            },
            'Siemens': {
                'description': '西门子（Siemens）是一家全球领先的技术公司，提供从自动化、数字化到电气化的全方位解决方案。其在工业4.0数字化转型方面处于领先地位，提供集成的硬件和软件解决方案，帮助企业实现智能制造。',
                'summary': 'Siemens在工业4.0和数字化转型方面处于行业领先地位，提供从硬件到软件的全方位智能制造解决方案。'
            },
            'Rockwell Automation': {
                'description': '罗克韦尔自动化（Rockwell Automation）是全球最大的专注于工业自动化和数字化转型的公司之一。其产品和服务涵盖控制系统、信息软件和工业服务，帮助客户提高生产力和可持续性。',
                'summary': 'Rockwell Automation在工业自动化领域具有全球领先地位，为客户提供全面的控制系统和数字化转型解决方案。'
            },
            'Honeywell': {
                'description': '霍尼韦尔（Honeywell）是一家多元化的技术和制造公司，业务涉及航空航天、楼宇技术、性能材料和安全解决方案等领域。其工业自动化产品和服务广泛应用于多个行业，提升运营效率和安全性。',
                'summary': 'Honeywell在多元化技术领域具有深厚积累，其工业自动化解决方案帮助客户提升运营效率和安全性。'
            },
            'Schneider Electric': {
                'description': '施耐德电气（Schneider Electric）是一家全球能源管理和自动化领域的领导者，提供从电力分配到自动化控制的全方位解决方案。其产品和服务旨在帮助客户实现能源效率和可持续发展。',
                'summary': 'Schneider Electric在能源管理和自动化领域具有全球领导地位，为客户提供可持续的能源解决方案。'
            },
            'Bosch': {
                'description': '博世（Bosch）是一家全球领先的技术和服务供应商，业务涵盖汽车技术、工业技术、消费品和能源及建筑技术等领域。其工业自动化产品和解决方案广泛应用于制造业，提高生产效率和质量。',
                'summary': 'Bosch在工业技术和自动化领域具有深厚技术积累，为制造业提供高效的生产解决方案。'
            },
            'GE': {
                'description': '通用电气（GE）是一家多元化的全球性企业，业务涉及航空、医疗、能源和数字工业等领域。其工业自动化和数字化解决方案帮助客户实现运营优化和创新。',
                'summary': 'GE在数字工业领域具有创新优势，为客户提供全面的工业自动化和数字化解决方案。'
            },
            'Hitachi': {
                'description': '日立（Hitachi）是一家总部位于日本的跨国公司，业务涵盖信息技术、能源、工业系统和社会基础设施等领域。其工业自动化和数字化解决方案广泛应用于多个行业，提升运营效率和可持续性。',
                'summary': 'Hitachi在工业系统和社会基础设施领域具有深厚积累，为客户提供全面的自动化和数字化解决方案。'
            },
            'Ignition': {
                'description': 'Ignition是Inductive Automation公司开发的SCADA和MES平台，提供统一的工业自动化解决方案。其平台具有强大的数据采集、可视化和控制能力，广泛应用于制造业和工业领域。',
                'summary': 'Ignition在SCADA和MES平台方面具有技术优势，为工业客户提供统一的自动化解决方案。'
            },
            'HiveMQ': {
                'description': 'HiveMQ是一家专注于MQTT消息代理和物联网连接的公司，提供企业级的MQTT平台解决方案。其产品广泛应用于工业物联网、车联网和智能设备连接场景。',
                'summary': 'HiveMQ在MQTT和物联网连接领域具有技术专长，为企业提供可靠的物联网消息传递解决方案。'
            },
            'UMH': {
                'description': 'UMH是一家专注于自助存储和物业管理解决方案的公司，提供数字化的存储和物业管理平台。其解决方案帮助客户提升运营效率和客户体验。',
                'summary': 'UMH在自助存储和物业管理领域具有专业优势，为客户提供数字化的运营管理解决方案。'
            },
            'Univers': {
                'description': 'Univers是一家专注于工业自动化和数字化解决方案的公司，为制造业客户提供全面的技术支持和咨询服务。',
                'summary': 'Univers在工业自动化和数字化咨询方面具有专业优势，为客户提供定制化的解决方案。'
            }
        }
    
    def get_company_strengths(self) -> Dict:
        """基于数据分析获取公司可取之处"""
        return {
            'Cognite': [
                '内容营销策略均衡：Awareness(60.8%)和Consideration(30.5%)占比合理，注重获客和培育',
                'Webinar资源丰富：148个Webinar，在考虑阶段内容投入较大',
                '内容类型多样化：包含blog、newsroom、customer_story等多种类型，内容矩阵完整'
            ],
            'Aveva': [
                'Blog内容丰富：376篇博客，在获客内容方面投入较大',
                '转化工具完善：150个Contact Forms和354个Demo/Trial，转化机制健全',
                '内容类型覆盖全面：包含blog、product、industry等多种类型'
            ],
            'Tulip': [
                'Blog内容突出：397篇博客，在内容营销方面投入较大',
                '内容类型丰富：包含blog、ebooks、case-studies等多种类型',
                '获客内容占比高：Awareness阶段占比94.8%，注重流量获取'
            ],
            'C3 AI': [
                '内容分布均衡：Awareness(64.8%)、Consideration(14.1%)、Conversion(13.2%)分布合理',
                '转化工具完善：257个Contact Forms和79个Demo/Trial',
                '技术栈完整：包含API/SDK和Remote/IoT能力'
            ],
            'Yokogawa': [
                '网站规模庞大：193,459个URL，内容资产丰富',
                '转化工具丰富：4,387个Contact Forms和3,198个Demo/Trial',
                '技术栈完善：1,038个API/SDK和5,130个Remote/IoT页面',
                'Webinar资源丰富：416个Webinar，在培育内容方面投入大'
            ],
            'Emerson': [
                '转化工具完善：239个Contact Forms和206个Demo/Trial',
                '技术栈完整：包含API/SDK和Remote/IoT能力',
                '内容类型覆盖全面：包含industry、product、company等多种类型'
            ],
            'ABB': [
                '转化内容占比高：Conversion阶段占比60.8%，注重转化优化',
                '技术栈完整：包含API/SDK、Portal和Remote/IoT能力',
                '内容类型覆盖全面：包含company、product、industry等多种类型'
            ],
            'Siemens': [
                '网站规模最大：33,476个URL，内容资产极其丰富',
                'Webinar资源丰富：1,952个Webinar，在培育内容方面投入巨大',
                '内容分布均衡：Awareness(24.1%)、Consideration(35.2%)、Conversion(32.5%)分布合理',
                '转化工具完善：2,074个Contact Forms和3,957个Demo/Trial',
                '技术栈完整：155个API/SDK、358个Portal和601个Remote/IoT页面',
                '内容类型覆盖全面：包含blog、webinar、product、industry等多种类型'
            ],
            'Rockwell Automation': [
                '暂无数据'
            ],
            'Honeywell': [
                '获客内容占比高：Awareness阶段占比81.6%，注重流量获取',
                '转化工具完善：179个Contact Forms和124个Demo/Trial',
                '社区参与度高：102个Community页面，注重用户社区建设'
            ],
            'Schneider Electric': [
                '暂无数据'
            ],
            'Bosch': [
                '获客内容占比高：Awareness阶段占比72.8%，注重流量获取',
                'Loyalty内容占比高：14.8%，注重客户留存',
                '内容类型覆盖全面：包含blog、product、industry等多种类型'
            ],
            'GE': [
                'Loyalty内容占比高：23.0%，注重客户留存和培训',
                '转化内容占比合理：Conversion阶段占比19.5%',
                '内容类型覆盖全面：包含company、product、industry等多种类型'
            ],
            'Hitachi': [
                '获客内容占比高：Awareness阶段占比94.3%，注重流量获取',
                '内容类型覆盖全面：包含blog、product、industry等多种类型',
                '转化工具完善：118个Contact Forms和63个Demo/Trial'
            ],
            'Ignition': [
                'Blog内容丰富：601篇博客，在内容营销方面投入较大',
                'Webinar资源丰富：186个Webinar，在培育内容方面投入大',
                '内容分布均衡：Awareness(62.0%)和Consideration(30.6%)占比合理',
                '技术栈完整：包含API/SDK、Portal和Remote/IoT能力'
            ],
            'HiveMQ': [
                'Blog内容突出：619篇博客，在内容营销方面投入巨大',
                'Webinar资源丰富：95个Webinar，在培育内容方面投入大',
                '获客内容占比高：Awareness阶段占比85.6%，注重流量获取',
                '技术栈完整：包含API/SDK和Remote/IoT能力'
            ],
            'UMH': [
                'Loyalty内容占比极高：75.8%，非常注重客户留存和培训',
                '转化工具完善：132个Demo/Trial',
                '网站规模较大：5,569个URL，内容资产丰富'
            ],
            'Univers': [
                '内容分布均衡：Awareness(67.7%)和Consideration(26.9%)占比合理',
                '转化工具完善：27个Contact Forms和30个Demo/Trial',
                '内容类型覆盖全面：包含blog、customer_story、product等多种类型'
            ]
        }
    
    def load_summary_data(self, company_key: str) -> Dict:
        """加载summary文件数据"""
        # 常见的语言代码列表（用于过滤）
        common_language_codes = {
            'en', 'de', 'fr', 'es', 'it', 'pt', 'nl', 'pl', 'ru', 'ja', 'zh', 'ko', 'ar', 'hi',
            'en-us', 'en-gb', 'zh-cn', 'ja-jp', 'pt-br', 'es-mx', 'fr-ca', 'en-au', 'en-ca',
            'us', 'cn', 'jp', 'kr', 'in', 'br', 'mx', 'ca', 'au', 'gb', 'uk', 'ie', 'nz', 'sg',
            'at', 'be', 'ch', 'cz', 'dk', 'fi', 'gr', 'hu', 'no', 'se', 'tr', 'bg', 'hr', 'ro',
            'sk', 'si', 'ee', 'lv', 'lt', 'is', 'lu', 'mt', 'cy', 'ae', 'sa', 'eg', 'za', 'ke',
            'th', 'vn', 'id', 'my', 'ph', 'tw', 'hk', 'mo', 'pk', 'bd', 'lk', 'mm', 'kh', 'la',
            'ww', 'eu', 'bh', 'kr', 'ro', 'hu', 'ch', 'en-eu', 'en-in', 'en-za', 'en-ae', 'en-mx',
            'en-ca', 'en-tw', 'en-hk', 'en-mm', 'en-my', 'en-ph', 'it-it', 'th-th', 'vi-vn',
            'id-id', 'zh-tw', 'zh-hk', 'fr-ca', 'es-mx', 'es-br', 'es-es', 'tr-tr', 'pl-pl',
            'de-de', 'fr-fr', 'ro-ro', 'sa-es'
        }
        
        company_name = self.company_names.get(company_key, company_key)
        # 尝试多种文件名格式
        info_dir = Path(__file__).parent.parent / "Information"
        possible_files = [
            info_dir / f"{company_key}_analyzed_summary.txt",
            info_dir / f"{company_name}_analyzed_summary.txt",
            info_dir / f"{company_name.replace(' ', '_')}_analyzed_summary.txt",
            info_dir / f"{company_name.replace(' ', '-')}_analyzed_summary.txt",
        ]
        # 特殊处理
        if company_key == 'c3ai':
            possible_files.insert(0, info_dir / "C3 AI_analyzed_summary.txt")
        elif company_key == 'rockwell':
            possible_files.insert(0, info_dir / "rockwell-automation_analyzed_summary.txt")
        elif company_key == 'schneider':
            possible_files.insert(0, info_dir / "schneider-electric_analyzed_summary.txt")
        
        summary_file = None
        for f in possible_files:
            if f.exists():
                summary_file = f
                break
        
        summary_data = {
            'total_urls': 0,
            'domains': [],
            'languages': {},
            'sections': {},
            'content_types': {},
            'years': {}
        }
        
        if summary_file.exists():
            with open(summary_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                current_section = None
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('='):
                        continue
                    
                    # Total URLs
                    if line.startswith('Total URLs:'):
                        try:
                            summary_data['total_urls'] = int(line.split(':')[1].strip())
                        except:
                            pass
                    
                    # Domains
                    elif line.startswith('Domains:'):
                        domains_str = line.split(':', 1)[1].strip()
                        summary_data['domains'] = [d.strip() for d in domains_str.split(',') if d.strip()]
                    
                    # Languages
                    elif line.startswith('Languages:'):
                        current_section = 'languages'
                    elif current_section == 'languages' and ':' in line and not line.startswith('Sections:'):
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            lang = parts[0].strip()
                            count_str = parts[1].strip()
                            # 过滤非语言代码：排除常见的非语言词
                            non_language_keywords = {
                                'blog', 'news', 'legal', 'tag', 'event', 'login', 'lp', 'plans', 'trial',
                                'demos', 'roles', 'team', 'abm', 'eng', 'buy', 'rent', 'media', 'other',
                                'sites', 'node', 'terms', 'faq', 'casl', 'lynn', 'home', 'india', 'apac',
                                'latam', 'korea', 'china', 'hey', 'mqtt', 'index', 'live', 'data', 'sip',
                                'svea', 'about', 'edge', 'ccpa', 'newsroom', 'customer_story', 'product',
                                'company', 'industry', 'resource', 'webinar', 'content', 'page', 'section',
                                'ww'  # ww不是标准语言代码
                            }
                            # 只保留真正的语言代码
                            if lang and lang.lower() not in non_language_keywords:
                                lang_lower = lang.lower()
                                # 检查是否是有效的语言代码格式
                                is_valid_lang = (
                                    (lang_lower in common_language_codes) or
                                    (lang.isalpha() and 2 <= len(lang) <= 5) or
                                    ('-' in lang and len(lang) <= 8 and lang.replace('-', '').isalpha())
                                )
                                if is_valid_lang:
                                    try:
                                        summary_data['languages'][lang] = int(count_str)
                                    except:
                                        pass
                    
                    # Sections
                    elif line.startswith('Sections:'):
                        current_section = 'sections'
                    elif current_section == 'sections' and ':' in line and not line.startswith('Content Types:'):
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            section = parts[0].strip()
                            count_str = parts[1].strip()
                            try:
                                summary_data['sections'][section] = int(count_str)
                            except:
                                pass
                    
                    # Content Types
                    elif line.startswith('Content Types:'):
                        current_section = 'content_types'
                    elif current_section == 'content_types' and ':' in line:
                        # 检查是否是下一个主要section的开始
                        if line.startswith('Years:'):
                            current_section = 'years'
                        elif not line.startswith('Content Types:'):  # 确保不是重复的Content Types标题
                            parts = line.split(':', 1)
                            if len(parts) == 2:
                                content_type = parts[0].strip()
                                count_str = parts[1].strip()
                                try:
                                    count = int(count_str)
                                    if count > 0:  # 只记录大于0的值
                                        summary_data['content_types'][content_type] = count
                                except:
                                    pass
                    
                    # Years
                    elif line.startswith('Years:'):
                        current_section = 'years'
                    elif current_section == 'years' and ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            year = parts[0].strip()
                            count_str = parts[1].strip()
                            try:
                                summary_data['years'][year] = int(count_str)
                            except:
                                pass
        
        return summary_data
    
    def load_company_data(self, company_key: str) -> Dict:
        """加载公司数据"""
        company_name = self.company_names.get(company_key, company_key)
        
        data = {
            'company': company_key,
            'company_name': company_name,
            'navigation_tree': None,
            'total_pages': 0,
            'webinar_count': 0,
            'blog_count': 0
        }
        
        # 加载summary数据
        summary_data = self.load_summary_data(company_key)
        data.update(summary_data)
        
        # 加载导航树数据
        # 尝试多种文件名格式
        possible_files = [
            self.output_data_dir / f"{company_name}_navigation_tree.csv",
            self.output_data_dir / f"{company_name.replace(' ', '-')}_navigation_tree.csv",
            self.output_data_dir / f"{company_name.replace(' ', '_')}_navigation_tree.csv",
            self.output_data_dir / f"{company_key}_navigation_tree.csv",
            self.output_data_dir / f"{company_key.replace(' ', '-')}_navigation_tree.csv",
        ]
        
        csv_file = None
        for f in possible_files:
            if f.exists():
                csv_file = f
                break
        
        # 如果output_data_dir中没找到，尝试structured_data目录
        if csv_file is None:
            possible_files_structured = [
                Path(__file__).parent.parent / "Information" / "structured_data" / f"{company_name}_navigation_tree.csv",
                Path(__file__).parent.parent / "Information" / "structured_data" / f"{company_name.replace(' ', '-')}_navigation_tree.csv",
                Path(__file__).parent.parent / "Information" / "structured_data" / f"{company_name.replace(' ', '_')}_navigation_tree.csv",
                Path(__file__).parent.parent / "Information" / "structured_data" / f"{company_key}_navigation_tree.csv",
            ]
            for f in possible_files_structured:
                if f.exists():
                    csv_file = f
                    break
        
        if csv_file.exists():
            df = pd.read_csv(csv_file)
            data['navigation_tree'] = df
            data['total_pages'] = len(df)
            
            # 统计Webinar和Blog - 优先使用URL匹配
            if 'page_url' in df.columns:
                df_lower = df['page_url'].astype(str).str.lower()
                webinar_count = len(df[df_lower.str.contains('webinar', na=False)])
                blog_count = len(df[df_lower.str.contains('blog', na=False)])
                
                # 如果CSV统计为0，但summary文件中有数据，使用summary文件的数据
                if webinar_count == 0 and 'webinar' in summary_data.get('content_types', {}):
                    webinar_count = summary_data['content_types']['webinar']
                if blog_count == 0 and 'blog' in summary_data.get('content_types', {}):
                    blog_count = summary_data['content_types']['blog']
                
                data['webinar_count'] = webinar_count
                data['blog_count'] = blog_count
            else:
                # 如果没有page_url列，使用summary文件的数据
                data['webinar_count'] = summary_data.get('content_types', {}).get('webinar', 0)
                data['blog_count'] = summary_data.get('content_types', {}).get('blog', 0)
        else:
            # 如果CSV文件不存在，使用summary文件的数据
            data['webinar_count'] = summary_data.get('content_types', {}).get('webinar', 0)
            data['blog_count'] = summary_data.get('content_types', {}).get('blog', 0)
        
        return data
    
    def load_sem_data(self) -> Dict:
        """加载SEM数据"""
        sem_data = {}
        
        channel_data_file = Path(__file__).parent.parent / "channel_data" / "competitor_marketing_channels1.csv"
        
        if not channel_data_file.exists():
            return sem_data
        
        try:
            df = pd.read_csv(channel_data_file)
            
            # 筛选SEM相关的数据
            sem_df = df[df['Channel'].str.upper() == 'SEM'].copy()
            
            if sem_df.empty:
                return sem_data
            
            # 按公司分组，收集所有关键词
            for brand in sem_df['Brand'].unique():
                if pd.isna(brand):
                    continue
                
                brand_sem = sem_df[sem_df['Brand'] == brand]
                keywords = []
                
                for _, row in brand_sem.iterrows():
                    if pd.notna(row.get('Value')):
                        keyword = str(row['Value']).strip()
                        if keyword:
                            keywords.append(keyword)
                
                if keywords:
                    sem_data[str(brand).strip()] = keywords
        
        except Exception as e:
            print(f"Error loading SEM data: {e}")
        
        return sem_data
    
    def analyze_company(self, company_data: Dict) -> Dict:
        """分析单个公司"""
        analysis = {
            'company': company_data['company_name'],
            'total_pages': company_data.get('total_pages', 0),
            'webinar_count': company_data.get('webinar_count', 0),
            'blog_count': company_data.get('blog_count', 0),
            'stage1': {},
            'stage2': {},
            'stage3': {}
        }
        
        navigation_tree = company_data.get('navigation_tree')
        if navigation_tree is None:
            return analysis
        
        df = navigation_tree
        
        # 找到URL列
        url_col = None
        for col in ['page_url', 'url', 'link']:
            if col in df.columns:
                url_col = col
                break
        
        if not url_col:
            return analysis
        
        df_lower = df[url_col].astype(str).str.lower()
        
        # 阶段一：流量入口侦察
        # SEO关键词（从URL路径中提取，过滤掉内容类型关键词）
        all_keywords = []
        
        # 需要过滤的内容类型关键词（这些不是SEO关键词）
        content_type_keywords = {
            'blog', 'news', 'press', 'press-release', 'article', 'whitepaper', 'ebook', 
            'report', 'webinar', 'video', 'demo', 'case-study', 'customer-story', 
            'success-story', 'datasheet', 'specification', 'documentation', 'guide', 
            'tutorial', 'support', 'community', 'training', 'contact', 'form', 'request',
            'download', 'resource', 'page', 'home', 'index', 'about', 'company', 'legal',
            'privacy', 'terms', 'cookie', 'sitemap', 'search', 'login', 'register', 'signup',
            'subscribe', 'newsletter', 'rss', 'feed', 'tag', 'category', 'archive', 'author',
            'ebooks', 'presentations', 'success-stories', 'webinars-videos', 'newsroom', 'docs'
        }
        
        # 需要过滤的语言代码和常见路径段
        filter_keywords = {
            'en', 'us', 'mx', 'br', 'cn', 'de', 'fr', 'es', 'it', 'pt', 'nl', 'pl', 'ru', 
            'ja', 'zh', 'ko', 'ar', 'hi', 'www', 'com', 'org', 'net', 'edu', 'html', 'htm',
            'php', 'asp', 'aspx', 'js', 'css', 'xml', 'json', 'pdf', 'jpg', 'png', 'gif',
            'global', 'local', 'regional', 'international', 'en-us', 'en-gb', 'zh-cn', 'ja-jp',
            'sa-es', 'be-fr', 'en-eu', 'en-in', 'en-mx', 'en-ca', 'about-us'
        }
        
        if 'path' in df.columns:
            for path_val in df['path'].dropna():
                path_str = str(path_val)
                segments = path_str.split('/')
                for seg in segments:
                    seg_clean = seg.lower().strip()
                    # 移除文件扩展名和参数
                    seg_clean = seg_clean.split('.')[0].split('?')[0].split('#')[0]
                    # 移除连字符后的部分（如 about-us -> about）
                    if '-' in seg_clean:
                        seg_clean = seg_clean.split('-')[0]
                    
                    # 过滤：长度>2，不是内容类型关键词，不是过滤关键词，不是纯数字
                    if (seg_clean and len(seg_clean) > 2 and 
                        seg_clean not in content_type_keywords and
                        seg_clean not in filter_keywords and
                        not seg_clean.isdigit() and
                        seg_clean.replace('-', '').isalpha()):
                        all_keywords.append(seg_clean)
        
        # 如果没有path列，尝试从URL中提取
        if not all_keywords and url_col:
            for url in df[url_col].dropna():
                url_str = str(url).lower()
                # 移除协议和域名
                if '://' in url_str:
                    url_str = url_str.split('://', 1)[1]
                if '/' in url_str:
                    url_str = url_str.split('/', 1)[1]  # 保留第一个/之后的内容
                
                # 提取路径段
                if '/' in url_str:
                    segments = url_str.split('/')
                    for seg in segments:
                        seg_clean = seg.split('.')[0].split('?')[0].split('#')[0].strip()
                        # 移除年份（4位数字）
                        if seg_clean.isdigit() and len(seg_clean) == 4:
                            continue
                        # 分割连字符和下划线
                        words = seg_clean.replace('-', ' ').replace('_', ' ').split()
                        for word in words:
                            word_clean = word.strip()
                            if (word_clean and len(word_clean) > 2 and 
                                word_clean not in content_type_keywords and
                                word_clean not in filter_keywords and
                                not word_clean.isdigit() and
                                word_clean.isalpha()):
                                all_keywords.append(word_clean)
        
        from collections import Counter
        keyword_counts = Counter(all_keywords)
        analysis['stage1']['top_keywords'] = [{'keyword': k, 'count': v} for k, v in keyword_counts.most_common(10)]
        
        # 内容选题分布（按销售漏斗）
        awareness_keywords = ['blog', 'article', 'news', 'press-release', 'whitepaper', 'ebook', 'report']
        consideration_keywords = ['webinar', 'demo', 'case-study', 'customer-story', 'success-story', 'video']
        conversion_keywords = ['datasheet', 'specification', 'pricing', 'trial', 'contact', 'request-demo']
        loyalty_keywords = ['documentation', 'guide', 'tutorial', 'support', 'community', 'training']
        
        awareness_count = 0
        consideration_count = 0
        conversion_count = 0
        loyalty_count = 0
        
        for _, row in df.iterrows():
            url = str(row.get(url_col, '')).lower()
            content_type = str(row.get('content_type', '')).lower()
            combined = url + ' ' + content_type
            
            if any(kw in combined for kw in awareness_keywords):
                awareness_count += 1
            elif any(kw in combined for kw in consideration_keywords):
                consideration_count += 1
            elif any(kw in combined for kw in conversion_keywords):
                conversion_count += 1
            elif any(kw in combined for kw in loyalty_keywords):
                loyalty_count += 1
        
        total_funnel = awareness_count + consideration_count + conversion_count + loyalty_count
        analysis['stage1']['funnel_distribution'] = {
            'awareness': {'count': awareness_count, 'pct': awareness_count/total_funnel*100 if total_funnel > 0 else 0},
            'consideration': {'count': consideration_count, 'pct': consideration_count/total_funnel*100 if total_funnel > 0 else 0},
            'conversion': {'count': conversion_count, 'pct': conversion_count/total_funnel*100 if total_funnel > 0 else 0},
            'loyalty': {'count': loyalty_count, 'pct': loyalty_count/total_funnel*100 if total_funnel > 0 else 0}
        }
        
        # 阶段二：转化与技术拆解
        # 转化工具
        form_urls = df[df_lower.str.contains('contact|form|request|register|signup|subscribe', na=False)]
        demo_urls = df[df_lower.str.contains('demo|trial|try|test-drive', na=False)]
        download_urls = df[df_lower.str.contains('download|resource|whitepaper|ebook|case-study', na=False)]
        tool_urls = df[df_lower.str.contains('calculator|tool|configurator|selector|wizard', na=False)]
        
        analysis['stage2']['conversion_tools'] = {
            'contact_forms': len(form_urls),
            'demo_trial': len(demo_urls),
            'content_downloads': len(download_urls),
            'interactive_tools': len(tool_urls),
            'total': len(form_urls) + len(demo_urls) + len(download_urls) + len(tool_urls)
        }
        
        # 技术栈
        api_urls = df[df_lower.str.contains('api|sdk|developer|developers', na=False)]
        portal_urls = df[df_lower.str.contains('portal|login|dashboard|my-account', na=False)]
        remote_urls = df[df_lower.str.contains('remote|iot|monitoring|cloud', na=False)]
        
        analysis['stage2']['tech_stack'] = {
            'api_sdk': len(api_urls),
            'portal': len(portal_urls),
            'remote_iot': len(remote_urls)
        }
        
        # 参与机制
        analysis['stage2']['engagement'] = {
            'webinar': company_data.get('webinar_count', 0),
            'gated_content': len(download_urls),
            'community': len(df[df_lower.str.contains('community|forum|discussion|support', na=False)])
        }
        
        # 阶段三：培育机制
        training_urls = df[df_lower.str.contains('training|academy|education|learn', na=False)]
        case_study_urls = df[df_lower.str.contains('case-study|case_study|casestudy|customer-story', na=False)]
        
        analysis['stage3']['nurturing'] = {
            'training': len(training_urls),
            'case_studies': len(case_study_urls)
        }
        
        return analysis
    
    def generate_merged_report(self) -> str:
        """生成合并报告"""
        report = f"""# Content Marketing + Automation 综合分析报告（合并版）

**生成日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**数据来源**: 网站导航树结构分析
**分析公司数**: {len(self.companies)}

---

## 📊 数据概览

"""
        
        all_analyses = []
        all_company_data = []
        
        for company_key in self.companies:
            company_data = self.load_company_data(company_key)
            all_company_data.append(company_data)
            analysis = self.analyze_company(company_data)
            all_analyses.append(analysis)
        
        # 生成详细的数据概览表格
        report += "### 基础统计\n\n"
        report += "| 公司 | Total URLs | Domains | Languages | Sections | Content Types | Years |\n"
        report += "|------|-----------|---------|-----------|----------|--------------|-------|\n"
        
        for company_data in all_company_data:
            company_name = company_data['company_name']
            total_urls = company_data.get('total_urls', company_data.get('total_pages', 0))
            domains = ', '.join(company_data.get('domains', [])) if company_data.get('domains') else '-'
            languages_dict = company_data.get('languages', {})
            languages_count = len([k for k in languages_dict.keys() if k])  # 过滤空字符串
            # 如果Languages为0，说明只使用了英文，应该显示为1
            if languages_count == 0:
                languages_count = 1
            sections_count = len([k for k in company_data.get('sections', {}).keys() if k])
            content_types_count = len([k for k in company_data.get('content_types', {}).keys() if k])
            years_count = len([k for k in company_data.get('years', {}).keys() if k])
            
            report += f"| {company_name} | {total_urls:,} | {domains} | {languages_count} | {sections_count} | {content_types_count} | {years_count} |\n"
        
        # 详细内容类型统计
        report += "\n### 内容类型详细统计\n\n"
        # 收集所有内容类型
        all_content_types = set()
        for company_data in all_company_data:
            all_content_types.update(company_data.get('content_types', {}).keys())
        
        if all_content_types:
            content_types_list = sorted([ct for ct in all_content_types if ct])  # 过滤空字符串
            if content_types_list:
                report += "| 公司 | " + " | ".join(content_types_list) + " |\n"
                report += "|------|" + "|".join(["---" for _ in content_types_list]) + "|\n"
                
                for company_data in all_company_data:
                    company_name = company_data['company_name']
                    content_types = company_data.get('content_types', {})
                    row = [company_name]
                    for ct in content_types_list:
                        count = content_types.get(ct, 0)
                        row.append(str(count))
                    report += "| " + " | ".join(row) + " |\n"
        
        report += "\n### Webinar和Blog统计\n\n"
        report += "| 公司 | Webinar数量 | Blog数量 |\n"
        report += "|------|------------|---------|\n"
        for company_data in all_company_data:
            company_name = company_data['company_name']
            webinar_count = company_data.get('webinar_count', 0)
            blog_count = company_data.get('blog_count', 0)
            report += f"| {company_name} | {webinar_count} | {blog_count} |\n"
        
        # Webinar关键词统计
        from collections import Counter
        report += "\n#### Webinar关键词统计（Top 10）\n\n"
        report += "| 公司 | Top 10 Webinar关键词 |\n"
        report += "|------|-------------------|\n"
        for company_data in all_company_data:
            company_name = company_data['company_name']
            navigation_tree = company_data.get('navigation_tree')
            webinar_keywords_str = '-'
            
            if navigation_tree is not None and 'page_url' in navigation_tree.columns:
                webinar_df = navigation_tree[navigation_tree['page_url'].str.contains('webinar', case=False, na=False)]
                if len(webinar_df) > 0:
                    # 从URL中提取关键词
                    keywords = []
                    # 需要过滤的词（停用词、协议、常见词）
                    filter_words = {
                        # 协议和域名相关
                        'https', 'http', 'www', 'com', 'org', 'net', 'edu', 'html', 'htm', 'php', 'asp', 'aspx',
                        # 常见英文停用词
                        'and', 'the', 'for', 'with', 'from', 'that', 'this', 'are', 'was', 'were', 'been', 'have',
                        'has', 'had', 'can', 'may', 'will', 'would', 'could', 'should', 'must', 'shall',
                        'how', 'what', 'when', 'where', 'why', 'who', 'which', 'your', 'our', 'their', 'its',
                        'all', 'any', 'some', 'many', 'more', 'most', 'much', 'very', 'too', 'also', 'just',
                        'only', 'even', 'still', 'yet', 'now', 'then', 'here', 'there', 'where', 'about',
                        'into', 'onto', 'upon', 'over', 'under', 'above', 'below', 'between', 'among', 'through',
                        'like', 'such', 'than', 'them', 'these', 'those', 'they', 'them', 'we', 'us', 'you',
                        'watch', 'now', 'about', 'key', 'steps', 'ensure', 'mastering', 'new', 'old', 'get', 'got',
                        'ask', 'anything', 'part', 'people', 'tags', 'featured', 'insights', 'articles'
                    }
                    
                    for url in webinar_df['page_url']:
                        if pd.notna(url):
                            # 提取URL路径中的关键词
                            url_lower = str(url).lower()
                            # 移除协议和域名
                            if '://' in url_lower:
                                url_lower = url_lower.split('://', 1)[1]
                            if '/' in url_lower:
                                # 移除域名部分（第一个/之前）
                                if '/' in url_lower:
                                    url_lower = '/' + '/'.join(url_lower.split('/')[1:])
                                path_parts = url_lower.split('/')
                                for part in path_parts:
                                    if part and 'webinar' not in part and len(part) > 2:
                                        # 移除文件扩展名和参数
                                        part = part.split('.')[0].split('?')[0].split('#')[0]
                                        # 分割连字符和下划线
                                        words = part.replace('-', ' ').replace('_', ' ').split()
                                        for word in words:
                                            word_clean = word.strip()
                                            # 过滤掉无意义的词和常见词
                                            if (word_clean and len(word_clean) > 2 and 
                                                word_clean not in filter_words and
                                                not word_clean.isdigit() and
                                                word_clean.isalpha()):
                                                keywords.append(word_clean)
                    
                    # 统计关键词频率
                    if keywords:
                        keyword_counts = Counter(keywords)
                        top_keywords = [f"{kw}({count})" for kw, count in keyword_counts.most_common(10)]
                        webinar_keywords_str = ', '.join(top_keywords) if top_keywords else '-'
            
            report += f"| {company_name} | {webinar_keywords_str} |\n"
        
        # Blog关键词统计
        report += "\n#### Blog关键词统计（Top 10）\n\n"
        report += "| 公司 | Top 10 Blog关键词 |\n"
        report += "|------|----------------|\n"
        for company_data in all_company_data:
            company_name = company_data['company_name']
            navigation_tree = company_data.get('navigation_tree')
            blog_keywords_str = '-'
            
            if navigation_tree is not None and 'page_url' in navigation_tree.columns:
                blog_df = navigation_tree[navigation_tree['page_url'].str.contains('blog', case=False, na=False)]
                if len(blog_df) > 0:
                    # 从URL中提取关键词
                    keywords = []
                    # 需要过滤的词（停用词、协议、常见词）
                    filter_words = {
                        # 协议和域名相关
                        'https', 'http', 'www', 'com', 'org', 'net', 'edu', 'html', 'htm', 'php', 'asp', 'aspx',
                        # 常见英文停用词
                        'and', 'the', 'for', 'with', 'from', 'that', 'this', 'are', 'was', 'were', 'been', 'have',
                        'has', 'had', 'can', 'may', 'will', 'would', 'could', 'should', 'must', 'shall',
                        'how', 'what', 'when', 'where', 'why', 'who', 'which', 'your', 'our', 'their', 'its',
                        'all', 'any', 'some', 'many', 'more', 'most', 'much', 'very', 'too', 'also', 'just',
                        'only', 'even', 'still', 'yet', 'now', 'then', 'here', 'there', 'where', 'about',
                        'into', 'onto', 'upon', 'over', 'under', 'above', 'below', 'between', 'among', 'through',
                        'like', 'such', 'than', 'them', 'these', 'those', 'they', 'them', 'we', 'us', 'you',
                        'watch', 'now', 'about', 'key', 'steps', 'ensure', 'mastering', 'new', 'old', 'get', 'got'
                    }
                    
                    for url in blog_df['page_url']:
                        if pd.notna(url):
                            url_str = str(url).lower()
                            # 移除协议
                            if '://' in url_str:
                                url_str = url_str.split('://', 1)[1]
                            # 移除域名部分（第一个/之前的所有内容）
                            if '/' in url_str:
                                url_str = url_str.split('/', 1)[1]  # 保留第一个/之后的内容
                            
                            # 提取路径部分的关键词
                            if '/' in url_str:
                                path_parts = url_str.split('/')
                                for part in path_parts:
                                    if part and 'blog' not in part and len(part) > 2:
                                        # 移除文件扩展名和参数
                                        part = part.split('.')[0].split('?')[0].split('#')[0]
                                        # 移除年份（4位数字）
                                        if part.isdigit() and len(part) == 4:
                                            continue
                                        # 分割连字符和下划线
                                        words = part.replace('-', ' ').replace('_', ' ').split()
                                        for word in words:
                                            word_clean = word.strip()
                                            # 过滤：长度>2，不是停用词，不是纯数字，是字母
                                            if (word_clean and len(word_clean) > 2 and 
                                                word_clean not in filter_words and
                                                not word_clean.isdigit() and
                                                word_clean.isalpha()):
                                                keywords.append(word_clean)
                    
                    # 统计关键词频率
                    if keywords:
                        keyword_counts = Counter(keywords)
                        top_keywords = [f"{kw}({count})" for kw, count in keyword_counts.most_common(10)]
                        blog_keywords_str = ', '.join(top_keywords) if top_keywords else '-'
            
            report += f"| {company_name} | {blog_keywords_str} |\n"
        
        # SEM关键词统计
        report += "\n### SEM（搜索引擎营销）关键词统计\n\n"
        report += "| 公司 | SEM关键词 |\n"
        report += "|------|----------|\n"
        
        for company_data in all_company_data:
            company_name = company_data['company_name']
            # 尝试多种公司名称匹配
            sem_keywords = self.sem_data.get(company_name, [])
            
            # 如果没找到，尝试其他可能的名称变体
            if not sem_keywords:
                # 尝试去掉空格、连字符等
                name_variants = [
                    company_name.replace(' ', ''),
                    company_name.replace('-', ' '),
                    company_name.replace(' ', '-'),
                ]
                for variant in name_variants:
                    if variant in self.sem_data:
                        sem_keywords = self.sem_data[variant]
                        break
            
            if sem_keywords:
                # 将关键词列表转换为字符串，用逗号分隔
                keywords_str = ', '.join(sem_keywords)
                # 如果关键词太多，截断显示
                if len(keywords_str) > 200:
                    keywords_str = keywords_str[:200] + '...'
                report += f"| {company_name} | {keywords_str} |\n"
            else:
                report += f"| {company_name} | - |\n"
        
        report += "\n---\n\n"
        
        # 阶段一：流量入口侦察
        report += "## 阶段一：流量入口侦察 (Top of Funnel)\n\n"
        
        # SEO关键词对比
        report += "### SEO关键词策略对比\n\n"
        report += "> **指标说明**：SEO关键词是从网站URL路径中提取的高频词汇，反映竞争对手通过内容优化想要获得排名的关键词。这些关键词揭示了他们的内容策略和主题覆盖范围，可以识别内容投资方向、发现SEO机会和内容缺口。通过对比分析，可以看出哪些关键词是竞争对手重点关注的，哪些可能是他们忽略的长尾关键词。\n\n"
        report += "| 公司 | Top 5 关键词 |\n"
        report += "|------|------------|\n"
        for analysis in all_analyses:
            keywords = analysis['stage1'].get('top_keywords', [])[:5]
            keyword_str = ', '.join([f"{kw['keyword']}({kw['count']})" for kw in keywords])
            report += f"| {analysis['company']} | {keyword_str} |\n"
        
        report += "\n### 内容选题分布（按销售漏斗）对比\n\n"
        report += "> **指标说明**：内容在销售漏斗各阶段的分布反映了营销预算分配和内容成熟度。如果竞品在Awareness阶段投入多，说明偏重获客；如果在Conversion阶段投入多，说明偏重转化。通过对比可以发现内容分布的特点和差异，识别不同公司在内容策略上的侧重点。\n\n"
        report += "| 公司 | Awareness | Consideration | Conversion | Loyalty |\n"
        report += "|------|-----------|--------------|-----------|---------|\n"
        for analysis in all_analyses:
            funnel = analysis['stage1'].get('funnel_distribution', {})
            report += f"| {analysis['company']} | {funnel.get('awareness', {}).get('pct', 0):.1f}% | {funnel.get('consideration', {}).get('pct', 0):.1f}% | {funnel.get('conversion', {}).get('pct', 0):.1f}% | {funnel.get('loyalty', {}).get('pct', 0):.1f}% |\n"
        
        # 阶段二：转化与技术拆解
        report += "\n---\n\n## 阶段二：转化与技术拆解 (Middle of Funnel)\n\n"
        report += "> 💡 **数据解读说明**：这部分分析的是当访客进入网站后，公司用什么手段把他们留住并转化。包含4个维度：转化工具检测、技术栈推测、参与机制、营销自动化工具检测。\n\n"
        
        # 转化工具对比
        report += "### 转化工具检测对比\n\n"
        report += "> **指标说明**：转化工具的数量和类型直接反映了一家公司的获客策略成熟度。联系表单多说明主动获取线索的意愿强，转化入口丰富；演示试用多通常意味着产品易用性好、体验门槛低，是产品导向的体现；内容下载多则说明内容营销成熟，通过高质量内容吸引和培育线索；交互工具（如计算器、配置器）多代表数字化执行力强，能够通过工具化提升用户体验。总体来看，转化工具总数反映了转化机制的完整度和丰富度。\n\n"
        report += "| 公司 | Contact Forms | Demo/Trial | Content Downloads | Interactive Tools | 总计 |\n"
        report += "|------|--------------|-----------|------------------|-----------------|------|\n"
        for analysis in all_analyses:
            tools = analysis['stage2'].get('conversion_tools', {})
            report += f"| {analysis['company']} | {tools.get('contact_forms', 0)} | {tools.get('demo_trial', 0)} | {tools.get('content_downloads', 0)} | {tools.get('interactive_tools', 0)} | {tools.get('total', 0)} |\n"
        
        # 技术栈对比
        report += "### 技术栈推测对比\n\n"
        report += "> **指标说明**：技术栈反映了公司的数字化成熟度和战略方向。API/SDK多说明重视开发者生态，平台化和生态化意图明显；Portal多意味着客户自助服务能力强，客户成功和运营效率的数字化程度高；Remote/IoT多则体现IoT和远程服务能力，数字化转型成熟。通过对比可以看出不同公司在技术能力建设上的侧重点和成熟度差异。\n\n"
        report += "| 公司 | API/SDK | Portal | Remote/IoT |\n"
        report += "|------|---------|--------|-----------|\n"
        for analysis in all_analyses:
            tech = analysis['stage2'].get('tech_stack', {})
            report += f"| {analysis['company']} | {tech.get('api_sdk', 0)} | {tech.get('portal', 0)} | {tech.get('remote_iot', 0)} |\n"
        
        # 参与机制对比
        report += "\n### 参与机制对比\n\n"
        report += "> **指标说明**：参与机制体现了内容营销的深度和用户粘性。Webinar多说明重视教育营销，通过深度内容建立品牌影响力；门控内容多意味着内容价值高，能够通过内容交换获取高质量线索；社区多则反映用户活跃度高，品牌忠诚度强。通过对比可以看出不同公司在用户参与和内容营销策略上的差异。\n\n"
        report += "| 公司 | Webinar | Gated Content | Community |\n"
        report += "|------|---------|--------------|----------|\n"
        for analysis in all_analyses:
            engagement = analysis['stage2'].get('engagement', {})
            report += f"| {analysis['company']} | {engagement.get('webinar', 0)} | {engagement.get('gated_content', 0)} | {engagement.get('community', 0)} |\n"
        
        # 阶段三：培育机制
        report += "\n---\n\n## 阶段三：自动化培育逻辑 (Bottom of Funnel)\n\n"
        report += "> **指标说明**：培育机制反映了客户成功和内容营销的深度。培训/学院多说明重视客户成功，通过知识传递提升客户技能和满意度；案例研究多则体现客户成功故事丰富，社会证明强，能够提升信任度和转化率。通过对比可以看出不同公司在客户培育和成功案例积累上的投入程度。\n\n"
        report += "| 公司 | Training/Academy | Case Studies |\n"
        report += "|------|----------------|-------------|\n"
        for analysis in all_analyses:
            nurturing = analysis['stage3'].get('nurturing', {})
            report += f"| {analysis['company']} | {nurturing.get('training', 0)} | {nurturing.get('case_studies', 0)} |\n"
        
        # 详细公司分析
        report += "\n---\n\n## 📋 各公司详细分析\n\n"
        
        # 公司简介和可取之处
        company_intros = self.get_company_introductions()
        company_strengths = self.get_company_strengths()
        
        for analysis in all_analyses:
            company_name = analysis['company']
            report += f"### {company_name}\n\n"
            
            # 公司简介（开头）
            intro = company_intros.get(company_name, {})
            if intro.get('description'):
                report += f"**公司简介**: {intro['description']}\n\n"
            
            report += f"**数据概览**:\n"
            report += f"- 总页面数: {analysis['total_pages']:,}\n"
            report += f"- Webinar数量: {analysis['webinar_count']}\n"
            report += f"- Blog数量: {analysis['blog_count']}\n\n"
            
            # 阶段一
            report += "**阶段一：流量入口侦察**\n"
            keywords = analysis['stage1'].get('top_keywords', [])[:10]
            report += "- Top关键词: " + ", ".join([f"{kw['keyword']}({kw['count']})" for kw in keywords]) + "\n"
            funnel = analysis['stage1'].get('funnel_distribution', {})
            report += f"- 内容分布: Awareness {funnel.get('awareness', {}).get('pct', 0):.1f}%, Consideration {funnel.get('consideration', {}).get('pct', 0):.1f}%, Conversion {funnel.get('conversion', {}).get('pct', 0):.1f}%, Loyalty {funnel.get('loyalty', {}).get('pct', 0):.1f}%\n\n"
            
            # 阶段二
            report += "**阶段二：转化与技术拆解**\n"
            tools = analysis['stage2'].get('conversion_tools', {})
            report += f"- 转化工具: Contact Forms {tools.get('contact_forms', 0)}, Demo/Trial {tools.get('demo_trial', 0)}, Content Downloads {tools.get('content_downloads', 0)}, Interactive Tools {tools.get('interactive_tools', 0)}\n"
            tech = analysis['stage2'].get('tech_stack', {})
            report += f"- 技术栈: API/SDK {tech.get('api_sdk', 0)}, Portal {tech.get('portal', 0)}, Remote/IoT {tech.get('remote_iot', 0)}\n"
            engagement = analysis['stage2'].get('engagement', {})
            report += f"- 参与机制: Webinar {engagement.get('webinar', 0)}, Gated Content {engagement.get('gated_content', 0)}, Community {engagement.get('community', 0)}\n\n"
            
            # 阶段三
            report += "**阶段三：培育机制**\n"
            nurturing = analysis['stage3'].get('nurturing', {})
            report += f"- Training/Academy: {nurturing.get('training', 0)}, Case Studies: {nurturing.get('case_studies', 0)}\n\n"
            
            # 可取之处（基于数据分析）
            strengths = company_strengths.get(company_name, [])
            if strengths:
                report += "**💡 可取之处**:\n"
                for strength in strengths:
                    report += f"- {strength}\n"
                report += "\n"
            
            report += "---\n\n"
        
        # 检测限制说明
        report += "## ⚠️ 检测方法限制说明\n\n"
        report += "**当前检测方法**: URL路径模式匹配\n\n"
        report += "**可以检测**:\n"
        report += "- URL中包含工具名称的情况（如 `/hubspot/`, `/marketo/`）\n"
        report += "- 域名匹配（如 `*.hubspot.com`）\n\n"
        report += "**无法检测的内容**:\n"
        report += "- JavaScript代码中的工具（需要查看页面源代码）\n"
        report += "- Cookie标识（需要访问网站）\n"
        report += "- 表单代码（需要查看HTML结构）\n"
        report += "- 跟踪像素（需要检查网络请求）\n"
        report += "- API调用（需要监控网络请求）\n\n"
        report += "**推荐检测方法**:\n"
        report += "- **BuiltWith.com**: 访问 https://builtwith.com，输入公司域名查看技术栈\n"
        report += "- **Wappalyzer**: 安装浏览器插件，访问网站查看检测到的工具\n"
        report += "- **手动检测**: 访问网站，按F12打开开发者工具，检查Network请求、Cookie、HTML代码\n"
        report += "- **Network监控**: 检查第三方请求（如 `*.hubspot.com`, `*.marketo.com`）和Cookie（如 `hubspotutk`, `_mkto_trk`）\n"
        
        return report
    
    def run(self):
        """运行生成器"""
        print("=" * 80)
        print("生成合并的内容营销+自动化分析报告")
        print("=" * 80)
        print()
        
        # 生成合并报告
        report_content = self.generate_merged_report()
        
        # 保存报告
        report_file = self.reports_dir / "Content_Marketing_Automation_综合分析报告_合并版.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ 合并报告已生成: {report_file}")
        print()
        
        # 删除单独的公司报告
        deleted_count = 0
        for company_key in self.companies:
            company_name = self.company_names.get(company_key, company_key)
            report_file = self.reports_dir / f"{company_name}_Content_Marketing_Automation_分析.md"
            if report_file.exists():
                report_file.unlink()
                deleted_count += 1
                print(f"  ✅ 已删除: {company_name}_Content_Marketing_Automation_分析.md")
        
        print()
        print(f"✅ 共删除 {deleted_count} 份单独报告")
        print(f"✅ 合并报告位置: {report_file}")


if __name__ == "__main__":
    generator = MergedContentMarketingReportGenerator()
    generator.run()

