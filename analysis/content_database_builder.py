#!/usr/bin/env python3
"""
内容营销数据库构建器
构建庞大的内容营销数据库，包括：
1. 内容分类体系
2. 内容元数据（标题、描述、结构等）
3. 内容写作模式分析
4. 内容模板库
"""

import pandas as pd
import re
import json
import time
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import hashlib


class ContentDatabaseBuilder:
    """内容营销数据库构建器"""
    
    def __init__(self, output_data_dir: Path = None, knowledge_dir: Path = None, 
                 content_db_dir: Path = None):
        """初始化构建器"""
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        
        if output_data_dir is None:
            self.output_data_dir = project_root / "output_data"
        else:
            self.output_data_dir = Path(output_data_dir)
        
        if knowledge_dir is None:
            self.knowledge_dir = project_root / "Knowledge"
        else:
            self.knowledge_dir = Path(knowledge_dir)
        
        if content_db_dir is None:
            self.content_db_dir = project_root / "Knowledge" / "内容营销数据库"
        else:
            self.content_db_dir = Path(content_db_dir)
        
        self.content_db_dir.mkdir(parents=True, exist_ok=True)
        
        # 内容类型定义
        self.content_types = {
            'whitepaper': {
                'keywords': ['whitepaper', 'white-paper', 'white_paper', 'wp-', '/wp/'],
                'patterns': [r'/whitepaper[s]?/', r'/white-paper[s]?/', r'/wp/'],
                'description': '白皮书 - 深度技术或行业分析文档'
            },
            'case_study': {
                'keywords': ['case-study', 'case_study', 'casestudy', 'customer-story', 'success-story'],
                'patterns': [r'/case-study[s]?/', r'/customer-story[s]?/', r'/success-story[s]?/'],
                'description': '案例研究 - 客户成功故事'
            },
            'webinar': {
                'keywords': ['webinar', 'webinars', 'on-demand', 'on_demand'],
                'patterns': [r'/webinar[s]?/', r'/on-demand/'],
                'description': '网络研讨会 - 在线演示和培训'
            },
            'blog': {
                'keywords': ['blog', 'blogs', 'article', 'articles', 'post', 'posts'],
                'patterns': [r'/blog[s]?/', r'/article[s]?/', r'/post[s]?/'],
                'description': '博客文章 - 定期发布的内容'
            },
            'ebook': {
                'keywords': ['ebook', 'e-book', 'e_book', 'guide', 'guides'],
                'patterns': [r'/ebook[s]?/', r'/e-book[s]?/', r'/guide[s]?/'],
                'description': '电子书 - 长篇指南类内容'
            },
            'datasheet': {
                'keywords': ['datasheet', 'data-sheet', 'data_sheet', 'specification', 'spec'],
                'patterns': [r'/datasheet[s]?/', r'/data-sheet[s]?/', r'/spec[s]?/'],
                'description': '数据表 - 产品规格文档'
            },
            'video': {
                'keywords': ['video', 'videos', 'watch', 'youtube'],
                'patterns': [r'/video[s]?/', r'/watch/'],
                'description': '视频内容'
            },
            'podcast': {
                'keywords': ['podcast', 'podcasts'],
                'patterns': [r'/podcast[s]?/'],
                'description': '播客'
            },
            'infographic': {
                'keywords': ['infographic', 'infographics'],
                'patterns': [r'/infographic[s]?/'],
                'description': '信息图'
            },
            'report': {
                'keywords': ['report', 'reports', 'research', 'study', 'analysis'],
                'patterns': [r'/report[s]?/', r'/research/', r'/study/'],
                'description': '研究报告'
            },
        }
        
        # 请求配置
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.request_delay = 1  # 请求延迟（秒）
    
    def detect_content_type(self, url: str) -> List[str]:
        """检测内容类型"""
        if pd.isna(url) or not isinstance(url, str):
            return []
        
        url_lower = url.lower()
        detected_types = []
        
        for content_type, config in self.content_types.items():
            # 检查关键词
            for keyword in config['keywords']:
                if keyword in url_lower:
                    detected_types.append(content_type)
                    break
            
            # 检查模式
            if content_type not in detected_types:
                for pattern in config['patterns']:
                    if re.search(pattern, url_lower):
                        detected_types.append(content_type)
                        break
        
        return detected_types if detected_types else ['other']
    
    def extract_content_metadata(self, url: str, fetch_content: bool = False) -> Dict:
        """提取内容元数据"""
        parsed = urlparse(url)
        path_segments = [seg for seg in parsed.path.split('/') if seg]
        
        metadata = {
            'url': url,
            'domain': parsed.netloc,
            'path_segments': path_segments,
            'depth': len(path_segments),
            'content_types': self.detect_content_type(url),
            'category': path_segments[0] if path_segments else None,
            'subcategory': path_segments[1] if len(path_segments) > 1 else None,
            'material_name': path_segments[-1] if path_segments else None,
            'url_hash': hashlib.md5(url.encode()).hexdigest()[:16],
        }
        
        # 如果启用内容爬取
        if fetch_content:
            try:
                content_data = self.fetch_page_content(url)
                metadata.update(content_data)
            except Exception as e:
                metadata['fetch_error'] = str(e)
        
        return metadata
    
    def fetch_page_content(self, url: str) -> Dict:
        """爬取页面内容"""
        time.sleep(self.request_delay)  # 避免请求过快
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取标题
            title = None
            if soup.title:
                title = soup.title.string.strip() if soup.title.string else None
            
            # 提取meta描述
            meta_desc = None
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag and meta_tag.get('content'):
                meta_desc = meta_tag.get('content').strip()
            
            # 提取h1标题
            h1 = None
            h1_tag = soup.find('h1')
            if h1_tag:
                h1 = h1_tag.get_text(strip=True)
            
            # 提取正文（前500字符）
            body_text = None
            body = soup.find('body')
            if body:
                # 移除script和style标签
                for script in body(["script", "style"]):
                    script.decompose()
                body_text = body.get_text(separator=' ', strip=True)[:500]
            
            # 提取结构化数据（JSON-LD）
            structured_data = []
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    data = json.loads(script.string)
                    structured_data.append(data)
                except:
                    pass
            
            return {
                'title': title,
                'meta_description': meta_desc,
                'h1': h1,
                'body_preview': body_text,
                'structured_data': json.dumps(structured_data) if structured_data else None,
                'word_count': len(body_text.split()) if body_text else 0,
                'fetch_status': 'success'
            }
        
        except requests.exceptions.RequestException as e:
            return {
                'fetch_status': 'error',
                'fetch_error': str(e)
            }
        except Exception as e:
            return {
                'fetch_status': 'error',
                'fetch_error': str(e)
            }
    
    def analyze_content_structure(self, company_name: str, content_type: str = None, 
                                  limit: int = None, fetch_content: bool = False) -> List[Dict]:
        """分析公司内容结构"""
        print(f"分析: {company_name}" + (f" - {content_type}" if content_type else ""))
        
        csv_file = self.output_data_dir / f"{company_name}_analyzed.csv"
        if not csv_file.exists():
            print(f"  ❌ 文件不存在: {csv_file}")
            return []
        
        df = pd.read_csv(csv_file)
        
        # 如果指定了内容类型，进行过滤
        if content_type:
            # 检查URL中是否包含该内容类型
            mask = df['url'].str.contains(content_type, case=False, na=False)
            df = df[mask]
        
        # 限制数量
        if limit:
            df = df.head(limit)
        
        content_list = []
        
        for idx, row in df.iterrows():
            url = row.get('url', '')
            if pd.isna(url):
                continue
            
            metadata = self.extract_content_metadata(url, fetch_content=fetch_content)
            metadata['company'] = company_name
            metadata['original_content_type'] = row.get('content_type', 'other')
            metadata['year'] = row.get('year', '')
            metadata['month'] = row.get('month', '')
            
            content_list.append(metadata)
            
            if (idx + 1) % 50 == 0:
                print(f"  已处理: {idx + 1}/{len(df)}")
        
        print(f"  ✅ 完成: {len(content_list)} 个内容")
        return content_list
    
    def build_content_database(self, companies: List[str] = None, 
                              content_types: List[str] = None,
                              fetch_content: bool = False,
                              limit_per_company: int = None) -> pd.DataFrame:
        """构建内容营销数据库"""
        print("=" * 80)
        print("构建内容营销数据库")
        print("=" * 80)
        print()
        
        if companies is None:
            csv_files = sorted(self.output_data_dir.glob("*_analyzed.csv"))
            companies = [f.stem.replace('_analyzed', '') for f in csv_files]
        
        all_content_data = []
        
        for company in companies:
            if content_types:
                # 为每种内容类型分别分析
                for ct in content_types:
                    content_list = self.analyze_content_structure(
                        company, content_type=ct, 
                        limit=limit_per_company,
                        fetch_content=fetch_content
                    )
                    all_content_data.extend(content_list)
            else:
                # 分析所有内容
                content_list = self.analyze_content_structure(
                    company, 
                    limit=limit_per_company,
                    fetch_content=fetch_content
                )
                all_content_data.extend(content_list)
        
        df = pd.DataFrame(all_content_data)
        
        # 确保content_types是字符串格式（用于CSV）
        if 'content_types' in df.columns:
            df['content_types'] = df['content_types'].apply(
                lambda x: ','.join(x) if isinstance(x, list) else str(x) if pd.notna(x) else ''
            )
        
        # 保存数据库
        db_file = self.content_db_dir / "content_database.csv"
        df.to_csv(db_file, index=False, encoding='utf-8')
        print(f"\n✅ 内容数据库已保存: {db_file}")
        print(f"   总记录数: {len(df):,}")
        
        # 保存JSON格式（便于程序访问）
        json_file = self.content_db_dir / "content_database.json"
        df.to_json(json_file, orient='records', force_ascii=False, indent=2)
        print(f"✅ JSON格式已保存: {json_file}")
        
        return df
    
    def analyze_content_patterns(self, df: pd.DataFrame) -> Dict:
        """分析内容模式"""
        print("\n" + "=" * 80)
        print("分析内容模式")
        print("=" * 80)
        print()
        
        patterns = {
            'naming_conventions': defaultdict(Counter),
            'category_structures': defaultdict(Counter),
            'content_type_distribution': Counter(),
            'url_patterns': defaultdict(list),
        }
        
        for _, row in df.iterrows():
            company = row.get('company', 'unknown')
            content_types = row.get('content_types', [])
            if isinstance(content_types, str):
                content_types = [ct.strip() for ct in content_types.split(',')]
            
            # 内容类型分布
            for ct in content_types:
                patterns['content_type_distribution'][ct] += 1
            
            # 命名约定
            material_name = row.get('material_name', '')
            if material_name:
                if '-' in material_name:
                    patterns['naming_conventions'][company]['kebab-case'] += 1
                elif '_' in material_name:
                    patterns['naming_conventions'][company]['snake_case'] += 1
                else:
                    patterns['naming_conventions'][company]['lowercase'] += 1
            
            # 分类结构
            category = row.get('category', '')
            subcategory = row.get('subcategory', '')
            if category:
                structure = f"{category}/{subcategory}" if subcategory else category
                patterns['category_structures'][company][structure] += 1
        
        return patterns
    
    def generate_content_templates(self, df: pd.DataFrame) -> Dict:
        """生成内容模板"""
        print("\n" + "=" * 80)
        print("生成内容模板")
        print("=" * 80)
        print()
        
        templates = {}
        
        # 按内容类型分组
        for content_type in self.content_types.keys():
            type_df = df[df['content_types'].str.contains(content_type, case=False, na=False)]
            
            if len(type_df) == 0:
                continue
            
            print(f"分析 {content_type}: {len(type_df)} 个样本")
            
            template = {
                'content_type': content_type,
                'description': self.content_types[content_type]['description'],
                'sample_count': len(type_df),
                'url_patterns': [],
                'category_patterns': [],
                'naming_patterns': [],
                'examples': [],
            }
            
            # URL模式
            for url in type_df['url'].head(20):
                template['url_patterns'].append(url)
            
            # 分类模式
            category_counts = type_df['category'].value_counts()
            template['category_patterns'] = category_counts.head(10).to_dict()
            
            # 命名模式
            naming_examples = type_df['material_name'].dropna().head(20).tolist()
            template['naming_patterns'] = naming_examples
            
            # 示例（如果有标题）
            if 'title' in type_df.columns:
                examples = type_df[['url', 'title', 'h1']].head(10).to_dict('records')
                template['examples'] = examples
            
            templates[content_type] = template
        
        # 保存模板
        template_file = self.content_db_dir / "content_templates.json"
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 内容模板已保存: {template_file}")
        
        return templates
    
    def generate_analysis_report(self, df: pd.DataFrame, patterns: Dict, templates: Dict) -> str:
        """生成分析报告"""
        report_file = self.content_db_dir / "内容营销深度分析报告.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 竞品内容营销深度分析报告\n\n")
            f.write("=" * 80 + "\n\n")
            
            # 总体统计
            f.write("## 总体统计\n\n")
            f.write(f"- **总内容数**: {len(df):,}\n")
            f.write(f"- **公司数**: {len(df['company'].unique())}\n")
            f.write(f"- **内容类型数**: {len(patterns['content_type_distribution'])}\n\n")
            
            # 内容类型分布
            f.write("## 内容类型分布\n\n")
            for ct, count in patterns['content_type_distribution'].most_common():
                f.write(f"- **{ct}**: {count:,} 个\n")
            f.write("\n")
            
            # 按公司分析
            f.write("## 按公司分析\n\n")
            for company in sorted(df['company'].unique()):
                company_df = df[df['company'] == company]
                f.write(f"### {company}\n\n")
                f.write(f"- **总内容数**: {len(company_df):,}\n")
                
                # 内容类型分布
                content_types = []
                for idx, row in company_df.iterrows():
                    types_str = row.get('content_types', '')
                    if pd.notna(types_str) and types_str != '':
                        if isinstance(types_str, list):
                            content_types.extend([str(ct).strip() for ct in types_str if ct])
                        else:
                            content_types.extend([ct.strip() for ct in str(types_str).split(',') if ct.strip()])
                
                type_counts = Counter(content_types)
                f.write("\n**内容类型分布**:\n\n")
                for ct, count in type_counts.most_common(10):
                    f.write(f"- {ct}: {count}\n")
                
                f.write("\n")
            
            # 内容模板
            f.write("## 内容模板库\n\n")
            for content_type, template in templates.items():
                f.write(f"### {content_type}\n\n")
                f.write(f"**描述**: {template['description']}\n\n")
                f.write(f"**样本数**: {template['sample_count']}\n\n")
                
                if template['category_patterns']:
                    f.write("**分类模式**:\n\n")
                    for category, count in list(template['category_patterns'].items())[:5]:
                        f.write(f"- {category}: {count}\n")
                    f.write("\n")
                
                if template['naming_patterns']:
                    f.write("**命名模式示例**:\n\n")
                    for name in template['naming_patterns'][:10]:
                        f.write(f"- `{name}`\n")
                    f.write("\n")
            
            f.write("\n" + "=" * 80 + "\n")
        
        print(f"✅ 分析报告已保存: {report_file}")
        return str(report_file)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='构建内容营销数据库')
    parser.add_argument('--content-types', nargs='+', 
                       help='指定要分析的内容类型（如: whitepaper case_study）')
    parser.add_argument('--companies', nargs='+',
                       help='指定要分析的公司')
    parser.add_argument('--fetch', action='store_true',
                       help='是否爬取实际内容（标题、描述等）')
    parser.add_argument('--limit', type=int,
                       help='每个公司/内容类型的限制数量')
    
    args = parser.parse_args()
    
    builder = ContentDatabaseBuilder()
    
    # 构建数据库
    df = builder.build_content_database(
        companies=args.companies,
        content_types=args.content_types,
        fetch_content=args.fetch,
        limit_per_company=args.limit
    )
    
    # 分析模式
    patterns = builder.analyze_content_patterns(df)
    
    # 生成模板
    templates = builder.generate_content_templates(df)
    
    # 生成报告
    builder.generate_analysis_report(df, patterns, templates)
    
    print("\n" + "=" * 80)
    print("✅ 内容营销数据库构建完成！")
    print("=" * 80)
    print(f"\n📁 数据库位置: {builder.content_db_dir}")
    print(f"   - content_database.csv")
    print(f"   - content_database.json")
    print(f"   - content_templates.json")
    print(f"   - 内容营销深度分析报告.md")


if __name__ == "__main__":
    main()

