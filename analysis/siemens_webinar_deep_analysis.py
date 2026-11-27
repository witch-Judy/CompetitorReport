#!/usr/bin/env python3
"""
Siemens Webinar深度分析
分析Webinar标题，判断倾向（科普 vs 产品），检查主题重复等
"""

import pandas as pd
import re
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
import json


class SiemensWebinarDeepAnalyzer:
    """Siemens Webinar深度分析器"""
    
    def __init__(self):
        """初始化分析器"""
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        
        self.information_dir = project_root / "Information"
        self.output_data_dir = project_root / "output_data"
        self.insight_dir = project_root / "insight"
        
        # 创建输出目录
        self.insight_dir.mkdir(parents=True, exist_ok=True)
        
        # 关键词库（扩展版）
        self.education_keywords = [
            'introduction', 'overview', 'fundamentals', 'basics', 'guide', 'tutorial',
            'how to', 'getting started', 'learn', 'understanding', 'explained',
            'what is', 'why', 'trends', 'future', 'industry', 'market',
            'best practices', 'strategies', 'insights', 'expert', 'panel',
            'innovation', 'transformation', 'digitalization', 'green deal',
            'sustainability', 'expert talk', 'shaping the future',
            'food beverage', 'reducing', 'non revenue', 'water', 'pharmaceutical',
            'automotive', 'chemical', 'energy', 'manufacturing'
        ]
        
        self.product_keywords = [
            'demo', 'demonstration', 'features', 'capabilities', 'functionality',
            'product', 'solution', 'platform', 'system', 'software', 'tool',
            'setup', 'configuration', 'implementation', 'deployment', 'installation',
            'training', 'workshop', 'hands-on', 'practical', 'use case',
            'simatic', 'wincc', 'tia', 'et200', 'scada', 'plc', 'cnc',
            'programming', 'operation', 'usage', 'how to use', 'getting started with',
            'copilot', 'simotics', 'sinema', 'connect', 'modules', 'motor',
            'remote', 'g220', 's200', 's210', 'coriolis', 'asd', 'sistar',
            'empro', 'inspekto', 'desigo', 'sentron', 'logo', 's7', 'portal',
            'sinamics', 'sitrain', 'services', 'digital services', 'analytics services'
        ]
        
        self.technical_keywords = [
            'api', 'integration', 'architecture', 'development', 'programming',
            'code', 'technical', 'deep dive', 'advanced', 'expert', 'masterclass',
            'g code', 'parametrizace', 'configuration', 'setup', 'installation',
            'segmentation', 'modeling', 'engineering', 'design',
            'simulation', 'data analytics', 'anomaly detection', 'digital twin',
            'digital twins', 'bioprocess', 'end to end'
        ]
        
        # 目录/导航页关键词（应该排除或单独标记）
        self.directory_keywords = [
            'webinars', 'webinar series', 'upcoming webinars', 'on demand webinars',
            'anmeldung', 'register', 'recordings', 'industria', 'webinare',
            'webinari', 'webinarreihe'
        ]
    
    def extract_webinar_titles(self) -> List[Dict]:
        """提取所有Webinar标题"""
        tree_file = self.information_dir / "siemens_analyzed_complete_tree.txt"
        
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
                            'title_lower': title.lower(),
                            'raw_line': line.strip()
                        })
        
        except Exception as e:
            print(f"❌ 读取文件时出错: {e}")
        
        return webinars
    
    def classify_webinar_type(self, title_lower: str) -> Dict:
        """分类Webinar类型"""
        classification = {
            'type': 'unknown',  # education, product, technical, mixed
            'tendency': 'unknown',  # 科普/教育, 产品用法, 技术深度, 混合
            'education_score': 0,
            'product_score': 0,
            'technical_score': 0
        }
        
        # 计算各类型得分
        for keyword in self.education_keywords:
            if keyword in title_lower:
                classification['education_score'] += 1
        
        for keyword in self.product_keywords:
            if keyword in title_lower:
                classification['product_score'] += 1
        
        for keyword in self.technical_keywords:
            if keyword in title_lower:
                classification['technical_score'] += 1
        
        # 特殊规则：如果标题包含产品名称，更可能是产品类
        product_names = ['simatic', 'wincc', 'tia', 'et200', 'scada', 'plc', 'cnc', 
                        'sinamics', 'sitrain', 'desigo', 'sentron', 'logo', 's7',
                        'copilot', 'simotics', 'sinema', 'connect', 'g220', 's200', 
                        's210', 'coriolis', 'asd', 'sistar', 'empro', 'inspekto',
                        'portal', 'modules', 'motor', 'remote']
        if any(name in title_lower for name in product_names):
            classification['product_score'] += 2
        
        # 保存product_names供后续使用
        self._product_names = product_names
        
        # 特殊规则：如果标题包含行业、趋势词，更可能是教育类
        industry_trend_words = ['industry', 'innovation', 'future', 'trends', 'market',
                               'green deal', 'sustainability', 'transformation',
                               'food beverage', 'pharmaceutical', 'automotive', 
                               'chemical', 'energy', 'manufacturing', 'reducing',
                               'non revenue', 'water']
        if any(word in title_lower for word in industry_trend_words):
            classification['education_score'] += 1
        
        # 特殊规则：如果标题包含编程、代码相关词，更可能是技术类
        code_words = ['programming', 'code', 'g code', 'parametrizace', 'configuration',
                     'simulation', 'data analytics', 'analytics', 'anomaly detection',
                     'digital twin', 'digital twins', 'bioprocess', 'end to end']
        if any(word in title_lower for word in code_words):
            classification['technical_score'] += 2
        
        # 判断主要类型
        scores = {
            'education': classification['education_score'],
            'product': classification['product_score'],
            'technical': classification['technical_score']
        }
        
        # 检查是否是目录/导航页（但要排除包含产品名的标题）
        is_directory = any(dk in title_lower for dk in self.directory_keywords)
        has_product_name = any(name in title_lower for name in product_names)
        
        # 如果包含产品名，即使有目录关键词，也不应该是目录页
        if is_directory and len(title_lower.split()) <= 5 and not has_product_name:
            # 如果标题很短且包含目录关键词，且没有产品名，标记为目录页
            classification['type'] = 'directory'
            classification['tendency'] = '目录/导航页'
            return classification
        
        # 特殊规则：如果标题包含"series"和"upcoming"，很可能是目录页
        if 'series' in title_lower and 'upcoming' in title_lower:
            classification['type'] = 'directory'
            classification['tendency'] = '目录/导航页'
            return classification
        
        max_score = max(scores.values())
        if max_score == 0:
            # 如果完全没有匹配，尝试通过标题结构判断
            # 规则1: 如果包含产品名，很可能是产品类
            expanded_product_names = self._product_names  # 使用已定义的产品名列表
            if any(name in title_lower for name in expanded_product_names):
                classification['type'] = 'product'
                classification['tendency'] = '产品用法'
            # 规则2: 如果包含行业词，可能是教育类
            elif any(word in title_lower for word in ['industry', 'automotive', 'pharmaceutical', 
                                      'chemical', 'energy', 'manufacturing', 'innovation',
                                      'food beverage', 'reducing', 'non revenue', 'water']):
                classification['type'] = 'education'
                classification['tendency'] = '科普/教育'
            # 规则3: 如果包含技术词，可能是技术类
            elif any(word in title_lower for word in ['simulation', 'data analytics', 
                                                     'analytics', 'anomaly detection',
                                                     'digital twin', 'bioprocess']):
                classification['type'] = 'technical'
                classification['tendency'] = '技术深度'
            # 规则4: 如果标题很短（≤4词），且包含产品名，是产品类
            elif len(title_lower.split()) <= 4:
                if any(name in title_lower for name in expanded_product_names):
                    classification['type'] = 'product'
                    classification['tendency'] = '产品用法'
                else:
                    classification['type'] = 'unknown'
                    classification['tendency'] = '未知'
            else:
                classification['type'] = 'unknown'
                classification['tendency'] = '未知'
        else:
            max_type = max(scores, key=scores.get)
            classification['type'] = max_type
            
            if max_type == 'education':
                classification['tendency'] = '科普/教育'
            elif max_type == 'product':
                classification['tendency'] = '产品用法'
            elif max_type == 'technical':
                classification['tendency'] = '技术深度'
            
            # 如果有多个类型得分相近，标记为混合
            if len([s for s in scores.values() if s > 0]) > 1:
                sorted_scores = sorted(scores.values(), reverse=True)
                if sorted_scores[0] - sorted_scores[1] <= 1:
                    classification['type'] = 'mixed'
                    classification['tendency'] = '混合型'
        
        return classification
    
    def detect_duplicate_themes(self, webinars: List[Dict]) -> Dict:
        """检测主题重复"""
        # 提取标题核心词
        theme_patterns = defaultdict(list)
        
        for webinar in webinars:
            title = webinar['title_lower']
            
            # 移除常见词
            stop_words = {
                'webinar', 'webinars', 'siemens', 'the', 'and', 'for', 'with', 'from', 'to',
                'on', 'in', 'at', 'by', 'of', 'a', 'an', 'is', 'are', 'was', 'were',
                'how', 'what', 'when', 'where', 'why', 'which', 'who'
            }
            
            # 提取关键词（长度>3的词）
            words = [w for w in re.findall(r'\b\w{4,}\b', title) 
                    if w not in stop_words]
            
            # 生成主题关键词组合（取前3个关键词）
            if len(words) >= 2:
                theme_key = ' '.join(sorted(words[:3]))
                theme_patterns[theme_key].append(webinar['title'])
        
        # 找出重复的主题
        duplicates = {k: v for k, v in theme_patterns.items() if len(v) > 1}
        
        return {
            'total_unique_themes': len(theme_patterns),
            'duplicate_themes': len(duplicates),
            'duplicate_examples': dict(sorted(duplicates.items(), 
                                             key=lambda x: len(x[1]), 
                                             reverse=True)[:20])
        }
    
    def analyze_topic_distribution(self, webinars: List[Dict]) -> Dict:
        """分析话题分布"""
        # 提取所有标题中的关键词
        all_keywords = []
        
        for webinar in webinars:
            title = webinar['title_lower']
            # 移除常见词和webinar相关词
            title_clean = re.sub(r'\bwebinar[s]?\b', '', title)
            words = re.findall(r'\b\w{4,}\b', title_clean)
            all_keywords.extend(words)
        
        # 过滤停用词
        stop_words = {
            'siemens', 'webinar', 'webinars', 'register', 'watch', 'replay',
            'the', 'and', 'for', 'with', 'from', 'to', 'on', 'in', 'at', 'by', 'of',
            'a', 'an', 'is', 'are', 'was', 'were', 'have', 'has', 'had', 'been',
            'this', 'that', 'these', 'those', 'what', 'which', 'when', 'where',
            'how', 'why', 'who', 'your', 'you', 'their', 'them', 'they'
        }
        
        filtered_keywords = [w for w in all_keywords if w not in stop_words]
        keyword_counts = Counter(filtered_keywords)
        
        return {
            'top_keywords': dict(keyword_counts.most_common(50)),
            'total_unique_keywords': len(keyword_counts)
        }
    
    def analyze_series_patterns(self, webinars: List[Dict]) -> Dict:
        """分析系列模式"""
        series_patterns = defaultdict(list)
        
        for webinar in webinars:
            title = webinar['title_lower']
            
            # 查找系列标识
            if 'series' in title:
                series_patterns['has_series'].append(webinar['title'])
            
            # 查找编号模式（如 Part 1, Part 2）
            if re.search(r'\bpart\s+\d+\b', title):
                series_patterns['numbered_series'].append(webinar['title'])
            
            # 查找日期模式（可能是系列的一部分）
            if re.search(r'\d{4}', title):  # 年份
                series_patterns['dated'].append(webinar['title'])
        
        return {
            'has_series_count': len(series_patterns.get('has_series', [])),
            'numbered_series_count': len(series_patterns.get('numbered_series', [])),
            'dated_count': len(series_patterns.get('dated', [])),
            'series_examples': dict(list(series_patterns.items())[:10])
        }
    
    def generate_analysis_report(self, webinars: List[Dict]) -> str:
        """生成分析报告"""
        print("=" * 80)
        print("Siemens Webinar深度分析")
        print("=" * 80)
        print()
        print(f"总Webinar数: {len(webinars)}")
        print()
        
        # 分类分析
        print("分析Webinar类型...")
        type_distribution = Counter()
        tendency_distribution = Counter()
        
        # 过滤掉目录页
        valid_webinars = []
        directory_count = 0
        
        for webinar in webinars:
            classification = self.classify_webinar_type(webinar['title_lower'])
            if classification['type'] == 'directory':
                directory_count += 1
                continue  # 跳过目录页
            type_distribution[classification['type']] += 1
            tendency_distribution[classification['tendency']] += 1
            webinar['classification'] = classification
            valid_webinars.append(webinar)
        
        webinars = valid_webinars  # 更新为有效Webinar列表
        print(f"过滤掉 {directory_count} 个目录/导航页")
        
        # 主题重复检测
        print("检测主题重复...")
        duplicate_analysis = self.detect_duplicate_themes(webinars)
        
        # 话题分布
        print("分析话题分布...")
        topic_analysis = self.analyze_topic_distribution(webinars)
        
        # 系列模式
        print("分析系列模式...")
        series_analysis = self.analyze_series_patterns(webinars)
        
        # 生成报告
        report_file = self.insight_dir / "Siemens_Webinar深度分析报告.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Siemens Webinar 深度分析报告\n\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"**分析日期**: {pd.Timestamp.now().strftime('%Y-%m-%d')}\n")
            f.write(f"**总Webinar数**: {len(webinars):,}\n\n")
            f.write("=" * 80 + "\n\n")
            
            # 执行摘要
            f.write("## 执行摘要\n\n")
            f.write("本报告深入分析Siemens的Webinar策略，包括：\n")
            f.write("1. **内容倾向分析** - 科普/教育 vs 产品用法\n")
            f.write("2. **主题重复检测** - 是否存在大量重复主题\n")
            f.write("3. **话题分布** - 主要讨论的话题领域\n")
            f.write("4. **系列模式** - 是否有系列化组织\n\n")
            
            # 内容倾向分析
            f.write("## 1. 内容倾向分析\n\n")
            f.write("### 类型分布\n\n")
            f.write("| 类型 | 数量 | 占比 | 说明 |\n")
            f.write("|------|------|------|------|\n")
            
            total = len(webinars)
            for type_name, count in type_distribution.most_common():
                pct = count / total * 100 if total > 0 else 0
                type_desc = {
                    'education': '科普/教育 - 介绍概念、趋势、基础知识',
                    'product': '产品用法 - 演示功能、使用方法、实操',
                    'technical': '技术深度 - 深入技术细节、架构、开发',
                    'mixed': '混合型 - 同时包含教育和产品内容',
                    'unknown': '未知 - 无法明确分类',
                    'directory': '目录/导航页 - 非具体内容'
                }.get(type_name, '未知')
                
                f.write(f"| {type_name} | {count:,} | {pct:.1f}% | {type_desc} |\n")
            
            f.write("\n")
            
            f.write("### 倾向分布\n\n")
            f.write("| 倾向 | 数量 | 占比 |\n")
            f.write("|------|------|------|\n")
            for tendency, count in tendency_distribution.most_common():
                pct = count / total * 100
                f.write(f"| {tendency} | {count:,} | {pct:.1f}% |\n")
            
            f.write("\n")
            
            # 类型示例
            f.write("### 各类型示例\n\n")
            for type_name in ['education', 'product', 'technical', 'mixed']:
                examples = [w for w in webinars if w['classification']['type'] == type_name][:10]
                if examples:
                    f.write(f"#### {type_name.upper()} 类型示例\n\n")
                    for i, ex in enumerate(examples, 1):
                        f.write(f"{i}. {ex['title']}\n")
                    f.write("\n")
            
            # 主题重复分析
            f.write("## 2. 主题重复检测\n\n")
            f.write(f"- **总Webinar数**: {len(webinars):,}\n")
            f.write(f"- **唯一主题数**: {duplicate_analysis['total_unique_themes']:,}\n")
            f.write(f"- **重复主题数**: {duplicate_analysis['duplicate_themes']:,}\n")
            f.write(f"- **重复率**: {duplicate_analysis['duplicate_themes']/duplicate_analysis['total_unique_themes']*100:.1f}%\n\n")
            
            if duplicate_analysis['duplicate_examples']:
                f.write("### 重复主题示例\n\n")
                for theme_key, titles in list(duplicate_analysis['duplicate_examples'].items())[:10]:
                    f.write(f"**主题**: {theme_key}\n")
                    f.write(f"**重复次数**: {len(titles)}\n")
                    f.write("**标题列表**:\n")
                    for title in titles[:5]:
                        f.write(f"- {title}\n")
                    f.write("\n")
            
            # 话题分布
            f.write("## 3. 话题分布分析\n\n")
            f.write(f"- **总关键词数**: {topic_analysis['total_unique_keywords']:,}\n\n")
            
            f.write("### Top 50 高频关键词\n\n")
            f.write("| 关键词 | 出现次数 |\n")
            f.write("|--------|----------|\n")
            for keyword, count in list(topic_analysis['top_keywords'].items())[:50]:
                f.write(f"| {keyword} | {count} |\n")
            
            f.write("\n")
            
            # 话题领域分析
            f.write("### 主要话题领域\n\n")
            topic_domains = {
                '工业自动化': ['industrial', 'automation', 'manufacturing', 'production', 'factory'],
                '数字化': ['digital', 'digitalization', 'digital twin', 'transformation'],
                'AI/机器学习': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'intelligent'],
                '网络安全': ['cybersecurity', 'security', 'cyber', 'secure'],
                '云平台': ['cloud', 'saas', 'platform', 'azure'],
                '产品系列': ['simatic', 'wincc', 'tia', 'plc', 'scada'],
                '行业应用': ['energy', 'automotive', 'pharmaceutical', 'chemical', 'oil', 'gas']
            }
            
            domain_counts = {}
            for domain, keywords in topic_domains.items():
                count = sum(topic_analysis['top_keywords'].get(kw, 0) for kw in keywords)
                if count > 0:
                    domain_counts[domain] = count
            
            for domain, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{domain}**: {count} 次提及\n")
            
            f.write("\n")
            
            # 系列模式
            f.write("## 4. 系列模式分析\n\n")
            f.write(f"- **有系列标识的Webinar**: {series_analysis['has_series_count']:,}\n")
            f.write(f"- **编号系列（Part 1, Part 2等）**: {series_analysis['numbered_series_count']:,}\n")
            f.write(f"- **包含日期的Webinar**: {series_analysis['dated_count']:,}\n\n")
            
            if series_analysis.get('series_examples'):
                f.write("### 系列示例\n\n")
                for series_type, examples in list(series_analysis['series_examples'].items())[:5]:
                    f.write(f"**{series_type}**:\n")
                    for ex in examples[:3]:
                        f.write(f"- {ex}\n")
                    f.write("\n")
            
            # 深度洞察
            f.write("## 5. 深度洞察\n\n")
            
            # 倾向判断
            education_ratio = type_distribution.get('education', 0) / total * 100
            product_ratio = type_distribution.get('product', 0) / total * 100
            
            f.write("### 内容倾向判断\n\n")
            if education_ratio > 50:
                f.write("**主要倾向**: **科普/教育导向**\n\n")
                f.write("Siemens的Webinar主要面向市场教育和思想领导力建设，通过科普内容建立品牌权威性。\n\n")
            elif product_ratio > 50:
                f.write("**主要倾向**: **产品用法导向**\n\n")
                f.write("Siemens的Webinar主要面向产品推广和用户培训，通过产品演示促进转化。\n\n")
            else:
                f.write("**主要倾向**: **混合策略**\n\n")
                f.write("Siemens的Webinar采用教育和产品并重的策略，既建立思想领导力，又促进产品转化。\n\n")
            
            # 主题重复判断
            duplicate_ratio = duplicate_analysis['duplicate_themes'] / duplicate_analysis['total_unique_themes'] * 100 if duplicate_analysis['total_unique_themes'] > 0 else 0
            f.write("### 主题重复情况\n\n")
            if duplicate_ratio > 30:
                f.write("**结论**: 存在**较多主题重复**\n\n")
                f.write(f"重复率: {duplicate_ratio:.1f}%，说明Siemens可能在多个系列或不同时间重复讨论相同主题。\n\n")
            elif duplicate_ratio > 10:
                f.write("**结论**: 存在**一定主题重复**\n\n")
                f.write(f"重复率: {duplicate_ratio:.1f}%，部分主题在不同系列中重复出现。\n\n")
            else:
                f.write("**结论**: 主题重复**较少**\n\n")
                f.write(f"重复率: {duplicate_ratio:.1f}%，说明Siemens的Webinar主题较为多样化。\n\n")
            
            # 策略建议
            f.write("## 6. 策略建议\n\n")
            f.write("基于以上分析，建议：\n\n")
            
            if education_ratio > product_ratio:
                f.write("1. **保持教育优势**: Siemens在教育内容方面表现突出，建议继续保持。\n")
                f.write("2. **增加产品转化**: 可以在教育内容中适当增加产品演示环节。\n")
            else:
                f.write("1. **加强思想领导力**: 可以增加行业趋势、最佳实践等教育内容。\n")
                f.write("2. **优化产品演示**: 继续优化产品演示内容，提高转化率。\n")
            
            if duplicate_ratio > 20:
                f.write("3. **减少主题重复**: 建议整合重复主题，提高内容效率。\n")
            else:
                f.write("3. **保持主题多样性**: 当前主题多样化程度良好，建议继续保持。\n")
            
            f.write("\n")
            f.write("=" * 80 + "\n")
        
        print(f"✅ 分析报告已保存: {report_file}")
        return str(report_file)
    
    def analyze(self):
        """执行完整分析"""
        # 提取Webinar标题
        webinars = self.extract_webinar_titles()
        
        if not webinars:
            print("❌ 未找到Webinar数据")
            return
        
        # 生成报告
        self.generate_analysis_report(webinars)
        
        print("\n" + "=" * 80)
        print("✅ Siemens Webinar深度分析完成！")
        print("=" * 80)


def main():
    """主函数"""
    analyzer = SiemensWebinarDeepAnalyzer()
    analyzer.analyze()


if __name__ == "__main__":
    main()

