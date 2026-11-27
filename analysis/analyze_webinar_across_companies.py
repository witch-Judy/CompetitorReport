#!/usr/bin/env python3
"""
分析所有竞品公司的Webinar情况
统计每个公司的webinar数量，并分析webinar的主题分类
"""

import pandas as pd
import re
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple


class WebinarAnalyzer:
    """Webinar分析器"""
    
    def __init__(self):
        """初始化分析器"""
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        
        self.output_data_dir = project_root / "output_data"
        self.information_dir = project_root / "Information"
        self.knowledge_dir = project_root / "Knowledge"
        
        # 创建输出目录
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_company_webinars(self, company: str) -> Dict:
        """分析单个公司的webinar情况"""
        # 加载CSV数据
        csv_file = self.output_data_dir / f"{company}_analyzed.csv"
        if not csv_file.exists():
            return None
        
        df = pd.read_csv(csv_file)
        
        # 筛选webinar
        webinar_mask = (
            (df['content_type'] == 'webinar') |
            (df['is_webinar'] == True) |
            (df['url'].str.contains('webinar', case=False, na=False)) |
            (df['path'].str.contains('webinar', case=False, na=False))
        )
        
        webinar_df = df[webinar_mask]
        
        if len(webinar_df) == 0:
            return {
                'company': company,
                'total_webinars': 0,
                'webinar_urls': [],
                'webinar_categories': {},
                'webinar_topics': []
            }
        
        # 分析分类
        categories = Counter()
        topics = []
        
        for _, row in webinar_df.iterrows():
            # 从URL路径中提取分类
            url = str(row.get('url', ''))
            path = str(row.get('path', ''))
            section = str(row.get('section', ''))
            subsection = str(row.get('subsection', ''))
            
            # 提取可能的主题关键词
            url_lower = url.lower()
            path_lower = path.lower()
            
            # 从路径中提取主题
            if section and section != 'nan':
                categories[section] += 1
            
            if subsection and subsection != 'nan':
                categories[subsection] += 1
            
            # 从URL中提取关键词作为主题
            # 移除常见的webinar相关词和文件扩展名
            url_clean = re.sub(r'webinar[s]?', '', url_lower, flags=re.IGNORECASE)
            url_clean = re.sub(r'on-demand', '', url_clean, flags=re.IGNORECASE)
            url_clean = re.sub(r'\.html?$', '', url_clean)  # 移除.html扩展名
            
            # 提取可能的主题词（通常是URL中的关键词）
            path_segments = [seg for seg in path.split('/') if seg and seg not in ['webinar', 'webinars', 'on-demand', 'webinars-videos']]
            
            # 过滤掉无意义的segment
            filtered_segments = []
            for seg in path_segments:
                # 过滤掉纯数字、文件扩展名、太短的
                if (len(seg) > 3 and 
                    not seg.isdigit() and 
                    not seg.endswith('.html') and 
                    seg not in ['en', 'de', 'fr', 'es', 'zh', 'ja', 'resources', 'company']):
                    filtered_segments.append(seg)
            
            if filtered_segments:
                # 最后一个segment通常是主题，但也要考虑前面的分类
                last_segment = filtered_segments[-1]
                if len(last_segment) > 3:
                    topics.append(last_segment)
                
                # 如果最后一个是数字或文件名，取倒数第二个
                if len(filtered_segments) > 1 and (last_segment.isdigit() or '.' in last_segment):
                    topics.append(filtered_segments[-2])
        
        return {
            'company': company,
            'total_webinars': len(webinar_df),
            'webinar_urls': webinar_df['url'].head(10).tolist(),
            'webinar_categories': dict(categories.most_common(10)),
            'webinar_topics': topics[:20]  # 前20个主题
        }
    
    def analyze_webinar_from_tree(self, company: str) -> Dict:
        """从complete_tree中分析webinar主题"""
        tree_file = self.information_dir / f"{company}_analyzed_complete_tree.txt"
        
        if not tree_file.exists():
            return {}
        
        try:
            with open(tree_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找webinar相关的行
            webinar_lines = []
            lines = content.split('\n')
            
            for line in lines:
                if 'webinar' in line.lower():
                    webinar_lines.append(line.strip())
            
            # 分析webinar的主题
            topics = []
            categories = []
            
            for line in webinar_lines:
                # 提取完整的标题文本
                # 移除tree结构符号
                line_clean = re.sub(r'[│├─└📄📂\s]+', ' ', line).strip()
                line_clean = re.sub(r'\.html?$', '', line_clean, flags=re.IGNORECASE)
                
                if not line_clean or len(line_clean) < 5:
                    continue
                
                # 提取webinar相关的主题
                line_lower = line_clean.lower()
                
                # 如果webinar在标题中
                if 'webinar' in line_lower:
                    # 移除webinar关键词
                    title_without_webinar = re.sub(r'\bwebinar[s]?\b', '', line_lower, flags=re.IGNORECASE).strip()
                    
                    # 提取有意义的词（长度>3，不是常见停用词）
                    stop_words = {
                        # 常见停用词
                        'on', 'demand', 'register', 'watch', 'click', 'here', 'more', 'view', 'series',
                        'the', 'and', 'for', 'with', 'from', 'to', 'your', 'you', 'are', 'this', 'that',
                        'these', 'those', 'what', 'which', 'when', 'where', 'how', 'why', 'who', 'whom',
                        'their', 'them', 'they', 'have', 'has', 'had', 'been', 'being', 'was', 'were',
                        'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can', 'about',
                        'into', 'over', 'after', 'under', 'above', 'below', 'between', 'among', 'through',
                        'during', 'before', 'after', 'since', 'until', 'while', 'because', 'although',
                        'however', 'therefore', 'furthermore', 'moreover', 'nevertheless', 'meanwhile',
                        # 无意义的动词/形容词
                        'improve', 'improving', 'better', 'best', 'good', 'great', 'new', 'latest',
                        'like', 'design', 'make', 'makes', 'made', 'take', 'takes', 'taking', 'get', 'gets',
                        'getting', 'got', 'give', 'gives', 'giving', 'gave', 'know', 'knows', 'knowing',
                        'knew', 'see', 'sees', 'seeing', 'saw', 'come', 'comes', 'coming', 'came', 'go',
                        'goes', 'going', 'went', 'think', 'thinks', 'thinking', 'thought', 'say', 'says',
                        'saying', 'said', 'tell', 'tells', 'telling', 'told', 'use', 'uses', 'using', 'used'
                    }
                    # 提取单词，移除标点
                    import string
                    words_raw = title_without_webinar.translate(str.maketrans('', '', string.punctuation)).split()
                    words = [w for w in words_raw 
                             if len(w) > 3 and w.lower() not in stop_words and not w.isdigit() and w.isalpha()]
                    
                    # 提取关键词（通常是标题中的重要词）
                    if words:
                        # 优先选择非品牌名和合作伙伴名的词
                        brand_words = {'siemens', 'cognite', 'yokogawa', 'ignition', 'hivemq', 'emerson', 'honeywell', 'rockwell', 'automation'}
                        # 合作伙伴/第三方公司名称
                        partner_words = {'outsystems', 'pwc', 'microsoft', 'aws', 'google', 'ibm', 'oracle', 'sap', 'salesforce', 'deloitte', 'accenture', 'kpmg', 'ey', 'ernst'}
                        # 合并过滤
                        exclude_words = brand_words | partner_words
                        meaningful_words = [w for w in words if w.lower() not in exclude_words]
                        
                        if meaningful_words:
                            # 选择前2-3个有意义的词作为主题
                            topics.extend(meaningful_words[:3])
                        else:
                            # 如果没有非品牌词，使用所有词
                            topics.extend(words[:3])
                
                # 从层级结构中提取分类
                # 计算缩进层级
                indent_level = len(line) - len(line.lstrip())
                if indent_level > 0:
                    # 提取分类（通常是webinar前面的层级）
                    parts = line.split('webinar')[0].strip()
                    if parts:
                        # 提取最后一个非空部分作为分类
                        clean_parts = [p.strip() for p in parts.split('│') if p.strip()]
                        if clean_parts:
                            category = clean_parts[-1].replace('├──', '').replace('└──', '').replace('📄', '').replace('📂', '').strip()
                            if category and len(category) > 2 and category.lower() not in ['webinar', 'webinars']:
                                categories.append(category)
            
            # 统计
            topic_counts = Counter(topics)
            category_counts = Counter(categories)
            
            # 如果所有词频率相同，返回所有词；否则返回频率最高的
            if topic_counts:
                max_count = max(topic_counts.values())
                # 如果所有词频率相同，返回所有词
                if all(count == max_count for count in topic_counts.values()):
                    topics_dict = dict(topic_counts)
                else:
                    # 否则返回频率最高的词
                    topics_dict = dict(topic_counts.most_common(10))
            else:
                topics_dict = {}
            
            if category_counts:
                max_cat_count = max(category_counts.values())
                if all(count == max_cat_count for count in category_counts.values()):
                    categories_dict = dict(category_counts)
                else:
                    categories_dict = dict(category_counts.most_common(10))
            else:
                categories_dict = {}
            
            return {
                'webinar_lines_count': len(webinar_lines),
                'topics': topics_dict,
                'categories': categories_dict,
                'sample_lines': webinar_lines[:10]
            }
        
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_all_companies(self) -> pd.DataFrame:
        """分析所有公司"""
        print("=" * 80)
        print("分析所有公司的Webinar情况")
        print("=" * 80)
        print()
        
        # 获取所有公司
        csv_files = sorted(self.output_data_dir.glob("*_analyzed.csv"))
        companies = [f.stem.replace('_analyzed', '') for f in csv_files]
        
        results = []
        
        for company in companies:
            print(f"分析: {company}")
            
            # 从CSV分析
            csv_analysis = self.analyze_company_webinars(company)
            
            # 从tree分析
            tree_analysis = self.analyze_webinar_from_tree(company)
            
            if csv_analysis:
                # 获取所有主题（如果频率相同，返回所有；否则返回频率最高的）
                topics_dict = tree_analysis.get('topics', {})
                if topics_dict:
                    # 如果所有词频率相同，返回所有词；否则按频率排序
                    topics_list = list(topics_dict.keys())
                    # 检查是否所有词频率相同
                    if len(set(topics_dict.values())) == 1:
                        # 所有词频率相同，返回所有词
                        topics_str = ', '.join(topics_list)
                    else:
                        # 按频率排序
                        sorted_topics = sorted(topics_dict.items(), key=lambda x: x[1], reverse=True)
                        topics_str = ', '.join([t[0] for t in sorted_topics])
                else:
                    topics_str = ''
                
                result = {
                    'company': company,
                    'total_webinars': csv_analysis['total_webinars'],
                    'main_categories': ', '.join(list(csv_analysis['webinar_categories'].keys())[:5]),
                    'top_topics': ', '.join(csv_analysis['webinar_topics'][:5]),
                    'tree_webinar_count': tree_analysis.get('webinar_lines_count', 0),
                    'tree_topics': topics_str,  # 现在返回所有词（如果频率相同）
                    'tree_categories': ', '.join(list(tree_analysis.get('categories', {}).keys())[:5])
                }
                results.append(result)
                
                print(f"  ✅ Webinar数量: {csv_analysis['total_webinars']}")
                if tree_analysis.get('topics'):
                    print(f"  ✅ 主要主题: {', '.join(list(tree_analysis['topics'].keys())[:3])}")
            else:
                print(f"  ❌ 数据文件不存在")
            
            print()
        
        df = pd.DataFrame(results)
        return df
    
    def generate_webinar_report(self, df: pd.DataFrame) -> str:
        """生成Webinar分析报告"""
        report_file = self.knowledge_dir / "所有公司Webinar分析报告.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 所有竞品公司Webinar分析报告\n\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"**分析日期**: {pd.Timestamp.now().strftime('%Y-%m-%d')}\n")
            f.write(f"**公司数量**: {len(df)}\n\n")
            f.write("=" * 80 + "\n\n")
            
            # 总体统计
            f.write("## 总体统计\n\n")
            f.write(f"- **总Webinar数**: {df['total_webinars'].sum():,}\n")
            f.write(f"- **平均每公司Webinar数**: {df['total_webinars'].mean():.1f}\n")
            f.write(f"- **最多Webinar的公司**: {df.loc[df['total_webinars'].idxmax(), 'company']} ({df['total_webinars'].max()}个)\n")
            f.write(f"- **有Webinar的公司数**: {len(df[df['total_webinars'] > 0])}\n\n")
            
            # 详细表格
            f.write("## 各公司Webinar详细分析\n\n")
            f.write("| 公司 | Webinar数量 | 主要分类 | 主要主题 | Tree中的主题 |\n")
            f.write("|------|------------|----------|----------|-------------|\n")
            
            # 按webinar数量排序
            df_sorted = df.sort_values('total_webinars', ascending=False)
            
            for _, row in df_sorted.iterrows():
                company = row['company']
                count = int(row['total_webinars'])
                categories = row['main_categories'][:50] if pd.notna(row['main_categories']) else '-'
                topics = row['top_topics'][:50] if pd.notna(row['top_topics']) else '-'
                tree_topics = row['tree_topics'][:50] if pd.notna(row['tree_topics']) else '-'
                
                f.write(f"| {company} | {count} | {categories} | {topics} | {tree_topics} |\n")
            
            f.write("\n")
            
            # 按数量分组
            f.write("## Webinar数量分布\n\n")
            f.write("| 数量范围 | 公司数 | 公司列表 |\n")
            f.write("|----------|--------|----------|\n")
            
            ranges = [
                (0, 0, "无"),
                (1, 10, "1-10"),
                (11, 50, "11-50"),
                (51, 200, "51-200"),
                (201, 1000, "201-1000"),
                (1001, float('inf'), "1000+")
            ]
            
            for min_count, max_count, label in ranges:
                if max_count == float('inf'):
                    companies_in_range = df_sorted[df_sorted['total_webinars'] >= min_count]
                else:
                    companies_in_range = df_sorted[
                        (df_sorted['total_webinars'] >= min_count) & 
                        (df_sorted['total_webinars'] <= max_count)
                    ]
                
                if len(companies_in_range) > 0:
                    company_list = ', '.join(companies_in_range['company'].tolist())
                    f.write(f"| {label} | {len(companies_in_range)} | {company_list} |\n")
            
            f.write("\n")
            
            # Webinar主题分析
            f.write("## Webinar主题分析\n\n")
            f.write("### 各公司Webinar主要主题\n\n")
            
            for _, row in df_sorted[df_sorted['total_webinars'] > 0].iterrows():
                company = row['company']
                f.write(f"#### {company} ({int(row['total_webinars'])}个)\n\n")
                
                if pd.notna(row['tree_topics']) and row['tree_topics']:
                    f.write(f"**主要主题**: {row['tree_topics']}\n\n")
                
                if pd.notna(row['tree_categories']) and row['tree_categories']:
                    f.write(f"**分类**: {row['tree_categories']}\n\n")
                
                f.write("\n")
            
            f.write("=" * 80 + "\n")
        
        print(f"✅ Webinar分析报告已保存: {report_file}")
        return str(report_file)
    
    def generate_webinar_table(self, df: pd.DataFrame) -> str:
        """生成简化的表格报告"""
        table_file = self.knowledge_dir / "所有公司Webinar统计表.md"
        
        with open(table_file, 'w', encoding='utf-8') as f:
            f.write("# 所有竞品公司Webinar统计表\n\n")
            f.write("=" * 80 + "\n\n")
            
            # 主要表格
            f.write("## Webinar统计表\n\n")
            f.write("| 排名 | 公司 | Webinar数量 | 主要分类 | 主要主题 |\n")
            f.write("|------|------|------------|----------|----------|\n")
            
            df_sorted = df.sort_values('total_webinars', ascending=False)
            
            for rank, (_, row) in enumerate(df_sorted.iterrows(), 1):
                company = row['company']
                count = int(row['total_webinars'])
                categories = row['main_categories'][:40] if pd.notna(row['main_categories']) and row['main_categories'] else '-'
                topics = row['tree_topics'][:40] if pd.notna(row['tree_topics']) and row['tree_topics'] else '-'
                
                f.write(f"| {rank} | {company} | {count} | {categories} | {topics} |\n")
            
            f.write("\n")
            f.write("=" * 80 + "\n")
            f.write("\n**说明**:\n")
            f.write("- **Webinar数量**: 从analyzed.csv中统计的webinar相关URL数量\n")
            f.write("- **主要分类**: 从URL路径中提取的分类信息\n")
            f.write("- **主要主题**: 从complete_tree中提取的webinar主题关键词\n")
        
        print(f"✅ Webinar统计表已保存: {table_file}")
        return str(table_file)


def main():
    """主函数"""
    analyzer = WebinarAnalyzer()
    
    # 分析所有公司
    df = analyzer.analyze_all_companies()
    
    # 保存CSV
    csv_file = analyzer.knowledge_dir / "所有公司Webinar统计.csv"
    df.to_csv(csv_file, index=False, encoding='utf-8')
    print(f"✅ Webinar统计数据已保存: {csv_file}")
    print()
    
    # 生成报告
    analyzer.generate_webinar_report(df)
    analyzer.generate_webinar_table(df)
    
    print("=" * 80)
    print("✅ 所有公司Webinar分析完成！")
    print("=" * 80)
    print()
    print("📁 生成的文件:")
    print(f"  - {csv_file}")
    print(f"  - {analyzer.knowledge_dir / '所有公司Webinar分析报告.md'}")
    print(f"  - {analyzer.knowledge_dir / '所有公司Webinar统计表.md'}")


if __name__ == "__main__":
    main()

