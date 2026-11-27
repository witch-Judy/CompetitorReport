#!/usr/bin/env python3
"""
Taxonomy Intelligence Analyzer
基于网站结构（分类树）进行竞争情报分析
三个维度：业务成熟度、数字化执行力、GTM策略
"""

import json
import re
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple
import concurrent.futures
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent))


class TaxonomyIntelligenceAnalyzer:
    """分类情报分析器"""
    
    def __init__(self):
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        
        self.information_dir = project_root / "Information"
        self.insight_dir = project_root / "insight"
        self.company_reports_dir = self.insight_dir / "reports" / "company_reports"
        self.company_reports_dir.mkdir(parents=True, exist_ok=True)
        
        # 公司信息（用于报告）
        self.company_info = {
            'abb': {'name': 'ABB', 'category': 'To B工业自动化'},
            'aveva': {'name': 'AVEVA', 'category': 'To B工业软件'},
            'bosch': {'name': 'Bosch', 'category': 'To B工业自动化'},
            'cognite': {'name': 'Cognite', 'category': 'To B工业数据平台'},
            'emerson': {'name': 'Emerson', 'category': 'To B工业自动化'},
            'ge': {'name': 'GE', 'category': 'To B工业数字化'},
            'hitachi': {'name': 'Hitachi', 'category': 'To B工业自动化'},
            'hivemq': {'name': 'HiveMQ', 'category': 'To B IoT平台'},
            'honeywell': {'name': 'Honeywell', 'category': 'To B工业自动化'},
            'ignition': {'name': 'Ignition', 'category': 'To B工业自动化软件'},
            'rockwell-automation': {'name': 'Rockwell Automation', 'category': 'To B工业自动化'},
            'schneider-electric': {'name': 'Schneider Electric', 'category': 'To B能源管理和自动化'},
            'siemens': {'name': 'Siemens', 'category': 'To B工业自动化和数字化'},
            'tulip': {'name': 'Tulip', 'category': 'To B制造执行系统'},
            'yokogawa': {'name': 'Yokogawa', 'category': 'To B工业自动化'},
            'c3-ai': {'name': 'C3 AI', 'category': 'To B企业AI软件'},
        }
    
    def parse_tree_file(self, tree_file: Path) -> Dict:
        """解析complete_tree文件"""
        with open(tree_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析树结构
        lines = content.split('\n')
        tree_structure = defaultdict(list)
        current_path = []
        page_count = 0
        folder_set = set()
        
        for line in lines:
            if not line.strip() or line.strip().startswith('=') or '📋' in line:
                continue
            
            # 计算层级：数│符号的数量（每个│代表一级）
            pipe_count = line.count('│')
            level = pipe_count
            
            # 提取节点名称
            node_name = line.strip()
            # 移除树符号
            node_name = re.sub(r'^[└├│─\s]+', '', node_name)
            # 移除emoji标记
            node_name = re.sub(r'^[📁📂📄]\s*', '', node_name)
            node_name = node_name.strip()
            
            if not node_name:
                continue
            
            # 判断是文件夹还是页面
            is_folder = '📁' in line or '📂' in line
            is_page = '📄' in line
            
            if is_folder:
                # 更新当前路径
                current_path = current_path[:level]
                current_path.append(node_name)
                folder_set.add('/'.join(current_path))
            elif is_page:
                # 页面节点
                page_count += 1
                if current_path:
                    path_key = '/'.join(current_path)
                    tree_structure[path_key].append(node_name)
                else:
                    # 根级别页面
                    tree_structure['/'].append(node_name)
        
        return {
            'tree_structure': dict(tree_structure),
            'total_pages': page_count,
            'total_folders': len(folder_set),
            'raw_content': content
        }
    
    def analyze_segment_maturity(self, tree_data: Dict) -> Dict:
        """维度一：业务成熟度分析（颗粒度）"""
        tree_structure = tree_data['tree_structure']
        
        # 语言代码列表（不计算为深度）
        # 注意：需要处理各种格式，包括 "En Us" (两个词), "En-Us" (连字符), "En_Us" (下划线)
        language_codes = {
            'en', 'us', 'mx', 'br', 'in', 'gb', 'uk', 'au', 'ca', 'sg', 'hk', 'tw',
            'en-us', 'en_us', 'enus', 'en-mx', 'en_mx', 'enmx',
            'ja', 'jp', 'ja-jp', 'ja_jp', 'jajp',
            'zh', 'cn', 'zh-cn', 'zh_cn', 'zhcn',
            'de', 'fr', 'es', 'it', 'pt', 'ru', 'ko',
            'en-gb', 'en_gb', 'engb',
            'en-ca', 'en_ca', 'enca',
            'en-au', 'en_au', 'enau',
            'es-br', 'es_br', 'esbr',
            'pt-br', 'pt_br', 'ptbr'
        }
        
        def filter_language_segments(segments):
            """过滤掉语言代码段"""
            filtered = []
            for seg in segments:
                seg_lower = seg.lower().strip()
                # 检查是否是语言代码（包括 "en us" 这种空格分隔的情况）
                if seg_lower not in language_codes:
                    # 检查是否是 "en us" 这种格式（两个词）
                    words = seg_lower.split()
                    if len(words) == 2 and words[0] in language_codes and words[1] in language_codes:
                        continue  # 跳过语言代码组合
                    filtered.append(seg)
            return filtered
        
        # 分析行业分类深度
        industry_depth = {}
        industry_segments = []
        
        for path, pages in tree_structure.items():
            path_lower = path.lower()
            if 'industr' in path_lower or 'sector' in path_lower:
                segments = path.split('/')
                # 过滤语言代码后计算深度
                filtered_segments = filter_language_segments(segments)
                depth = len(filtered_segments)
                industry_name = filtered_segments[-1] if filtered_segments else path
                
                if depth not in industry_depth:
                    industry_depth[depth] = []
                industry_depth[depth].append({
                    'path': path,
                    'name': industry_name,
                    'page_count': len(pages)
                })
                
                industry_segments.append({
                    'path': path,
                    'depth': depth,
                    'pages': len(pages)
                })
        
        # 分析生命周期管理
        lifecycle_keywords = ['legacy', 'end-of-life', 'end of life', 'retrofit', 'upgrade', 'replacement', 'obsolete', 'lifecycle', 'life cycle']
        lifecycle_pages = []
        
        for path, pages in tree_structure.items():
            path_lower = path.lower()
            # 检查路径和页面名称
            page_names_lower = ' '.join([str(p).lower() for p in pages])
            combined = path_lower + ' ' + page_names_lower
            
            matched_keywords = [kw for kw in lifecycle_keywords if kw in combined]
            if matched_keywords:
                lifecycle_pages.append({
                    'path': path,
                    'page_count': len(pages),
                    'matched_keywords': matched_keywords[:3]  # 只保留前3个匹配的关键词
                })
        
        # 计算成熟度指标
        max_industry_depth = max(industry_depth.keys()) if industry_depth else 0
        avg_industry_depth = sum(s['depth'] for s in industry_segments) / len(industry_segments) if industry_segments else 0
        
        return {
            'industry_depth_distribution': {k: len(v) for k, v in industry_depth.items()},
            'max_industry_depth': max_industry_depth,
            'avg_industry_depth': float(avg_industry_depth),
            'industry_segments': industry_segments[:20],  # Top 20
            'lifecycle_management': {
                'has_lifecycle_pages': len(lifecycle_pages) > 0,
                'lifecycle_page_count': len(lifecycle_pages),
                'lifecycle_paths': lifecycle_pages[:10]
            },
            'maturity_score': self._calculate_maturity_score(max_industry_depth, len(lifecycle_pages))
        }
    
    def _calculate_maturity_score(self, max_depth: int, lifecycle_count: int) -> str:
        """计算成熟度评分"""
        if max_depth >= 4 and lifecycle_count >= 3:
            return "高成熟度 - 场景化解决方案 + 完整生命周期管理"
        elif max_depth >= 3 and lifecycle_count >= 1:
            return "中高成熟度 - 细分行业覆盖 + 基础生命周期管理"
        elif max_depth >= 2:
            return "中等成熟度 - 基础行业分类"
        else:
            return "低成熟度 - 通用产品导向"
    
    def analyze_digital_execution(self, tree_data: Dict) -> Dict:
        """维度二：数字化执行力分析"""
        tree_structure = tree_data['tree_structure']
        
        # 功能性页面关键词
        functional_keywords = {
            'portal': ['portal', 'login', 'dashboard', 'my-account'],
            'configurator': ['configurator', 'config', 'selector', 'wizard'],
            'calculator': ['calculator', 'calc', 'tool', 'estimator'],
            'exchange': ['exchange', 'marketplace', 'store', 'shop'],
            'remote': ['remote', 'remote-access', 'remote-monitoring', 'iot'],
            'api': ['api', 'sdk', 'developer', 'integration'],
            'training': ['training', 'academy', 'learning', 'certification']
        }
        
        functional_pages = defaultdict(list)
        
        for path, pages in tree_structure.items():
            path_lower = path.lower()
            for func_type, keywords in functional_keywords.items():
                if any(kw in path_lower for kw in keywords):
                    functional_pages[func_type].append({
                        'path': path,
                        'page_count': len(pages)
                    })
        
        # 生态系统建设
        ecosystem_keywords = ['partner', 'developer', 'ecosystem', 'venture', 'startup', 'channel']
        ecosystem_pages = []
        
        for path, pages in tree_structure.items():
            path_lower = path.lower()
            if any(kw in path_lower for kw in ecosystem_keywords):
                ecosystem_pages.append({
                    'path': path,
                    'page_count': len(pages),
                    'type': self._classify_ecosystem_type(path_lower)
                })
        
        return {
            'functional_pages': {k: len(v) for k, v in functional_pages.items()},
            'functional_details': dict(functional_pages),
            'ecosystem_pages': len(ecosystem_pages),
            'ecosystem_details': ecosystem_pages[:15],
            'digital_execution_score': self._calculate_digital_score(functional_pages, ecosystem_pages)
        }
    
    def _classify_ecosystem_type(self, path: str) -> str:
        """分类生态系统类型"""
        if 'partner' in path:
            return '合作伙伴生态'
        elif 'developer' in path or 'sdk' in path:
            return '开发者生态'
        elif 'venture' in path or 'startup' in path:
            return '创投生态'
        elif 'channel' in path:
            return '渠道生态'
        else:
            return '其他生态'
    
    def _calculate_digital_score(self, functional_pages: Dict, ecosystem_pages: List) -> str:
        """计算数字化执行力评分"""
        total_functional = sum(len(v) for v in functional_pages.values())
        
        if total_functional >= 5 and len(ecosystem_pages) >= 3:
            return "高执行力 - 服务产品化 + 完整生态建设"
        elif total_functional >= 3 and len(ecosystem_pages) >= 1:
            return "中高执行力 - 基础数字化工具 + 生态布局"
        elif total_functional >= 1:
            return "中等执行力 - 部分数字化工具"
        else:
            return "低执行力 - 传统服务模式"
    
    def analyze_content_strategy(self, tree_data: Dict) -> Dict:
        """维度三：GTM策略分析（内容资产分布）"""
        tree_structure = tree_data['tree_structure']
        
        # 内容类型关键词
        content_keywords = {
            'stories': ['story', 'stories', 'case-study', 'customer-story', 'success'],
            'blog': ['blog', 'article', 'news', 'press'],
            'webinar': ['webinar', 'event', 'workshop'],
            'resource': ['resource', 'whitepaper', 'ebook', 'guide', 'download'],
            'product': ['product', 'solution', 'platform'],
            'industry': ['industry', 'industries', 'sector']
        }
        
        content_distribution = defaultdict(lambda: {'count': 0, 'paths': []})
        
        for path, pages in tree_structure.items():
            path_lower = path.lower()
            page_count = len(pages)
            
            for content_type, keywords in content_keywords.items():
                if any(kw in path_lower for kw in keywords):
                    content_distribution[content_type]['count'] += page_count
                    content_distribution[content_type]['paths'].append({
                        'path': path,
                        'page_count': page_count
                    })
        
        # 分析内容厚度
        content_thickness = {}
        for content_type, data in content_distribution.items():
            total_pages = data['count']
            path_count = len(data['paths'])
            avg_pages_per_path = total_pages / path_count if path_count > 0 else 0
            
            content_thickness[content_type] = {
                'total_pages': total_pages,
                'path_count': path_count,
                'avg_pages_per_path': float(avg_pages_per_path),
                'top_paths': sorted(data['paths'], key=lambda x: x['page_count'], reverse=True)[:5]
            }
        
        # 计算内容成熟度
        stories_count = content_distribution['stories']['count']
        blog_count = content_distribution['blog']['count']
        total_content = sum(data['count'] for data in content_distribution.values())
        
        return {
            'content_distribution': dict(content_thickness),
            'total_content_pages': total_content,
            'stories_count': stories_count,
            'blog_count': blog_count,
            'content_maturity_score': self._calculate_content_maturity(stories_count, blog_count, total_content)
        }
    
    def _calculate_content_maturity(self, stories: int, blog: int, total: int) -> str:
        """计算内容成熟度评分"""
        if stories >= 50 and blog >= 100:
            return "高成熟度 - 丰富案例故事 + 活跃内容营销"
        elif stories >= 20 and blog >= 50:
            return "中高成熟度 - 良好案例覆盖 + 内容营销"
        elif stories >= 10 or blog >= 20:
            return "中等成熟度 - 基础内容营销"
        else:
            return "低成熟度 - 内容资产不足"
    
    def generate_llm_analysis_prompt(self, company_name: str, analysis_data: Dict) -> str:
        """生成LLM分析提示词"""
        prompt = f"""# {company_name} - Taxonomy Intelligence 深度分析

## 数据概览
- 总页面数: {analysis_data['total_pages']:,}
- 总文件夹数: {analysis_data['total_folders']:,}

## 维度一：业务成熟度 (Segment Maturity)

### 行业分类深度
- 最大深度: {analysis_data['segment_maturity']['max_industry_depth']}层
- 平均深度: {analysis_data['segment_maturity']['avg_industry_depth']:.1f}层
- 成熟度评分: {analysis_data['segment_maturity']['maturity_score']}

### 行业细分示例（Top 10）:
"""
        for seg in analysis_data['segment_maturity']['industry_segments'][:10]:
            prompt += f"- {seg['path']} (深度{seg['depth']}, {seg['pages']}页)\n"
        
        prompt += f"""
### 生命周期管理
- 是否有生命周期页面: {'是' if analysis_data['segment_maturity']['lifecycle_management']['has_lifecycle_pages'] else '否'}
- 生命周期页面数: {analysis_data['segment_maturity']['lifecycle_management']['lifecycle_page_count']}

## 维度二：数字化执行力 (Digital Execution)

### 功能性页面
"""
        for func_type, count in analysis_data['digital_execution']['functional_pages'].items():
            prompt += f"- {func_type}: {count}个\n"
        
        prompt += f"""
- 数字化执行力评分: {analysis_data['digital_execution']['digital_execution_score']}

### 生态系统建设
- 生态系统页面数: {analysis_data['digital_execution']['ecosystem_pages']}

## 维度三：GTM策略 (Content Strategy)

### 内容资产分布
"""
        for content_type, data in analysis_data['content_strategy']['content_distribution'].items():
            prompt += f"- {content_type}: {data['total_pages']}页 ({data['path_count']}个路径)\n"
        
        prompt += f"""
- 总内容页面: {analysis_data['content_strategy']['total_content_pages']:,}
- 案例故事数: {analysis_data['content_strategy']['stories_count']}
- 博客文章数: {analysis_data['content_strategy']['blog_count']}
- 内容成熟度评分: {analysis_data['content_strategy']['content_maturity_score']}

---

请基于以上数据，按照以下格式进行深度分析：

## 执行漏洞 (Execution Gaps)

### 1. 业务成熟度漏洞
- [分析行业分类的颗粒度，识别哪些细分领域覆盖不足]
- [分析生命周期管理，识别售后执行漏洞]

### 2. 数字化执行力漏洞
- [分析功能性页面的缺失，识别数字化工具不足]
- [分析生态系统建设，识别生态空白]

### 3. GTM策略漏洞
- [分析内容资产分布，识别内容营销薄弱环节]
- [对比行业最佳实践，识别内容执行差距]

## 竞争机会 (Competitive Opportunities)

### 1. 细分市场机会
- [基于行业分类深度，识别可以切入的细分领域]
- [基于生命周期管理，识别可以攻击的售后漏洞]

### 2. 数字化差异化机会
- [基于功能性页面分析，识别可以超越的数字化工具]
- [基于生态系统分析，识别可以建设的生态优势]

### 3. 内容营销机会
- [基于内容分布，识别可以填补的内容空白]
- [基于内容厚度，识别可以超越的内容策略]

## 战略洞察 (Strategic Insights)

### 1. 业务架构洞察
- [总结业务成熟度，判断公司发展阶段]
- [分析业务重点，识别战略方向]

### 2. 执行能力洞察
- [总结数字化执行力，判断执行成熟度]
- [分析服务模式，识别竞争优势]

### 3. 营销策略洞察
- [总结GTM策略，判断营销成熟度]
- [分析内容策略，识别营销重点]

请用中文回答，分析要深入、具体、可执行。
"""
        return prompt
    
    def analyze_company(self, company_key: str) -> Dict:
        """分析单个公司"""
        tree_file = self.information_dir / f"{company_key}_analyzed_complete_tree.txt"
        
        if not tree_file.exists():
            print(f"  ⚠️  文件不存在: {tree_file}")
            return None
        
        print(f"  分析 {company_key}...")
        
        # 解析树文件
        tree_data = self.parse_tree_file(tree_file)
        
        # 三个维度分析
        segment_maturity = self.analyze_segment_maturity(tree_data)
        digital_execution = self.analyze_digital_execution(tree_data)
        content_strategy = self.analyze_content_strategy(tree_data)
        
        return {
            'company': company_key,
            'company_info': self.company_info.get(company_key, {'name': company_key, 'category': 'Unknown'}),
            'tree_data': tree_data,
            'segment_maturity': segment_maturity,
            'digital_execution': digital_execution,
            'content_strategy': content_strategy
        }
    
    def generate_report(self, analysis_data: Dict, llm_insights: str = None):
        """生成分析报告"""
        company_key = analysis_data['company']
        company_name = analysis_data['company_info']['name']
        
        report_file = self.company_reports_dir / f"{company_name}_Taxonomy_Intelligence_分析报告.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# {company_name} - Taxonomy Intelligence 深度分析报告\n\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"**分析日期**: {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"**分析方法**: 基于网站结构（分类树）的竞争情报分析\n\n")
            f.write("=" * 80 + "\n\n")
            
            # 数据概览
            f.write("## 数据概览\n\n")
            f.write(f"- **总页面数**: {analysis_data['tree_data']['total_pages']:,}\n")
            f.write(f"- **总文件夹数**: {analysis_data['tree_data']['total_folders']:,}\n\n")
            
            # 维度一：业务成熟度
            f.write("## 维度一：业务成熟度 (Segment Maturity)\n\n")
            sm = analysis_data['segment_maturity']
            f.write(f"### 行业分类深度\n\n")
            f.write(f"- **最大深度**: {sm['max_industry_depth']}层\n")
            f.write(f"- **平均深度**: {sm['avg_industry_depth']:.1f}层\n")
            f.write(f"- **成熟度评分**: {sm['maturity_score']}\n\n")
            
            f.write("**行业深度分布**:\n")
            for depth, count in sorted(sm['industry_depth_distribution'].items()):
                f.write(f"- {depth}层: {count}个分类\n")
            f.write("\n")
            
            f.write("**行业细分示例（Top 10）**:\n")
            for seg in sm['industry_segments'][:10]:
                f.write(f"- {seg['path']} (深度{seg['depth']}, {seg['pages']}页)\n")
            f.write("\n")
            
            f.write("### 生命周期管理\n\n")
            lc = sm['lifecycle_management']
            f.write(f"- **是否有生命周期页面**: {'是' if lc['has_lifecycle_pages'] else '否'}\n")
            f.write(f"- **生命周期页面数**: {lc['lifecycle_page_count']}\n")
            if lc['lifecycle_paths']:
                f.write("\n**生命周期页面示例**:\n")
                for lp in lc['lifecycle_paths'][:5]:
                    f.write(f"- {lp['path']} ({lp['page_count']}页)\n")
            f.write("\n")
            
            # 维度二：数字化执行力
            f.write("## 维度二：数字化执行力 (Digital Execution)\n\n")
            de = analysis_data['digital_execution']
            f.write("### 功能性页面\n\n")
            for func_type, count in de['functional_pages'].items():
                f.write(f"- **{func_type}**: {count}个\n")
            f.write(f"\n**数字化执行力评分**: {de['digital_execution_score']}\n\n")
            
            if de['functional_details']:
                f.write("**功能性页面详情**:\n")
                for func_type, pages in de['functional_details'].items():
                    if pages:
                        f.write(f"\n{func_type}:\n")
                        for page in pages[:3]:
                            f.write(f"  - {page['path']} ({page['page_count']}页)\n")
                f.write("\n")
            
            f.write("### 生态系统建设\n\n")
            f.write(f"- **生态系统页面数**: {de['ecosystem_pages']}\n")
            if de['ecosystem_details']:
                f.write("\n**生态系统页面示例**:\n")
                for eco in de['ecosystem_details'][:10]:
                    f.write(f"- {eco['path']} ({eco['type']}, {eco['page_count']}页)\n")
            f.write("\n")
            
            # 维度三：GTM策略
            f.write("## 维度三：GTM策略 (Content Strategy)\n\n")
            cs = analysis_data['content_strategy']
            f.write("### 内容资产分布\n\n")
            for content_type, data in cs['content_distribution'].items():
                f.write(f"- **{content_type}**: {data['total_pages']}页 ({data['path_count']}个路径)\n")
            f.write("\n")
            
            f.write(f"- **总内容页面**: {cs['total_content_pages']:,}\n")
            f.write(f"- **案例故事数**: {cs['stories_count']}\n")
            f.write(f"- **博客文章数**: {cs['blog_count']}\n")
            f.write(f"- **内容成熟度评分**: {cs['content_maturity_score']}\n\n")
            
            if cs['content_distribution']:
                f.write("**内容分布详情**:\n")
                for content_type, data in cs['content_distribution'].items():
                    if data['top_paths']:
                        f.write(f"\n{content_type} (Top 5路径):\n")
                        for path_info in data['top_paths']:
                            f.write(f"  - {path_info['path']} ({path_info['page_count']}页)\n")
                f.write("\n")
            
            # LLM深度分析
            if llm_insights:
                f.write("=" * 80 + "\n\n")
                f.write("## LLM深度分析\n\n")
                f.write(llm_insights)
                f.write("\n")
            
            f.write("=" * 80 + "\n")
        
        return report_file
    
    def analyze_all_companies(self, use_llm: bool = False):
        """分析所有公司"""
        print("=" * 80)
        print("Taxonomy Intelligence 深度分析")
        print("=" * 80)
        print()
        
        # 找到所有complete_tree文件
        tree_files = list(self.information_dir.glob("*_analyzed_complete_tree.txt"))
        company_keys = [f.stem.replace('_analyzed_complete_tree', '') for f in tree_files]
        
        print(f"找到 {len(company_keys)} 个公司\n")
        
        # 并行分析
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_company = {
                executor.submit(self.analyze_company, company_key): company_key 
                for company_key in company_keys
            }
            
            for future in concurrent.futures.as_completed(future_to_company):
                company_key = future_to_company[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    print(f"  ❌ {company_key} 分析失败: {e}")
        
        print()
        
        # 生成报告
        print("生成报告...")
        
        if use_llm:
            print("调用LLM进行深度分析...")
            try:
                from analysis.llm_taxonomy_analyzer import LLMTaxonomyAnalyzer
                llm_analyzer = LLMTaxonomyAnalyzer()
                
                # 并行调用LLM
                enhanced_results = []
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    future_to_result = {
                        executor.submit(llm_analyzer.generate_analysis_with_llm, result): result
                        for result in results
                    }
                    
                    for future in concurrent.futures.as_completed(future_to_result):
                        result = future_to_result[future]
                        try:
                            llm_insights = future.result()
                            result['llm_insights'] = llm_insights
                            enhanced_results.append(result)
                            print(f"  ✅ {result['company_info']['name']} LLM分析完成")
                        except Exception as e:
                            print(f"  ⚠️  {result['company_info']['name']} LLM分析跳过: {e}")
                            enhanced_results.append(result)
                
                results = enhanced_results
            except Exception as e:
                print(f"  ⚠️  LLM模块加载失败: {e}")
                print("  提示: 使用 --use-llm 需要设置 OPENAI_API_KEY 环境变量")
        
        for analysis_data in results:
            llm_insights = analysis_data.get('llm_insights')
            report_file = self.generate_report(analysis_data, llm_insights)
            print(f"  ✅ {analysis_data['company_info']['name']}: {report_file.name}")
        
        print()
        print("=" * 80)
        print("分析完成")
        print("=" * 80)
        print(f"共生成 {len(results)} 份报告")
        print(f"报告位置: {self.company_reports_dir}")


if __name__ == "__main__":
    analyzer = TaxonomyIntelligenceAnalyzer()
    analyzer.analyze_all_companies(use_llm=False)

