#!/usr/bin/env python3
"""
Siemens 内容深度分析器
深入分析每篇内容的：
1. 内容架构（标题、段落、格式等）
2. 写作原因（SEO、用户体验、营销目标等）
3. 内容模式（结构、风格、策略等）
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter
from urllib.parse import urlparse
import hashlib


class SiemensContentDeepAnalyzer:
    """Siemens内容深度分析器"""
    
    def __init__(self):
        """初始化分析器"""
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        
        self.output_data_dir = project_root / "output_data"
        self.knowledge_dir = project_root / "Knowledge"
        self.siemens_dir = self.knowledge_dir / "Siemens内容营销策略研究"
        self.content_analysis_dir = self.siemens_dir / "内容深度分析"
        self.content_analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        (self.content_analysis_dir / "原始内容").mkdir(exist_ok=True)
        (self.content_analysis_dir / "内容架构").mkdir(exist_ok=True)
        (self.content_analysis_dir / "写作模式").mkdir(exist_ok=True)
        
        # 请求配置
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.request_delay = 2  # 请求延迟（秒）
        self.timeout = 15
        
        # PDF下载目录
        self.pdf_dir = self.content_analysis_dir / "PDF内容"
        self.pdf_dir.mkdir(exist_ok=True)
    
    def _fetch_pdf(self, url: str) -> Dict:
        """处理PDF文件"""
        try:
            response = self.session.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            # 保存PDF
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            pdf_filename = url.split('/')[-1] or f"{url_hash}.pdf"
            # 清理文件名
            pdf_filename = re.sub(r'[^\w\-_\.]', '_', pdf_filename)
            pdf_path = self.pdf_dir / pdf_filename
            
            with open(pdf_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return {
                'url': url,
                'content_type': 'pdf',
                'pdf_path': str(pdf_path),
                'pdf_filename': pdf_filename,
                'file_size': pdf_path.stat().st_size,
                'fetch_status': 'success',
                'fetch_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'note': 'PDF文件已下载，需要专门的PDF解析工具提取文本内容'
            }
        
        except Exception as e:
            return {
                'url': url,
                'fetch_status': 'error',
                'error': str(e)
            }
    
    def fetch_content(self, url: str) -> Dict:
        """爬取内容"""
        time.sleep(self.request_delay)
        
        # 检查是否是PDF
        if url.lower().endswith('.pdf'):
            return self._fetch_pdf(url)
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # 检查Content-Type
            content_type = response.headers.get('Content-Type', '').lower()
            if 'pdf' in content_type:
                return self._fetch_pdf(url)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取标题
            title = None
            if soup.title:
                title = soup.title.string.strip() if soup.title.string else None
            
            # 提取H1
            h1 = None
            h1_tag = soup.find('h1')
            if h1_tag:
                h1 = h1_tag.get_text(strip=True)
            
            # 提取所有标题（H1-H6）
            headings = []
            for level in range(1, 7):
                for tag in soup.find_all(f'h{level}'):
                    text = tag.get_text(strip=True)
                    if text:
                        headings.append({
                            'level': level,
                            'text': text,
                            'tag': f'h{level}'
                        })
            
            # 提取正文段落
            paragraphs = []
            # 尝试多个可能的正文容器
            body_selectors = [
                'main article',
                'article',
                'main',
                '.content',
                '.article-content',
                '#content',
                '.post-content',
                '.entry-content',
                '.text-content',
                '.body-content',
                '[role="main"]',
                '.main-content'
            ]
            
            body_content = None
            for selector in body_selectors:
                try:
                    body_content = soup.select_one(selector)
                    if body_content:
                        break
                except:
                    continue
            
            if not body_content:
                body_content = soup.find('body')
            
            if body_content:
                # 移除script和style
                for script in body_content(["script", "style", "nav", "footer", "header", "aside"]):
                    script.decompose()
                
                # 提取段落
                for p in body_content.find_all('p'):
                    text = p.get_text(strip=True)
                    if text and len(text) > 20:  # 过滤太短的段落
                        paragraphs.append(text)
                
                # 如果没有段落，尝试提取div中的文本
                if not paragraphs:
                    for div in body_content.find_all('div', class_=re.compile(r'content|text|body|article', re.I)):
                        text = div.get_text(strip=True)
                        # 过滤太短或太长的文本
                        if 50 <= len(text) <= 5000:
                            paragraphs.append(text)
                
                # 如果还是没有，提取所有文本
                if not paragraphs:
                    full_text = body_content.get_text(separator='\n', strip=True)
                    # 按换行分割，过滤短行
                    lines = [line.strip() for line in full_text.split('\n') if len(line.strip()) > 50]
                    paragraphs = lines[:50]  # 限制数量
                
                # 如果段落还是太少，尝试提取所有div中的文本
                if len(paragraphs) < 3:
                    for div in body_content.find_all('div'):
                        # 跳过导航、页脚等
                        if any(skip in str(div.get('class', [])).lower() for skip in ['nav', 'footer', 'header', 'menu', 'sidebar']):
                            continue
                        text = div.get_text(strip=True)
                        if 100 <= len(text) <= 2000:  # 合理长度的文本
                            paragraphs.append(text)
                            if len(paragraphs) >= 20:
                                break
            
            # 提取列表
            lists = []
            for ul in body_content.find_all(['ul', 'ol']) if body_content else []:
                items = [li.get_text(strip=True) for li in ul.find_all('li')]
                if items:
                    lists.append({
                        'type': ul.name,
                        'items': items
                    })
            
            # 提取图片
            images = []
            for img in soup.find_all('img'):
                src = img.get('src') or img.get('data-src')
                alt = img.get('alt', '')
                if src:
                    images.append({
                        'src': src,
                        'alt': alt
                    })
            
            # 提取链接
            links = []
            for a in soup.find_all('a', href=True):
                href = a.get('href')
                text = a.get_text(strip=True)
                if href and text:
                    links.append({
                        'href': href,
                        'text': text[:100]  # 限制长度
                    })
            
            # 提取Meta信息
            meta_desc = None
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag and meta_tag.get('content'):
                meta_desc = meta_tag.get('content').strip()
            
            meta_keywords = None
            meta_kw = soup.find('meta', attrs={'name': 'keywords'})
            if meta_kw and meta_kw.get('content'):
                meta_keywords = meta_kw.get('content').strip()
            
            # 提取结构化数据
            structured_data = []
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    data = json.loads(script.string)
                    structured_data.append(data)
                except:
                    pass
            
            # 计算内容统计
            full_text = ' '.join(paragraphs)
            word_count = len(full_text.split())
            char_count = len(full_text)
            
            return {
                'url': url,
                'title': title,
                'h1': h1,
                'meta_description': meta_desc,
                'meta_keywords': meta_keywords,
                'headings': headings,
                'paragraphs': paragraphs,
                'lists': lists,
                'images': images,
                'links': links,
                'structured_data': structured_data,
                'word_count': word_count,
                'char_count': char_count,
                'paragraph_count': len(paragraphs),
                'heading_count': len(headings),
                'image_count': len(images),
                'link_count': len(links),
                'fetch_status': 'success',
                'fetch_time': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        
        except requests.exceptions.RequestException as e:
            return {
                'url': url,
                'fetch_status': 'error',
                'error': str(e)
            }
        except Exception as e:
            return {
                'url': url,
                'fetch_status': 'error',
                'error': str(e)
            }
    
    def analyze_content_structure(self, content_data: Dict) -> Dict:
        """分析内容架构"""
        if content_data.get('fetch_status') != 'success':
            return {}
        
        structure = {
            'title_structure': {},
            'heading_hierarchy': {},
            'content_organization': {},
            'formatting_patterns': {},
        }
        
        # 标题结构分析
        if content_data.get('title'):
            title = content_data['title']
            structure['title_structure'] = {
                'length': len(title),
                'word_count': len(title.split()),
                'has_separator': '|' in title or '-' in title or ':' in title,
                'format': self._detect_title_format(title)
            }
        
        # 标题层级分析
        headings = content_data.get('headings', [])
        if headings:
            heading_levels = Counter([h['level'] for h in headings])
            structure['heading_hierarchy'] = {
                'total_headings': len(headings),
                'level_distribution': dict(heading_levels),
                'max_depth': max([h['level'] for h in headings]) if headings else 0,
                'heading_sequence': [h['level'] for h in headings[:10]]  # 前10个标题的层级
            }
        
        # 内容组织分析
        paragraphs = content_data.get('paragraphs', [])
        if paragraphs:
            para_lengths = [len(p.split()) for p in paragraphs]
            structure['content_organization'] = {
                'paragraph_count': len(paragraphs),
                'avg_paragraph_length': sum(para_lengths) / len(para_lengths) if para_lengths else 0,
                'min_paragraph_length': min(para_lengths) if para_lengths else 0,
                'max_paragraph_length': max(para_lengths) if para_lengths else 0,
                'total_words': content_data.get('word_count', 0)
            }
        
        # 格式化模式
        structure['formatting_patterns'] = {
            'has_lists': len(content_data.get('lists', [])) > 0,
            'list_count': len(content_data.get('lists', [])),
            'has_images': len(content_data.get('images', [])) > 0,
            'image_count': len(content_data.get('images', [])),
            'has_links': len(content_data.get('links', [])) > 0,
            'link_count': len(content_data.get('links', []))
        }
        
        return structure
    
    def analyze_writing_reasons(self, content_data: Dict, structure: Dict) -> Dict:
        """分析写作原因"""
        reasons = {
            'seo_optimization': {},
            'user_experience': {},
            'marketing_goals': {},
            'content_strategy': {}
        }
        
        # SEO优化分析
        reasons['seo_optimization'] = {
            'has_meta_description': content_data.get('meta_description') is not None,
            'has_meta_keywords': content_data.get('meta_keywords') is not None,
            'title_optimized': self._check_seo_title(content_data.get('title', '')),
            'has_structured_data': len(content_data.get('structured_data', [])) > 0,
            'heading_structure': structure.get('heading_hierarchy', {}).get('max_depth', 0) > 0,
            'image_alt_tags': sum(1 for img in content_data.get('images', []) if img.get('alt'))
        }
        
        # 用户体验分析
        reasons['user_experience'] = {
            'readability': self._assess_readability(content_data),
            'scannability': self._assess_scannability(structure),
            'engagement_elements': {
                'has_images': len(content_data.get('images', [])) > 0,
                'has_lists': len(content_data.get('lists', [])) > 0,
                'has_headings': len(content_data.get('headings', [])) > 0
            }
        }
        
        # 营销目标分析
        reasons['marketing_goals'] = {
            'content_depth': self._assess_content_depth(content_data),
            'call_to_action': self._detect_cta(content_data),
            'social_sharing': self._detect_social_elements(content_data),
            'conversion_elements': self._detect_conversion_elements(content_data)
        }
        
        # 内容策略分析
        reasons['content_strategy'] = {
            'content_type': self._infer_content_type(content_data),
            'target_audience': self._infer_audience(content_data),
            'content_purpose': self._infer_purpose(content_data, structure)
        }
        
        return reasons
    
    def _detect_title_format(self, title: str) -> str:
        """检测标题格式"""
        if '|' in title:
            return 'pipe_separated'
        elif '-' in title:
            return 'dash_separated'
        elif ':' in title:
            return 'colon_separated'
        else:
            return 'simple'
    
    def _check_seo_title(self, title: str) -> bool:
        """检查标题SEO优化"""
        if not title:
            return False
        # 检查标题长度（50-60字符最佳）
        if 50 <= len(title) <= 60:
            return True
        # 检查是否包含关键词
        if len(title.split()) >= 3:
            return True
        return False
    
    def _assess_readability(self, content_data: Dict) -> Dict:
        """评估可读性"""
        paragraphs = content_data.get('paragraphs', [])
        if not paragraphs:
            return {'score': 0, 'factors': []}
        
        factors = []
        score = 0
        
        # 段落长度
        avg_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs)
        if 50 <= avg_length <= 200:
            score += 1
            factors.append('optimal_paragraph_length')
        
        # 标题使用
        if len(content_data.get('headings', [])) > 0:
            score += 1
            factors.append('has_headings')
        
        # 列表使用
        if len(content_data.get('lists', [])) > 0:
            score += 1
            factors.append('has_lists')
        
        return {'score': score, 'factors': factors}
    
    def _assess_scannability(self, structure: Dict) -> Dict:
        """评估可扫描性"""
        score = 0
        factors = []
        
        # 标题层级
        if structure.get('heading_hierarchy', {}).get('max_depth', 0) >= 2:
            score += 1
            factors.append('hierarchical_headings')
        
        # 列表
        if structure.get('formatting_patterns', {}).get('has_lists'):
            score += 1
            factors.append('has_lists')
        
        # 图片
        if structure.get('formatting_patterns', {}).get('has_images'):
            score += 1
            factors.append('has_images')
        
        return {'score': score, 'factors': factors}
    
    def _assess_content_depth(self, content_data: Dict) -> str:
        """评估内容深度"""
        word_count = content_data.get('word_count', 0)
        if word_count < 300:
            return 'shallow'
        elif word_count < 1000:
            return 'medium'
        else:
            return 'deep'
    
    def _detect_cta(self, content_data: Dict) -> List[str]:
        """检测行动号召"""
        cta_keywords = [
            'download', 'learn more', 'get started', 'contact us', 'request',
            'sign up', 'register', 'subscribe', 'buy now', 'try free',
            'download now', 'read more', 'view more', 'explore'
        ]
        
        paragraphs = ' '.join(content_data.get('paragraphs', []))
        links_text = ' '.join([link.get('text', '') for link in content_data.get('links', [])])
        full_text = (paragraphs + ' ' + links_text).lower()
        
        found_ctas = []
        for keyword in cta_keywords:
            if keyword in full_text:
                found_ctas.append(keyword)
        
        return found_ctas
    
    def _detect_social_elements(self, content_data: Dict) -> bool:
        """检测社交分享元素"""
        # 检查是否有社交分享按钮或链接
        # 这里简化处理，实际可以检查特定的class或id
        return False
    
    def _detect_conversion_elements(self, content_data: Dict) -> List[str]:
        """检测转化元素"""
        elements = []
        
        # 检查表单
        if 'form' in str(content_data.get('url', '')).lower():
            elements.append('form')
        
        # 检查下载链接
        links = content_data.get('links', [])
        for link in links:
            href = link.get('href', '').lower()
            if any(ext in href for ext in ['.pdf', '.doc', '.zip', 'download']):
                elements.append('download')
        
        return elements
    
    def _infer_content_type(self, content_data: Dict) -> str:
        """推断内容类型"""
        url = content_data.get('url', '').lower()
        title = (content_data.get('title', '') + ' ' + content_data.get('h1', '')).lower()
        
        if 'webinar' in url or 'webinar' in title:
            return 'webinar'
        elif 'case' in url or 'case' in title or 'customer' in url:
            return 'case_study'
        elif 'blog' in url or 'blog' in title:
            return 'blog'
        elif 'whitepaper' in url or 'white-paper' in url:
            return 'whitepaper'
        elif 'product' in url:
            return 'product'
        elif 'industry' in url:
            return 'industry'
        else:
            return 'other'
    
    def _infer_audience(self, content_data: Dict) -> str:
        """推断目标受众"""
        # 简化处理，可以根据关键词推断
        return 'general'
    
    def _infer_purpose(self, content_data: Dict, structure: Dict) -> str:
        """推断内容目的"""
        word_count = content_data.get('word_count', 0)
        has_cta = len(self._detect_cta(content_data)) > 0
        
        if word_count > 2000:
            return 'deep_education'
        elif has_cta:
            return 'conversion'
        elif word_count < 500:
            return 'awareness'
        else:
            return 'information'
    
    def analyze_content_batch(self, urls: List[str], content_type: str = None) -> List[Dict]:
        """批量分析内容"""
        print(f"开始分析 {len(urls)} 个URL...")
        print()
        
        results = []
        
        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] 分析: {url[:80]}...")
            
            # 爬取内容
            content_data = self.fetch_content(url)
            
            if content_data.get('fetch_status') == 'success':
                # 分析架构
                structure = self.analyze_content_structure(content_data)
                
                # 分析原因
                reasons = self.analyze_writing_reasons(content_data, structure)
                
                # 保存原始内容
                url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
                content_file = self.content_analysis_dir / "原始内容" / f"{url_hash}.json"
                with open(content_file, 'w', encoding='utf-8') as f:
                    json.dump(content_data, f, ensure_ascii=False, indent=2, default=str)
                
                # 组合分析结果
                analysis_result = {
                    'url': url,
                    'url_hash': url_hash,
                    'content_type': content_type or self._infer_content_type(content_data),
                    'content_data': {
                        'title': content_data.get('title'),
                        'h1': content_data.get('h1'),
                        'word_count': content_data.get('word_count'),
                        'paragraph_count': content_data.get('paragraph_count')
                    },
                    'structure': structure,
                    'reasons': reasons,
                    'analysis_time': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                results.append(analysis_result)
                print(f"  ✅ 成功: {content_data.get('word_count', 0)} 字, {content_data.get('paragraph_count', 0)} 段")
            else:
                print(f"  ❌ 失败: {content_data.get('error', 'Unknown error')}")
            
            print()
        
        return results
    
    def generate_analysis_report(self, results: List[Dict], content_type: str = None) -> str:
        """生成分析报告"""
        if content_type:
            report_file = self.content_analysis_dir / f"{content_type}_内容架构与原因分析.md"
        else:
            report_file = self.content_analysis_dir / "内容架构与原因分析.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Siemens 内容架构与写作原因分析报告\n\n")
            f.write("=" * 80 + "\n\n")
            if content_type:
                f.write(f"**内容类型**: {content_type}\n")
            f.write(f"**分析样本数**: {len(results)}\n")
            f.write(f"**分析时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("=" * 80 + "\n\n")
            
            # 总体统计
            f.write("## 总体统计\n\n")
            if results:
                avg_words = sum(r['content_data']['word_count'] for r in results if r['content_data']['word_count']) / len(results)
                avg_paragraphs = sum(r['content_data']['paragraph_count'] for r in results if r['content_data']['paragraph_count']) / len(results)
                f.write(f"- **平均字数**: {avg_words:.0f}\n")
                f.write(f"- **平均段落数**: {avg_paragraphs:.1f}\n")
            f.write("\n")
            
            # 内容架构分析
            f.write("## 内容架构分析\n\n")
            
            # 标题结构
            f.write("### 标题结构模式\n\n")
            title_formats = Counter()
            for result in results:
                fmt = result['structure'].get('title_structure', {}).get('format', 'unknown')
                title_formats[fmt] += 1
            
            for fmt, count in title_formats.most_common():
                f.write(f"- **{fmt}**: {count} 个\n")
            f.write("\n")
            
            # 标题层级
            f.write("### 标题层级结构\n\n")
            max_depths = [r['structure'].get('heading_hierarchy', {}).get('max_depth', 0) for r in results]
            if max_depths:
                avg_depth = sum(max_depths) / len(max_depths)
                f.write(f"- **平均标题深度**: {avg_depth:.1f} 层\n")
                f.write(f"- **最大标题深度**: {max(max_depths)} 层\n")
            f.write("\n")
            
            # 内容组织
            f.write("### 内容组织模式\n\n")
            if results:
                org_data = [r['structure'].get('content_organization', {}) for r in results]
                avg_para_length = sum(o.get('avg_paragraph_length', 0) for o in org_data) / len(org_data)
                f.write(f"- **平均段落长度**: {avg_para_length:.0f} 词\n")
            f.write("\n")
            
            # 写作原因分析
            f.write("## 写作原因分析\n\n")
            
            # SEO优化
            f.write("### SEO优化策略\n\n")
            seo_stats = {
                'has_meta_desc': sum(1 for r in results if r['reasons'].get('seo_optimization', {}).get('has_meta_description')),
                'has_structured_data': sum(1 for r in results if r['reasons'].get('seo_optimization', {}).get('has_structured_data')),
                'title_optimized': sum(1 for r in results if r['reasons'].get('seo_optimization', {}).get('title_optimized'))
            }
            f.write(f"- **有Meta描述**: {seo_stats['has_meta_desc']}/{len(results)} ({seo_stats['has_meta_desc']/len(results)*100:.1f}%)\n")
            f.write(f"- **有结构化数据**: {seo_stats['has_structured_data']}/{len(results)} ({seo_stats['has_structured_data']/len(results)*100:.1f}%)\n")
            f.write(f"- **标题优化**: {seo_stats['title_optimized']}/{len(results)} ({seo_stats['title_optimized']/len(results)*100:.1f}%)\n")
            f.write("\n")
            
            # 用户体验
            f.write("### 用户体验设计\n\n")
            readability_scores = [r['reasons'].get('user_experience', {}).get('readability', {}).get('score', 0) for r in results]
            if readability_scores:
                avg_readability = sum(readability_scores) / len(readability_scores)
                f.write(f"- **平均可读性得分**: {avg_readability:.1f}/3\n")
            f.write("\n")
            
            # 营销目标
            f.write("### 营销目标\n\n")
            cta_count = sum(len(r['reasons'].get('marketing_goals', {}).get('call_to_action', [])) for r in results)
            f.write(f"- **包含CTA的内容**: {cta_count}/{len(results)}\n")
            f.write("\n")
            
            # 详细分析
            f.write("## 详细内容分析\n\n")
            for i, result in enumerate(results, 1):
                f.write(f"### {i}. {result['content_data'].get('title', 'Untitled')}\n\n")
                f.write(f"**URL**: {result['url']}\n\n")
                f.write(f"**内容类型**: {result['content_type']}\n\n")
                f.write(f"**字数**: {result['content_data']['word_count']}\n")
                f.write(f"**段落数**: {result['content_data']['paragraph_count']}\n\n")
                
                # 架构
                f.write("**内容架构**:\n")
                structure = result['structure']
                if structure.get('heading_hierarchy'):
                    f.write(f"- 标题层级: {structure['heading_hierarchy'].get('max_depth', 0)} 层\n")
                if structure.get('content_organization'):
                    f.write(f"- 平均段落长度: {structure['content_organization'].get('avg_paragraph_length', 0):.0f} 词\n")
                f.write("\n")
                
                # 原因
                f.write("**写作原因**:\n")
                reasons = result['reasons']
                if reasons.get('seo_optimization', {}).get('has_meta_description'):
                    f.write("- SEO优化: 有Meta描述\n")
                if reasons.get('marketing_goals', {}).get('call_to_action'):
                    f.write(f"- 营销目标: 包含CTA ({', '.join(reasons['marketing_goals']['call_to_action'][:3])})\n")
                f.write("\n")
                f.write("---\n\n")
        
        print(f"✅ 分析报告已保存: {report_file}")
        return str(report_file)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Siemens内容深度分析')
    parser.add_argument('--content-type', type=str,
                       help='内容类型（如: webinar, industry, blog）')
    parser.add_argument('--limit', type=int, default=20,
                       help='分析数量限制')
    parser.add_argument('--urls', nargs='+',
                       help='指定URL列表')
    
    args = parser.parse_args()
    
    analyzer = SiemensContentDeepAnalyzer()
    
    # 加载数据
    df = pd.read_csv(analyzer.output_data_dir / "siemens_analyzed.csv")
    
    # 确定要分析的URL
    if args.urls:
        urls = args.urls
    elif args.content_type:
        # 按内容类型筛选
        type_df = df[df['content_type'] == args.content_type]
        urls = type_df['url'].head(args.limit).tolist()
    else:
        # 默认分析webinar
        type_df = df[df['content_type'] == 'webinar']
        urls = type_df['url'].head(args.limit).tolist()
        print("未指定内容类型，默认分析 webinar")
        print()
    
    if not urls:
        print("❌ 未找到要分析的URL")
        return
    
    # 执行分析
    results = analyzer.analyze_content_batch(urls, args.content_type)
    
    # 生成报告
    if results:
        analyzer.generate_analysis_report(results, args.content_type)
        
        # 保存JSON数据
        json_file = analyzer.content_analysis_dir / f"{args.content_type or 'all'}_analysis_data.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        print(f"✅ 分析数据已保存: {json_file}")
    
    print("\n" + "=" * 80)
    print("✅ Siemens 内容深度分析完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()

