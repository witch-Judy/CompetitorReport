#!/usr/bin/env python3
"""
提取所有公司的H1标签数据
"""

import re
import pandas as pd
from pathlib import Path
from typing import Dict, List
from collections import defaultdict


class H1Extractor:
    """H1标签提取器"""
    
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
    
    def extract_h1_from_xml(self, xml_file: Path) -> List[Dict]:
        """从XML文件中提取H1标签"""
        h1_data = []
        
        if not xml_file.exists():
            return h1_data
        
        try:
            content = xml_file.read_text(encoding='utf-8', errors='ignore')
            
            # 查找所有H1标签（包括各种变体）
            h1_pattern = r'<h1[^>]*>(.*?)</h1>'
            h1_matches = re.findall(h1_pattern, content, re.IGNORECASE | re.DOTALL)
            
            for h1_content in h1_matches:
                # 清理HTML标签，只保留文本
                clean_text = re.sub(r'<[^>]+>', '', h1_content).strip()
                # 移除多余的空白字符
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                
                if clean_text:
                    h1_data.append({
                        'h1_text': clean_text,
                        'h1_html': h1_content.strip()
                    })
        
        except Exception as e:
            print(f"Error processing {xml_file}: {e}")
        
        return h1_data
    
    def extract_company_h1(self, company_key: str) -> pd.DataFrame:
        """提取单个公司的H1数据"""
        company_name = self.company_names.get(company_key, company_key)
        
        # 查找XML文件
        xml_file = self.raw_data_dir / company_key / f"{company_key}.xml"
        
        # 如果不存在，尝试其他可能的文件名
        if not xml_file.exists():
            # 尝试查找该目录下的所有XML文件
            company_dir = self.raw_data_dir / company_key
            if company_dir.exists():
                xml_files = list(company_dir.glob("*.xml"))
                if xml_files:
                    xml_file = xml_files[0]
        
        if not xml_file.exists():
            print(f"Warning: No XML file found for {company_name}")
            return pd.DataFrame()
        
        # 提取H1数据
        h1_data = self.extract_h1_from_xml(xml_file)
        
        if not h1_data:
            print(f"Warning: No H1 tags found for {company_name}")
            return pd.DataFrame()
        
        # 创建DataFrame
        df = pd.DataFrame(h1_data)
        df['company'] = company_name
        df['company_key'] = company_key
        
        # 添加统计信息
        df['h1_length'] = df['h1_text'].str.len()
        df['word_count'] = df['h1_text'].str.split().str.len()
        
        return df
    
    def extract_all_companies(self):
        """提取所有公司的H1数据"""
        all_h1_data = []
        
        for company_key in self.companies:
            print(f"Processing {company_key}...")
            df = self.extract_company_h1(company_key)
            
            if not df.empty:
                # 保存单个公司的H1数据
                output_file = self.h1_output_dir / f"{self.company_names[company_key]}_H1.csv"
                df.to_csv(output_file, index=False, encoding='utf-8-sig')
                print(f"  ✅ Saved {len(df)} H1 tags to {output_file.name}")
                
                all_h1_data.append(df)
            else:
                print(f"  ⚠️  No H1 data found for {company_key}")
        
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
            "\n---\n",
            "## 各公司H1标签统计\n",
            "| 公司 | H1数量 | 平均字符数 | 平均词数 |\n",
            "|------|--------|-----------|---------|\n"
        ]
        
        # 按公司统计
        company_stats = df.groupby('company').agg({
            'h1_text': 'count',
            'h1_length': 'mean',
            'word_count': 'mean'
        }).round(1)
        
        company_stats.columns = ['H1数量', '平均字符数', '平均词数']
        company_stats = company_stats.sort_values('H1数量', ascending=False)
        
        for company, stats in company_stats.iterrows():
            report_lines.append(
                f"| {company} | {int(stats['H1数量'])} | {stats['平均字符数']:.1f} | {stats['平均词数']:.1f} |\n"
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
    extractor = H1Extractor()
    extractor.extract_all_companies()
    print("\n✅ H1 extraction completed!")


if __name__ == "__main__":
    main()


