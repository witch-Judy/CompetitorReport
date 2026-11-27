#!/usr/bin/env python3
"""
生成公司档案：外部介绍 + 数据总结
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List
import sys

sys.path.insert(0, str(Path(__file__).parent))


class CompanyProfileGenerator:
    """公司档案生成器"""
    
    def __init__(self):
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        
        self.output_data_dir = project_root / "output_data"
        self.reference_dir = self.output_data_dir / "reference"
        self.insight_dir = project_root / "insight"
        self.insight_reports_dir = self.insight_dir / "reports"
        
        # 公司外部介绍（基于公开信息）
        self.company_profiles = {
            'c3-ai': {
                'name': 'C3 AI',
                'description': 'C3 AI是一家企业AI软件公司，提供企业级AI应用平台，帮助大型组织构建、部署和运营大规模AI应用。公司专注于工业AI、预测性维护、能源管理等领域，为制造业、能源、金融等行业提供AI解决方案。',
                'type': 'To B - 企业AI软件平台',
                'industry': 'AI/ML软件、企业软件',
                'founded': '2009年',
                'headquarters': '美国加州红木城'
            },
            'abb': {
                'name': 'ABB',
                'description': 'ABB是一家瑞士-瑞典跨国工业技术公司，专注于电气化、自动化、机器人和运动控制领域。ABB为工业、交通和基础设施行业提供产品、系统和服务，是全球领先的工业自动化解决方案提供商之一。',
                'type': 'To B - 工业自动化',
                'industry': '工业自动化、电气化、机器人',
                'founded': '1988年（由ASEA和BBC Brown Boveri合并）',
                'headquarters': '瑞士苏黎世'
            },
            'aveva': {
                'name': 'AVEVA',
                'description': 'AVEVA是一家英国工业软件公司，提供工程、规划和运营软件解决方案。公司专注于为流程工业（如化工、石油天然气、电力等）提供数字孪生、资产绩效管理、工程设计等软件平台。',
                'type': 'To B - 工业软件',
                'industry': '工业软件、工程软件、数字孪生',
                'founded': '1967年',
                'headquarters': '英国剑桥'
            },
            'bosch': {
                'name': 'Bosch',
                'description': '博世（Bosch）是一家德国跨国工程和技术公司，业务涵盖汽车零部件、工业技术、消费品和建筑技术。在工业自动化领域，博世提供智能制造、工业4.0解决方案、自动化系统等。',
                'type': 'To B - 工业自动化',
                'industry': '工业自动化、汽车零部件、智能制造',
                'founded': '1886年',
                'headquarters': '德国斯图加特'
            },
            'cognite': {
                'name': 'Cognite',
                'description': 'Cognite是一家挪威工业数据软件公司，提供工业数据平台Cognite Data Fusion，帮助工业企业整合、管理和分析运营数据。公司专注于为能源、制造业等行业提供数据驱动的洞察和AI应用。',
                'type': 'To B - 工业数据平台',
                'industry': '工业数据平台、工业AI、数字孪生',
                'founded': '2016年',
                'headquarters': '挪威奥斯陆'
            },
            'emerson': {
                'name': 'Emerson',
                'description': '艾默生（Emerson）是一家美国跨国工业技术公司，专注于自动化解决方案、商业和住宅解决方案。在工业自动化领域，艾默生提供过程控制、测量仪器、阀门和执行器等产品。',
                'type': 'To B - 工业自动化',
                'industry': '工业自动化、过程控制、测量仪器',
                'founded': '1890年',
                'headquarters': '美国密苏里州圣路易斯'
            },
            'ge': {
                'name': 'GE (General Electric)',
                'description': '通用电气（GE）是一家美国跨国工业公司，业务涵盖航空、电力、可再生能源、医疗保健等领域。在工业数字化方面，GE提供Predix工业互联网平台和数字解决方案。',
                'type': 'To B - 工业数字化',
                'industry': '工业互联网、数字孪生、工业软件',
                'founded': '1892年',
                'headquarters': '美国马萨诸塞州波士顿'
            },
            'hitachi': {
                'name': 'Hitachi',
                'description': '日立（Hitachi）是一家日本跨国工业公司，业务涵盖IT、能源、工业、交通、建筑等领域。在工业自动化方面，日立提供智能制造、工业物联网、自动化系统等解决方案。',
                'type': 'To B - 工业自动化',
                'industry': '工业自动化、智能制造、工业物联网',
                'founded': '1910年',
                'headquarters': '日本东京'
            },
            'hivemq': {
                'name': 'HiveMQ',
                'description': 'HiveMQ是一家德国MQTT消息代理软件公司，提供企业级MQTT平台，用于物联网（IoT）和工业物联网（IIoT）应用的实时数据通信。公司专注于为工业4.0和IoT场景提供可靠的消息传递解决方案。',
                'type': 'To B - IoT消息平台',
                'industry': 'IoT消息平台、MQTT、工业物联网',
                'founded': '2012年',
                'headquarters': '德国慕尼黑'
            },
            'honeywell': {
                'name': 'Honeywell',
                'description': '霍尼韦尔（Honeywell）是一家美国跨国工业公司，业务涵盖航空航天、建筑技术、性能材料、安全与生产力解决方案。在工业自动化领域，霍尼韦尔提供过程控制、自动化系统、工业软件等。',
                'type': 'To B - 工业自动化',
                'industry': '工业自动化、过程控制、工业软件',
                'founded': '1906年',
                'headquarters': '美国新泽西州夏洛特'
            },
            'ignition': {
                'name': 'Ignition',
                'description': 'Ignition是由Inductive Automation开发的工业自动化软件平台，提供SCADA、MES、IIoT等解决方案。Ignition以基于Web的架构和灵活的许可模式著称，广泛应用于制造业和工业自动化场景。',
                'type': 'To B - 工业自动化软件',
                'industry': 'SCADA、MES、IIoT、工业软件',
                'founded': '2003年（Inductive Automation）',
                'headquarters': '美国加州福尔松'
            },
            'rockwell-automation': {
                'name': 'Rockwell Automation',
                'description': '罗克韦尔自动化（Rockwell Automation）是一家美国工业自动化和数字化转型公司，提供自动化控制、信息解决方案和服务。公司专注于为制造业提供集成控制和信息解决方案。',
                'type': 'To B - 工业自动化',
                'industry': '工业自动化、控制系统、智能制造',
                'founded': '1903年',
                'headquarters': '美国威斯康星州密尔沃基'
            },
            'schneider-electric': {
                'name': 'Schneider Electric',
                'description': '施耐德电气（Schneider Electric）是一家法国跨国能源管理和自动化公司，提供电力管理、自动化解决方案、工业软件等。公司专注于为工业、建筑、数据中心等提供能效和自动化解决方案。',
                'type': 'To B - 能源管理和自动化',
                'industry': '能源管理、工业自动化、工业软件',
                'founded': '1836年',
                'headquarters': '法国吕埃-马迈松'
            },
            'siemens': {
                'name': 'Siemens',
                'description': '西门子（Siemens）是一家德国跨国工业公司，业务涵盖数字化工业、智能基础设施、移动出行、医疗技术等领域。在工业自动化方面，西门子提供自动化系统、工业软件、数字孪生等解决方案，是工业4.0的领导者之一。',
                'type': 'To B - 工业自动化和数字化',
                'industry': '工业自动化、工业软件、数字孪生、智能制造',
                'founded': '1847年',
                'headquarters': '德国慕尼黑'
            },
            'tulip': {
                'name': 'Tulip',
                'description': 'Tulip是一家美国制造执行系统（MES）软件公司，提供无代码平台，帮助制造商构建和部署车间应用。Tulip专注于为制造业提供数字化车间解决方案，连接人员、机器和系统。',
                'type': 'To B - 制造执行系统',
                'industry': 'MES、制造软件、无代码平台',
                'founded': '2014年',
                'headquarters': '美国马萨诸塞州萨默维尔'
            },
            'umh': {
                'name': 'UMH',
                'description': 'UMH是一家工业自动化解决方案提供商，专注于为制造业提供自动化系统和解决方案。',
                'type': 'To B - 工业自动化',
                'industry': '工业自动化',
                'founded': '未知',
                'headquarters': '未知'
            },
            'univers': {
                'name': 'Univers',
                'description': 'Univers是一家工业自动化或相关领域的公司。',
                'type': 'To B - 工业自动化',
                'industry': '工业自动化',
                'founded': '未知',
                'headquarters': '未知'
            },
            'yokogawa': {
                'name': 'Yokogawa',
                'description': '横河电机（Yokogawa）是一家日本工业自动化和测试测量公司，提供过程控制、测量仪器、工业自动化系统等。公司专注于为流程工业（如化工、石油天然气、电力等）提供自动化解决方案。',
                'type': 'To B - 工业自动化',
                'industry': '过程控制、测量仪器、工业自动化',
                'founded': '1915年',
                'headquarters': '日本东京'
            },
            # 参考公司
            'apple': {
                'name': 'Apple',
                'description': '苹果（Apple）是一家美国跨国科技公司，设计、开发和销售消费电子产品、计算机软件和在线服务。苹果以iPhone、iPad、Mac等硬件产品以及iOS、macOS等软件平台著称。',
                'type': 'To C - 消费电子产品',
                'industry': '消费电子、软件、服务',
                'founded': '1976年',
                'headquarters': '美国加州库比蒂诺'
            },
            'byd': {
                'name': 'BYD',
                'description': '比亚迪（BYD）是一家中国跨国技术公司，业务涵盖新能源汽车、电池、电子、轨道交通等领域。比亚迪是全球领先的电动汽车制造商之一，也生产电池、手机部件等。',
                'type': 'To C - 新能源汽车',
                'industry': '新能源汽车、电池、电子',
                'founded': '1995年',
                'headquarters': '中国深圳'
            },
            'palantir': {
                'name': 'Palantir',
                'description': 'Palantir是一家美国大数据分析公司，提供数据集成和分析平台，主要服务于政府、国防、金融等行业。Palantir的平台帮助组织整合和分析大规模数据，用于决策支持。',
                'type': 'To B - 大数据分析平台',
                'industry': '大数据分析、数据平台、企业软件',
                'founded': '2003年',
                'headquarters': '美国科罗拉多州丹佛'
            },
            'samsara': {
                'name': 'Samsara',
                'description': 'Samsara是一家美国物联网（IoT）公司，提供连接运营平台，包括车辆追踪、视频安全、设备监控等解决方案。Samsara专注于为车队管理、物流、制造业等提供IoT解决方案。',
                'type': 'To B - IoT平台',
                'industry': 'IoT、车队管理、视频安全',
                'founded': '2015年',
                'headquarters': '美国加州旧金山'
            },
            'stripe': {
                'name': 'Stripe',
                'description': 'Stripe是一家美国金融科技公司，提供在线支付处理平台和API。Stripe帮助企业和开发者接受在线支付，提供支付基础设施、订阅管理、发票等金融工具。',
                'type': 'To B - 金融科技',
                'industry': '支付处理、金融科技、API',
                'founded': '2010年',
                'headquarters': '美国加州旧金山'
            },
            'xiaomi': {
                'name': 'Xiaomi',
                'description': '小米（Xiaomi）是一家中国跨国科技公司，主要生产智能手机、智能家居设备、消费电子产品等。小米以高性价比产品和IoT生态链著称，是全球主要的智能手机制造商之一。',
                'type': 'To C - 消费电子产品',
                'industry': '智能手机、智能家居、消费电子',
                'founded': '2010年',
                'headquarters': '中国北京'
            }
        }
    
    def analyze_company_data(self, company_name: str, csv_file: Path) -> Dict:
        """分析公司数据"""
        if not csv_file.exists():
            return None
        
        df = pd.read_csv(csv_file)
        
        # 内容类型分布
        content_types = df['content_type'].value_counts().head(5).to_dict()
        content_types_pct = {k: v/len(df)*100 for k, v in content_types.items()}
        
        # 漏斗分析
        awareness_keywords = ['blog', 'article', 'news', 'press-release', 'whitepaper', 'ebook', 'report']
        consideration_keywords = ['webinar', 'demo', 'case-study', 'customer-story', 'success-story', 'video']
        conversion_keywords = ['datasheet', 'specification', 'pricing', 'trial', 'contact', 'request-demo']
        loyalty_keywords = ['documentation', 'guide', 'tutorial', 'support', 'community', 'training']
        
        awareness_count = 0
        consideration_count = 0
        conversion_count = 0
        loyalty_count = 0
        
        for _, row in df.iterrows():
            path = str(row.get('path', '')).lower()
            url = str(row.get('url', '')).lower()
            content_type = str(row.get('content_type', '')).lower()
            combined = path + ' ' + url + ' ' + content_type
            
            if any(kw in combined for kw in awareness_keywords):
                awareness_count += 1
            elif any(kw in combined for kw in consideration_keywords):
                consideration_count += 1
            elif any(kw in combined for kw in conversion_keywords):
                conversion_count += 1
            elif any(kw in combined for kw in loyalty_keywords):
                loyalty_count += 1
        
        total_funnel = awareness_count + consideration_count + conversion_count + loyalty_count
        funnel_pct = {
            'awareness': awareness_count/total_funnel*100 if total_funnel > 0 else 0,
            'consideration': consideration_count/total_funnel*100 if total_funnel > 0 else 0,
            'conversion': conversion_count/total_funnel*100 if total_funnel > 0 else 0,
            'loyalty': loyalty_count/total_funnel*100 if total_funnel > 0 else 0
        }
        
        # 判断漏斗类型
        if funnel_pct['awareness'] > 50:
            funnel_type = 'awareness-heavy'
        elif funnel_pct['consideration'] > 40:
            funnel_type = 'consideration-heavy'
        elif funnel_pct['conversion'] > 30:
            funnel_type = 'conversion-heavy'
        elif funnel_pct['loyalty'] > 30:
            funnel_type = 'loyalty-heavy'
        else:
            funnel_type = 'balanced'
        
        return {
            'total_urls': len(df),
            'avg_depth': float(df['depth'].mean()),
            'content_types': content_types_pct,
            'funnel_distribution': funnel_pct,
            'funnel_type': funnel_type,
            'blog_count': int(df['is_blog'].sum()),
            'webinar_count': int(df['is_webinar'].sum()),
            'resource_count': int(df['is_resource'].sum())
        }
    
    def generate_all_profiles(self):
        """生成所有公司档案"""
        print("=" * 80)
        print("生成公司档案：外部介绍 + 数据总结")
        print("=" * 80)
        print()
        
        profiles = []
        
        # 处理竞品公司
        competitor_files = sorted(self.output_data_dir.glob("*_analyzed.csv"))
        competitor_files = [f for f in competitor_files if 'reference' not in str(f)]
        
        for csv_file in competitor_files:
            company_key = csv_file.stem.replace('_analyzed', '')
            if company_key in self.company_profiles:
                print(f"处理 {company_key}...")
                profile = self.company_profiles[company_key].copy()
                data_analysis = self.analyze_company_data(company_key, csv_file)
                if data_analysis:
                    profile['data_analysis'] = data_analysis
                    profile['category'] = 'To B工业自动化'
                    profiles.append(profile)
        
        # 处理参考公司
        if self.reference_dir.exists():
            reference_files = sorted(self.reference_dir.glob("*_analyzed.csv"))
            for csv_file in reference_files:
                company_key = csv_file.stem.replace('_analyzed', '')
                if company_key in self.company_profiles:
                    print(f"处理 {company_key}...")
                    profile = self.company_profiles[company_key].copy()
                    data_analysis = self.analyze_company_data(company_key, csv_file)
                    if data_analysis:
                        profile['data_analysis'] = data_analysis
                        if company_key in ['apple', 'xiaomi', 'byd']:
                            profile['category'] = 'To C消费品'
                        else:
                            profile['category'] = 'To B科技/软件'
                        profiles.append(profile)
        
        # 生成报告
        report_file = self.insight_reports_dir / "公司档案_外部介绍与数据总结.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 公司档案：外部介绍与数据总结\n\n")
            f.write("=" * 80 + "\n\n")
            f.write("**说明**: 本报告包含各公司的外部介绍（基于公开信息）和数据驱动的分析总结\n\n")
            f.write("=" * 80 + "\n\n")
            
            # 按类别分组
            categories = {}
            for profile in profiles:
                cat = profile['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(profile)
            
            for category, companies in categories.items():
                f.write(f"## {category}\n\n")
                
                for profile in companies:
                    f.write(f"### {profile['name']}\n\n")
                    
                    # 外部介绍
                    f.write("#### 公司介绍\n\n")
                    f.write(f"**公司类型**: {profile['type']}\n\n")
                    f.write(f"**行业**: {profile['industry']}\n\n")
                    f.write(f"**成立时间**: {profile['founded']}\n\n")
                    f.write(f"**总部**: {profile['headquarters']}\n\n")
                    f.write(f"**简介**: {profile['description']}\n\n")
                    
                    # 数据总结
                    if 'data_analysis' in profile:
                        data = profile['data_analysis']
                        f.write("#### 数据驱动的策略总结\n\n")
                        
                        f.write(f"- **总URL数**: {data['total_urls']:,}\n")
                        f.write(f"- **平均URL深度**: {data['avg_depth']:.1f}\n")
                        f.write(f"- **内容营销漏斗类型**: {data['funnel_type']}\n")
                        f.write(f"  - Awareness (认知): {data['funnel_distribution']['awareness']:.1f}%\n")
                        f.write(f"  - Consideration (考虑): {data['funnel_distribution']['consideration']:.1f}%\n")
                        f.write(f"  - Conversion (转化): {data['funnel_distribution']['conversion']:.1f}%\n")
                        f.write(f"  - Loyalty (忠诚): {data['funnel_distribution']['loyalty']:.1f}%\n\n")
                        
                        f.write("**主要内容类型分布（Top 5）**:\n")
                        for ct, pct in sorted(data['content_types'].items(), 
                                             key=lambda x: x[1], reverse=True)[:5]:
                            f.write(f"- {ct}: {pct:.1f}%\n")
                        f.write("\n")
                        
                        f.write("**关键内容资产**:\n")
                        f.write(f"- Blog文章: {data['blog_count']:,}篇\n")
                        f.write(f"- Webinar: {data['webinar_count']:,}个\n")
                        f.write(f"- 资源页面: {data['resource_count']:,}个\n\n")
                        
                        # 策略洞察
                        f.write("**策略洞察**:\n")
                        insights = []
                        
                        if data['funnel_type'] == 'awareness-heavy':
                            insights.append(f"采用**获客导向**的内容策略，注重通过博客、白皮书等内容吸引潜在客户，建立品牌认知")
                        elif data['funnel_type'] == 'consideration-heavy':
                            insights.append(f"采用**考虑阶段导向**的内容策略，注重通过webinar、案例研究等内容帮助客户评估解决方案")
                        elif data['funnel_type'] == 'conversion-heavy':
                            insights.append(f"采用**转化导向**的内容策略，注重通过产品规格、试用等内容促进购买决策")
                        
                        if data['avg_depth'] < 2:
                            insights.append(f"网站组织**扁平化**（平均深度{data['avg_depth']:.1f}），内容易于访问")
                        elif data['avg_depth'] > 4:
                            insights.append(f"网站组织**层级化**（平均深度{data['avg_depth']:.1f}），内容分类细致")
                        
                        if data['blog_count'] > 100:
                            insights.append(f"拥有大量博客内容（{data['blog_count']:,}篇），注重内容营销和SEO")
                        
                        if data['webinar_count'] > 50:
                            insights.append(f"拥有丰富的webinar资源（{data['webinar_count']:,}个），注重教育型内容")
                        
                        for insight in insights:
                            f.write(f"- {insight}\n")
                        f.write("\n")
                    
                    f.write("---\n\n")
        
        print(f"\n✅ 报告已保存: {report_file}")
        print(f"   共生成 {len(profiles)} 个公司档案")


if __name__ == "__main__":
    generator = CompanyProfileGenerator()
    generator.generate_all_profiles()

