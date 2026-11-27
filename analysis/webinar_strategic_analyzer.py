#!/usr/bin/env python3
"""
Webinar 双维解剖分析器
- 执行层解剖：SOP分析（基于现有数据）
- 战略层解剖：战略解码（话题、漏斗、生态）
"""

import pandas as pd
import re
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
import json


class WebinarStrategicAnalyzer:
    """Webinar战略分析器"""
    
    def __init__(self):
        """初始化分析器"""
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        
        self.output_data_dir = project_root / "output_data"
        self.information_dir = project_root / "Information"
        self.knowledge_dir = project_root / "Knowledge"
        self.insight_dir = project_root / "insight"
        
        # 创建输出目录
        self.webinar_analysis_dir = self.knowledge_dir / "Webinar专项分析"
        self.webinar_analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # 话题关键词库
        self.topic_keywords = {
            'ai_genai': ['ai', 'artificial intelligence', 'generative ai', 'genai', 'machine learning', 'ml', 'llm'],
            'data_ops': ['dataops', 'data ops', 'data operations', 'data platform', 'data fusion'],
            'digital_twin': ['digital twin', 'digital twins', 'digitalization'],
            'iot_iiot': ['iot', 'iiot', 'industrial iot', 'edge computing'],
            'cloud': ['cloud', 'azure', 'aws', 'gcp', 'cloud migration', 'saas'],
            'cybersecurity': ['cybersecurity', 'security', 'cyber', 'zero trust'],
            'sustainability': ['sustainability', 'sustainable', 'esg', 'carbon', 'emissions'],
            'automation': ['automation', 'robotic', 'rpa', 'workflow automation'],
            'analytics': ['analytics', 'business intelligence', 'bi', 'insights', 'dashboard']
        }
        
        # 漏斗阶段关键词
        self.funnel_keywords = {
            'tofu': ['trend', 'future', 'industry', 'market', 'gartner', 'forrester', 'analyst', 'outlook', 'vision'],
            'mofu': ['case study', 'customer story', 'solution', 'comparison', 'vs', 'roi', 'benefits', 'use case'],
            'bofu': ['demo', 'tutorial', 'training', 'how to', 'getting started', 'implementation', 'setup', 'guide']
        }
        
        # 合作伙伴关键词
        self.partner_keywords = [
            'microsoft', 'aws', 'google', 'azure', 'gcp', 'nvidia', 'intel', 'dell', 'hp',
            'pwc', 'deloitte', 'accenture', 'kpmg', 'ey', 'ernst', 'mckinsey',
            'gartner', 'forrester', 'idc', 'gartner'
        ]
    
    def extract_webinar_titles(self, company: str) -> List[Dict]:
        """从complete_tree中提取Webinar标题"""
        tree_file = self.information_dir / f"{company}_analyzed_complete_tree.txt"
        
        if not tree_file.exists():
            return []
        
        webinars = []
        
        try:
            with open(tree_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                if 'webinar' in line.lower():
                    # 清理标题
                    title = re.sub(r'[│├─└📄📂\s]+', ' ', line).strip()
                    title = re.sub(r'\.html?$', '', title, flags=re.IGNORECASE)
                    
                    if title and len(title) > 5:
                        webinars.append({
                            'title': title,
                            'raw_line': line.strip()
                        })
        
        except Exception as e:
            print(f"❌ 读取{company}的tree文件时出错: {e}")
        
        return webinars
    
    def analyze_topic_trends(self, webinars: List[Dict], company: str) -> Dict:
        """分析话题风向标"""
        if not webinars:
            return {}
        
        # 提取所有标题文本
        all_titles = ' '.join([w['title'].lower() for w in webinars])
        
        # 统计话题关键词出现频率
        topic_counts = {}
        for topic, keywords in self.topic_keywords.items():
            count = sum(1 for keyword in keywords if keyword in all_titles)
            if count > 0:
                topic_counts[topic] = count
        
        # 提取标题中的高频词
        stop_words = {
            'webinar', 'webinars', 'on', 'demand', 'register', 'watch', 'series',
            'the', 'and', 'for', 'with', 'from', 'to', 'your', 'you', 'are', 'this', 'that',
            'these', 'those', 'what', 'which', 'when', 'where', 'how', 'why', 'who', 'whom',
            'their', 'them', 'they', 'have', 'has', 'had', 'been', 'being', 'was', 'were',
            'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can', 'about',
            'into', 'over', 'after', 'under', 'above', 'below', 'between', 'among', 'through',
            'during', 'before', 'after', 'since', 'until', 'while', 'because', 'although',
            'improve', 'improving', 'better', 'best', 'good', 'great', 'new', 'latest',
            'like', 'design', 'make', 'makes', 'made', 'take', 'takes', 'taking', 'get', 'gets',
            'getting', 'got', 'give', 'gives', 'giving', 'gave', 'know', 'knows', 'knowing',
            'knew', 'see', 'sees', 'seeing', 'saw', 'come', 'comes', 'coming', 'came', 'go',
            'goes', 'going', 'went', 'think', 'thinks', 'thinking', 'thought', 'say', 'says',
            'saying', 'said', 'tell', 'tells', 'telling', 'told', 'use', 'uses', 'using', 'used'
        }
        
        # 提取有意义的词
        words = []
        for title in [w['title'] for w in webinars]:
            title_clean = re.sub(r'[^\w\s]', ' ', title.lower())
            title_words = [w for w in title_clean.split() 
                          if len(w) > 3 and w not in stop_words]
            words.extend(title_words)
        
        word_counts = Counter(words)
        
        return {
            'topic_distribution': topic_counts,
            'top_keywords': dict(word_counts.most_common(20)),
            'total_webinars': len(webinars)
        }
    
    def analyze_funnel_stage(self, webinars: List[Dict]) -> Dict:
        """分析漏斗阶段定位"""
        funnel_distribution = {'tofu': 0, 'mofu': 0, 'bofu': 0, 'unknown': 0}
        funnel_examples = {'tofu': [], 'mofu': [], 'bofu': [], 'unknown': []}
        
        for webinar in webinars:
            title_lower = webinar['title'].lower()
            
            # 检查每个漏斗阶段的关键词
            matched_stage = None
            max_matches = 0
            
            for stage, keywords in self.funnel_keywords.items():
                matches = sum(1 for keyword in keywords if keyword in title_lower)
                if matches > max_matches:
                    max_matches = matches
                    matched_stage = stage
            
            if matched_stage and max_matches > 0:
                funnel_distribution[matched_stage] += 1
                if len(funnel_examples[matched_stage]) < 5:
                    funnel_examples[matched_stage].append(webinar['title'])
            else:
                funnel_distribution['unknown'] += 1
                if len(funnel_examples['unknown']) < 5:
                    funnel_examples['unknown'].append(webinar['title'])
        
        return {
            'distribution': funnel_distribution,
            'examples': funnel_examples
        }
    
    def analyze_ecosystem(self, webinars: List[Dict]) -> Dict:
        """分析生态朋友圈"""
        partners_found = Counter()
        co_hosted_webinars = []
        
        for webinar in webinars:
            title_lower = webinar['title'].lower()
            
            # 查找合作伙伴
            found_partners = []
            for partner in self.partner_keywords:
                if partner in title_lower:
                    partners_found[partner] += 1
                    found_partners.append(partner)
            
            if found_partners:
                co_hosted_webinars.append({
                    'title': webinar['title'],
                    'partners': found_partners
                })
        
        return {
            'partners': dict(partners_found.most_common(10)),
            'co_hosted_count': len(co_hosted_webinars),
            'co_hosted_examples': co_hosted_webinars[:10]
        }
    
    def analyze_webinar_structure(self, company: str) -> Dict:
        """分析Webinar在网站结构中的位置"""
        csv_file = self.output_data_dir / f"{company}_analyzed.csv"
        
        if not csv_file.exists():
            return {}
        
        df = pd.read_csv(csv_file)
        
        # 筛选webinar
        webinar_mask = (
            (df['content_type'] == 'webinar') |
            (df['url'].str.contains('webinar', case=False, na=False)) |
            (df['path'].str.contains('webinar', case=False, na=False))
        )
        
        webinar_df = df[webinar_mask]
        
        if len(webinar_df) == 0:
            return {}
        
        # 分析URL路径结构
        path_patterns = Counter()
        sections = Counter()
        
        for _, row in webinar_df.iterrows():
            path = str(row.get('path', ''))
            section = str(row.get('section', ''))
            
            if section and section != 'nan':
                sections[section] += 1
            
            # 提取路径模式
            if path:
                # 检查是否有系列标识
                if 'series' in path.lower():
                    path_patterns['has_series'] += 1
                if 'on-demand' in path.lower() or 'ondemand' in path.lower():
                    path_patterns['on_demand'] += 1
                if 'live' in path.lower():
                    path_patterns['live'] += 1
        
        return {
            'total_webinars': len(webinar_df),
            'path_patterns': dict(path_patterns),
            'sections': dict(sections.most_common(10))
        }
    
    def analyze_company_webinar(self, company: str) -> Dict:
        """分析单个公司的Webinar"""
        print(f"分析: {company}")
        
        # 提取Webinar标题
        webinars = self.extract_webinar_titles(company)
        
        if not webinars:
            print(f"  ⚠️ 未找到Webinar数据")
            return None
        
        # 话题分析
        topic_analysis = self.analyze_topic_trends(webinars, company)
        
        # 漏斗分析
        funnel_analysis = self.analyze_funnel_stage(webinars)
        
        # 生态分析
        ecosystem_analysis = self.analyze_ecosystem(webinars)
        
        # 结构分析
        structure_analysis = self.analyze_webinar_structure(company)
        
        return {
            'company': company,
            'webinar_count': len(webinars),
            'webinar_titles': [w['title'] for w in webinars[:20]],  # 前20个标题
            'topic_analysis': topic_analysis,
            'funnel_analysis': funnel_analysis,
            'ecosystem_analysis': ecosystem_analysis,
            'structure_analysis': structure_analysis
        }
    
    def analyze_all_companies(self) -> pd.DataFrame:
        """分析所有公司"""
        print("=" * 80)
        print("Webinar双维解剖分析")
        print("=" * 80)
        print()
        
        # 获取所有公司
        csv_files = sorted(self.output_data_dir.glob("*_analyzed.csv"))
        companies = [f.stem.replace('_analyzed', '') for f in csv_files]
        
        results = []
        
        for company in companies:
            result = self.analyze_company_webinar(company)
            if result:
                results.append(result)
            print()
        
        return results
    
    def generate_strategic_report(self, results: List[Dict]) -> str:
        """生成战略分析报告"""
        report_file = self.webinar_analysis_dir / "Webinar战略解剖报告.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Webinar 双维解剖分析报告\n\n")
            f.write("=" * 80 + "\n\n")
            f.write("**分析日期**: " + pd.Timestamp.now().strftime('%Y-%m-%d') + "\n")
            f.write(f"**分析公司数**: {len(results)}\n\n")
            f.write("=" * 80 + "\n\n")
            
            # 执行摘要
            f.write("## 执行摘要\n\n")
            total_webinars = sum(r['webinar_count'] for r in results)
            f.write(f"- **总Webinar数**: {total_webinars:,}\n")
            f.write(f"- **有Webinar的公司**: {len(results)} 个\n")
            f.write("\n")
            
            # 第一维度：执行层解剖
            f.write("## 第一维度：执行层解剖 (The \"How-To\" Audit)\n\n")
            f.write("### 基于现有数据的发现\n\n")
            
            for result in results:
                company = result['company']
                f.write(f"#### {company}\n\n")
                f.write(f"- **Webinar数量**: {result['webinar_count']}\n")
                
                structure = result.get('structure_analysis', {})
                if structure:
                    f.write(f"- **网站位置**: {', '.join(list(structure.get('sections', {}).keys())[:3])}\n")
                    path_patterns = structure.get('path_patterns', {})
                    if path_patterns:
                        patterns = []
                        if path_patterns.get('has_series'):
                            patterns.append('系列化')
                        if path_patterns.get('on_demand'):
                            patterns.append('点播')
                        if path_patterns.get('live'):
                            patterns.append('直播')
                        if patterns:
                            f.write(f"- **格式特征**: {', '.join(patterns)}\n")
                f.write("\n")
            
            f.write("### 需要人工补充的数据\n\n")
            f.write("以下信息需要访问实际网页或视频平台获取：\n\n")
            f.write("1. **着陆页设计**: 表单问题数量、Lead Scoring信号、倒计时设计\n")
            f.write("2. **推广渠道**: LinkedIn预热时间、Speaker短视频预热\n")
            f.write("3. **内容呈现**: 格式（PPT/对话/Demo）、互动设计（Polls、Q&A）\n")
            f.write("4. **会后运营**: 回放上线时间、内容切片情况、播放量数据\n\n")
            
            # 第二维度：战略层解剖
            f.write("## 第二维度：战略层解剖 (The Strategic Decoding)\n\n")
            
            # 话题风向标
            f.write("### 1. 话题风向标 (Topic Trends)\n\n")
            
            for result in results:
                company = result['company']
                topic_analysis = result.get('topic_analysis', {})
                
                if topic_analysis and topic_analysis.get('topic_distribution'):
                    f.write(f"#### {company}\n\n")
                    f.write("**核心话题分布**:\n")
                    for topic, count in sorted(topic_analysis['topic_distribution'].items(), 
                                             key=lambda x: x[1], reverse=True):
                        topic_name = topic.replace('_', ' ').title()
                        f.write(f"- **{topic_name}**: {count} 次提及\n")
                    
                    if topic_analysis.get('top_keywords'):
                        f.write("\n**标题高频词**:\n")
                        for keyword, count in list(topic_analysis['top_keywords'].items())[:10]:
                            f.write(f"- {keyword}: {count} 次\n")
                    f.write("\n")
            
            # 漏斗阶段定位
            f.write("### 2. 漏斗阶段定位 (Funnel Mapping)\n\n")
            
            for result in results:
                company = result['company']
                funnel_analysis = result.get('funnel_analysis', {})
                
                if funnel_analysis:
                    f.write(f"#### {company}\n\n")
                    distribution = funnel_analysis.get('distribution', {})
                    total = sum(distribution.values())
                    
                    if total > 0:
                        f.write("**漏斗分布**:\n")
                        f.write(f"- **TOFU (漏斗上层)**: {distribution.get('tofu', 0)} ({distribution.get('tofu', 0)/total*100:.1f}%)\n")
                        f.write(f"- **MOFU (漏斗中层)**: {distribution.get('mofu', 0)} ({distribution.get('mofu', 0)/total*100:.1f}%)\n")
                        f.write(f"- **BOFU (漏斗下层)**: {distribution.get('bofu', 0)} ({distribution.get('bofu', 0)/total*100:.1f}%)\n")
                        f.write(f"- **未知**: {distribution.get('unknown', 0)} ({distribution.get('unknown', 0)/total*100:.1f}%)\n")
                        
                        examples = funnel_analysis.get('examples', {})
                        if examples.get('tofu'):
                            f.write("\n**TOFU示例**:\n")
                            for ex in examples['tofu'][:3]:
                                f.write(f"- {ex}\n")
                        if examples.get('mofu'):
                            f.write("\n**MOFU示例**:\n")
                            for ex in examples['mofu'][:3]:
                                f.write(f"- {ex}\n")
                        if examples.get('bofu'):
                            f.write("\n**BOFU示例**:\n")
                            for ex in examples['bofu'][:3]:
                                f.write(f"- {ex}\n")
                    f.write("\n")
            
            # 生态朋友圈
            f.write("### 3. 生态朋友圈 (Ecosystem Strategy)\n\n")
            
            for result in results:
                company = result['company']
                ecosystem_analysis = result.get('ecosystem_analysis', {})
                
                if ecosystem_analysis:
                    partners = ecosystem_analysis.get('partners', {})
                    co_hosted_count = ecosystem_analysis.get('co_hosted_count', 0)
                    
                    if partners or co_hosted_count > 0:
                        f.write(f"#### {company}\n\n")
                        f.write(f"- **联合举办Webinar数**: {co_hosted_count}\n")
                        
                        if partners:
                            f.write("\n**合作伙伴**:\n")
                            for partner, count in sorted(partners.items(), key=lambda x: x[1], reverse=True):
                                f.write(f"- **{partner.title()}**: {count} 次\n")
                        
                        co_hosted_examples = ecosystem_analysis.get('co_hosted_examples', [])
                        if co_hosted_examples:
                            f.write("\n**联合举办示例**:\n")
                            for ex in co_hosted_examples[:5]:
                                f.write(f"- {ex['title']}\n")
                                f.write(f"  合作伙伴: {', '.join(ex['partners'])}\n")
                        f.write("\n")
            
            # 战略洞察
            f.write("## 战略洞察\n\n")
            f.write("### 话题趋势洞察\n\n")
            f.write("基于Webinar标题分析，识别各公司的核心战略话题：\n\n")
            
            # 汇总所有公司的话题
            all_topics = defaultdict(list)
            for result in results:
                company = result['company']
                topic_analysis = result.get('topic_analysis', {})
                topics = topic_analysis.get('topic_distribution', {})
                for topic, count in topics.items():
                    all_topics[topic].append((company, count))
            
            for topic, companies in sorted(all_topics.items(), key=lambda x: len(x[1]), reverse=True):
                topic_name = topic.replace('_', ' ').title()
                company_list = ', '.join([f"{c[0]} ({c[1]}次)" for c in companies[:5]])
                f.write(f"- **{topic_name}**: {company_list}\n")
            
            f.write("\n")
            f.write("### 漏斗策略洞察\n\n")
            f.write("分析各公司的Webinar策略定位：\n\n")
            
            for result in results:
                company = result['company']
                funnel_analysis = result.get('funnel_analysis', {})
                distribution = funnel_analysis.get('distribution', {})
                total = sum(distribution.values())
                
                if total > 0:
                    tofu_ratio = distribution.get('tofu', 0) / total
                    bofu_ratio = distribution.get('bofu', 0) / total
                    
                    strategy = "未知"
                    if tofu_ratio > 0.5:
                        strategy = "**拉新为主** - 大量TOFU内容，疯狂扩张品牌声量"
                    elif bofu_ratio > 0.5:
                        strategy = "**存量为主** - 大量BOFU内容，服务现有客户"
                    else:
                        strategy = "**平衡策略** - TOFU/MOFU/BOFU分布相对均衡"
                    
                    f.write(f"- **{company}**: {strategy}\n")
            
            f.write("\n")
            f.write("=" * 80 + "\n")
        
        print(f"✅ 战略分析报告已保存: {report_file}")
        return str(report_file)
    
    def generate_sop_scorecard(self, results: List[Dict]) -> str:
        """生成SOP记分卡（Excel格式的CSV）"""
        scorecard_file = self.webinar_analysis_dir / "Webinar_SOP记分卡.csv"
        
        rows = []
        for result in results:
            company = result['company']
            structure = result.get('structure_analysis', {})
            funnel = result.get('funnel_analysis', {})
            ecosystem = result.get('ecosystem_analysis', {})
            
            # 提取信息
            webinar_count = result.get('webinar_count', 0)
            path_patterns = structure.get('path_patterns', {})
            has_series = '是' if path_patterns.get('has_series', 0) > 0 else '否'
            has_ondemand = '是' if path_patterns.get('on_demand', 0) > 0 else '否'
            
            funnel_dist = funnel.get('distribution', {})
            total_funnel = sum(funnel_dist.values())
            tofu_ratio = funnel_dist.get('tofu', 0) / total_funnel * 100 if total_funnel > 0 else 0
            mofu_ratio = funnel_dist.get('mofu', 0) / total_funnel * 100 if total_funnel > 0 else 0
            bofu_ratio = funnel_dist.get('bofu', 0) / total_funnel * 100 if total_funnel > 0 else 0
            
            partners = ecosystem.get('partners', {})
            top_partner = list(partners.keys())[0].title() if partners else '-'
            
            rows.append({
                '公司': company,
                'Webinar数量': webinar_count,
                '是否有系列': has_series,
                '是否有点播': has_ondemand,
                'TOFU占比(%)': f"{tofu_ratio:.1f}",
                'MOFU占比(%)': f"{mofu_ratio:.1f}",
                'BOFU占比(%)': f"{bofu_ratio:.1f}",
                '主要合作伙伴': top_partner,
                '联合举办数': ecosystem.get('co_hosted_count', 0)
            })
        
        df = pd.DataFrame(rows)
        df.to_csv(scorecard_file, index=False, encoding='utf-8-sig')
        
        print(f"✅ SOP记分卡已保存: {scorecard_file}")
        return str(scorecard_file)


def main():
    """主函数"""
    analyzer = WebinarStrategicAnalyzer()
    
    # 分析所有公司
    results = analyzer.analyze_all_companies()
    
    if results:
        # 生成报告
        analyzer.generate_strategic_report(results)
        analyzer.generate_sop_scorecard(results)
        
        # 保存JSON数据
        json_file = analyzer.webinar_analysis_dir / "webinar_strategic_analysis.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        print(f"✅ 分析数据已保存: {json_file}")
    
    print("\n" + "=" * 80)
    print("✅ Webinar双维解剖分析完成！")
    print("=" * 80)
    print()
    print("📁 生成的文件:")
    print(f"  - {analyzer.webinar_analysis_dir / 'Webinar战略解剖报告.md'}")
    print(f"  - {analyzer.webinar_analysis_dir / 'Webinar_SOP记分卡.csv'}")
    print(f"  - {analyzer.webinar_analysis_dir / 'webinar_strategic_analysis.json'}")


if __name__ == "__main__":
    main()

