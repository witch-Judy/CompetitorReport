#!/usr/bin/env python3
"""
从URL列表中提取H1标签数据
需要访问实际网页来获取H1内容
"""

import re
import pandas as pd
import requests
from pathlib import Path
from typing import Dict, List
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse


class H1ExtractorFromURLs:
    """从URL列表中提取H1标签"""
    
    def __init__(self):
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        
        self.raw_data_dir = project_root / "raw_data"
        self.output_data_dir = project_root / "output_data"
        self.h1_output_dir = self.output_data_dir / "H1"
        self.h1_output_dir.mkdir(parents=True, exist_ok=True)
        
        # 18个公司列表
        self.companies = [
            'abb', 'aveva', 'bosch', 'cognite', 'emerson', 'ge', 'hitachi',
            'hivemq', 'honeywell', 'ignition', 'rockwell-automation',
            'schneider-electric', 'siemens', 'tulip', 'yokogawa', 'c3-ai',
            'umh', 'univers'
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
            'c3-ai': 'C3 AI',
            'umh': 'UMH',
            'univers': 'Univers'
        }
        
        # 请求设置
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 10
        self.request_delay = 0.5  # 请求间隔，避免过快
    
    def extract_urls_from_xml(self, xml_file: Path) -> List[str]:
        """从XML文件中提取URL列表"""
        urls = []
        
        if not xml_file.exists():
            return urls
        
        try:
            content = xml_file.read_text(encoding='utf-8', errors='ignore')
            # 提取所有<loc>标签中的URL
            url_pattern = r'<loc>(.*?)</loc>'
            urls = re.findall(url_pattern, content, re.IGNORECASE)
        except Exception as e:
            print(f"Error reading XML file {xml_file}: {e}")
        
        return urls
    
    def fetch_h1_from_url(self, url: str) -> Dict:
        """从单个URL获取H1标签"""
        try:
            time.sleep(self.request_delay)
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取H1标签
            h1_tags = soup.find_all('h1')
            h1_texts = []
            
            for h1 in h1_tags:
                text = h1.get_text(strip=True)
                if text:
                    h1_texts.append(text)
            
            return {
                'url': url,
                'h1_count': len(h1_texts),
                'h1_texts': h1_texts,
                'h1_text': h1_texts[0] if h1_texts else None,  # 第一个H1
                'status': 'success'
            }
        
        except requests.exceptions.Timeout:
            return {'url': url, 'status': 'timeout', 'h1_count': 0, 'h1_texts': []}
        except requests.exceptions.RequestException as e:
            return {'url': url, 'status': f'error: {str(e)[:50]}', 'h1_count': 0, 'h1_texts': []}
        except Exception as e:
            return {'url': url, 'status': f'error: {str(e)[:50]}', 'h1_count': 0, 'h1_texts': []}
    
    def extract_company_h1(self, company_key: str, max_urls: int = 100) -> pd.DataFrame:
        """提取单个公司的H1数据"""
        company_name = self.company_names.get(company_key, company_key)
        
        # 查找XML文件
        xml_file = self.raw_data_dir / company_key / f"{company_key}.xml"
        
        # 如果不存在，尝试其他可能的文件名
        if not xml_file.exists():
            company_dir = self.raw_data_dir / company_key
            if company_dir.exists():
                xml_files = list(company_dir.glob("*.xml"))
                if xml_files:
                    xml_file = xml_files[0]
        
        if not xml_file.exists():
            print(f"Warning: No XML file found for {company_name}")
            return pd.DataFrame()
        
        # 提取URL列表
        urls = self.extract_urls_from_xml(xml_file)
        print(f"Found {len(urls)} URLs for {company_name}")
        
        if not urls:
            return pd.DataFrame()
        
        # 限制处理的URL数量（避免过多请求）
        urls_to_process = urls[:max_urls]
        print(f"Processing first {len(urls_to_process)} URLs...")
        
        # 提取H1数据
        h1_data = []
        for i, url in enumerate(urls_to_process, 1):
            if i % 10 == 0:
                print(f"  Processed {i}/{len(urls_to_process)} URLs...")
            
            result = self.fetch_h1_from_url(url)
            if result['h1_count'] > 0:
                h1_data.append(result)
        
        if not h1_data:
            print(f"Warning: No H1 tags found for {company_name}")
            return pd.DataFrame()
        
        # 创建DataFrame
        rows = []
        for item in h1_data:
            for h1_text in item['h1_texts']:
                rows.append({
                    'company': company_name,
                    'company_key': company_key,
                    'url': item['url'],
                    'h1_text': h1_text,
                    'h1_length': len(h1_text),
                    'word_count': len(h1_text.split())
                })
        
        df = pd.DataFrame(rows)
        return df
    
    def extract_all_companies(self, max_urls_per_company: int = 100):
        """提取所有公司的H1数据"""
        all_h1_data = []
        
        for company_key in self.companies:
            print(f"\n{'='*60}")
            print(f"Processing {company_key}...")
            print(f"{'='*60}")
            
            df = self.extract_company_h1(company_key, max_urls=max_urls_per_company)
            
            if not df.empty:
                # 保存单个公司的H1数据
                output_file = self.h1_output_dir / f"{self.company_names[company_key]}_H1.csv"
                df.to_csv(output_file, index=False, encoding='utf-8-sig')
                print(f"✅ Saved {len(df)} H1 tags to {output_file.name}")
                
                all_h1_data.append(df)
            else:
                print(f"⚠️  No H1 data found for {company_key}")
        
        # 合并所有公司的数据
        if all_h1_data:
            combined_df = pd.concat(all_h1_data, ignore_index=True)
            combined_file = self.h1_output_dir / "All_Companies_H1.csv"
            combined_df.to_csv(combined_file, index=False, encoding='utf-8-sig')
            print(f"\n✅ Saved combined H1 data ({len(combined_df)} total H1 tags) to {combined_file.name}")
            
            # 生成统计报告
            self.generate_summary_report(combined_df)
        else:
            print("\n⚠️  No H1 data found for any company")
    
    def generate_summary_report(self, df: pd.DataFrame):
        """生成H1数据统计报告"""
        report_file = self.h1_output_dir / "H1_统计报告.md"
        
        report_lines = [
            "# H1标签统计报告\n",
            f"**生成日期**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**总H1标签数**: {len(df)}\n",
            f"**总URL数**: {df['url'].nunique()}\n",
            "\n---\n",
            "## 各公司H1标签统计\n",
            "| 公司 | H1数量 | URL数量 | 平均字符数 | 平均词数 |\n",
            "|------|--------|--------|-----------|---------|\n"
        ]
        
        # 按公司统计
        company_stats = df.groupby('company').agg({
            'h1_text': 'count',
            'url': 'nunique',
            'h1_length': 'mean',
            'word_count': 'mean'
        }).round(1)
        
        company_stats.columns = ['H1数量', 'URL数量', '平均字符数', '平均词数']
        company_stats = company_stats.sort_values('H1数量', ascending=False)
        
        for company, stats in company_stats.iterrows():
            report_lines.append(
                f"| {company} | {int(stats['H1数量'])} | {int(stats['URL数量'])} | {stats['平均字符数']:.1f} | {stats['平均词数']:.1f} |\n"
            )
        
        # 添加Top 20 H1标签
        report_lines.extend([
            "\n---\n",
            "## Top 20 H1标签（按出现频率）\n",
            "\n| 排名 | H1文本 | 出现次数 |\n",
            "|------|--------|---------|\n"
        ])
        
        h1_counts = df['h1_text'].value_counts().head(20)
        for rank, (h1_text, count) in enumerate(h1_counts.items(), 1):
            # 截断过长的文本
            display_text = h1_text[:80] + "..." if len(h1_text) > 80 else h1_text
            report_lines.append(f"| {rank} | {display_text} | {count} |\n")
        
        # 写入报告
        report_file.write_text(''.join(report_lines), encoding='utf-8')
        print(f"✅ Generated summary report: {report_file.name}")


def main():
    print("="*80)
    print("H1标签提取工具")
    print("="*80)
    print("\n注意：此工具需要访问实际网页来提取H1标签")
    print("处理时间取决于URL数量和网络速度")
    print("默认每个公司处理前100个URL\n")
    
    extractor = H1ExtractorFromURLs()
    
    # 可以调整每个公司处理的URL数量
    max_urls = 100  # 可以根据需要调整
    
    extractor.extract_all_companies(max_urls_per_company=max_urls)
    print("\n✅ H1 extraction completed!")


if __name__ == "__main__":
    main()


