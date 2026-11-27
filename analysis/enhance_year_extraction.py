#!/usr/bin/env python3
"""
增强年份提取功能
从URL路径、文件名等多个维度提取年份信息
"""

import pandas as pd
import re
import os
import sys
from pathlib import Path
from typing import Optional


class YearExtractor:
    """年份提取器"""
    
    def __init__(self):
        """初始化年份提取器"""
        # 年份模式：4位数字，范围2000-2099
        self.year_patterns = [
            r'/(20\d{2})/',           # URL路径中的年份: /2024/, /2025/
            r'/(20\d{2})-',           # URL路径中的年份: /2024-01/
            r'-(20\d{2})/',           # URL路径中的年份: -2024/
            r'/(20\d{2})$',           # URL路径末尾的年份: /2024
            r'^(20\d{2})/',           # URL路径开头的年份: 2024/
            r'/(20\d{2})',            # URL路径中的年份（通用）
            r'\b(20\d{2})\b',         # 任何位置的年份（单词边界）
        ]
    
    def extract_year_from_url(self, url: str) -> Optional[str]:
        """从URL中提取年份"""
        if pd.isna(url) or not isinstance(url, str):
            return None
        
        from datetime import datetime
        current_year = datetime.now().year
        
        for pattern in self.year_patterns:
            matches = re.findall(pattern, url)
            if matches:
                # 验证年份范围（2000-当前年份+1，允许未来一年）
                for year_str in matches:
                    try:
                        year = int(year_str)
                        # 只接受2000年到当前年份+1的范围（允许未来一年）
                        if 2000 <= year <= current_year + 1:
                            return str(year)
                    except:
                        continue
        
        return None
    
    def extract_year_from_filename(self, filename: str) -> Optional[str]:
        """从文件名中提取年份"""
        if pd.isna(filename) or not isinstance(filename, str):
            return None
        
        from datetime import datetime
        current_year = datetime.now().year
        
        # 查找4位数字年份
        matches = re.findall(r'\b(20\d{2})\b', str(filename))
        for year_str in matches:
            try:
                year = int(year_str)
                # 只接受2000年到当前年份+1的范围
                if 2000 <= year <= current_year + 1:
                    return str(year)
            except:
                continue
        
        return None
    
    def extract_year_from_path(self, path: str) -> Optional[str]:
        """从路径中提取年份"""
        if pd.isna(path) or not isinstance(path, str):
            return None
        
        from datetime import datetime
        current_year = datetime.now().year
        
        # 检查路径段中是否包含年份
        path_segments = path.split('/')
        for segment in path_segments:
            matches = re.findall(r'\b(20\d{2})\b', segment)
            for year_str in matches:
                try:
                    year = int(year_str)
                    # 只接受2000年到当前年份+1的范围
                    if 2000 <= year <= current_year + 1:
                        return str(year)
                except:
                    continue
        
        return None
    
    def enhance_year_data(self, csv_file: Path) -> pd.DataFrame:
        """增强CSV文件的年份数据"""
        print(f"处理: {csv_file.name}")
        
        df = pd.read_csv(csv_file)
        
        # 统计原始年份数据
        original_year_count = df['year'].notna().sum() if 'year' in df.columns else 0
        
        # 如果已经有year列，先检查缺失的
        if 'year' not in df.columns:
            df['year'] = None
        
        # 为缺失年份的行尝试提取
        missing_year_mask = df['year'].isna()
        enhanced_count = 0
        
        for idx in df[missing_year_mask].index:
            row = df.loc[idx]
            
            # 方法1: 从URL提取
            if 'url' in row:
                year = self.extract_year_from_url(str(row['url']))
                if year:
                    df.at[idx, 'year'] = year
                    enhanced_count += 1
                    continue
            
            # 方法2: 从path提取
            if 'path' in row:
                year = self.extract_year_from_path(str(row['path']))
                if year:
                    df.at[idx, 'year'] = year
                    enhanced_count += 1
                    continue
            
            # 方法3: 从filename提取
            if 'filename' in row:
                year = self.extract_year_from_filename(str(row['filename']))
                if year:
                    df.at[idx, 'year'] = year
                    enhanced_count += 1
                    continue
        
        final_year_count = df['year'].notna().sum()
        
        print(f"  原始年份数据: {original_year_count}/{len(df)} ({original_year_count/len(df)*100:.1f}%)")
        print(f"  增强后年份数据: {final_year_count}/{len(df)} ({final_year_count/len(df)*100:.1f}%)")
        print(f"  新增年份数据: {enhanced_count} 个")
        print()
        
        return df
    
    def batch_enhance_all(self, output_data_dir: Path, backup: bool = True):
        """批量增强所有CSV文件的年份数据"""
        print("=" * 80)
        print("批量增强年份数据")
        print("=" * 80)
        print()
        
        csv_files = sorted(output_data_dir.glob("*_analyzed.csv"))
        
        results = []
        
        for csv_file in csv_files:
            try:
                # 备份原文件
                if backup:
                    backup_file = csv_file.with_suffix('.csv.backup')
                    if not backup_file.exists():
                        import shutil
                        shutil.copy2(csv_file, backup_file)
                
                # 增强年份数据
                df_enhanced = self.enhance_year_data(csv_file)
                
                # 确保year列是字符串类型
                if 'year' in df_enhanced.columns:
                    df_enhanced['year'] = df_enhanced['year'].astype(str).replace('nan', '')
                    df_enhanced['year'] = df_enhanced['year'].replace('', pd.NA)
                
                # 保存增强后的数据
                df_enhanced.to_csv(csv_file, index=False, encoding='utf-8')
                
                results.append({
                    'file': csv_file.name,
                    'original_year_count': df_enhanced['year'].notna().sum() if 'year' in df_enhanced.columns else 0,
                    'total_urls': len(df_enhanced)
                })
                
            except Exception as e:
                print(f"  ❌ 处理 {csv_file.name} 时出错: {e}")
                print()
        
        print("=" * 80)
        print("批量增强完成")
        print("=" * 80)
        print()
        
        return results


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='增强年份数据提取')
    parser.add_argument('--all', action='store_true', help='批量处理所有公司')
    parser.add_argument('--company', type=str, help='处理单个公司')
    parser.add_argument('--no-backup', action='store_true', help='不备份原文件')
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    output_data_dir = project_root / "output_data"
    
    extractor = YearExtractor()
    
    if args.all:
        extractor.batch_enhance_all(output_data_dir, backup=not args.no_backup)
    elif args.company:
        csv_file = output_data_dir / f"{args.company}_analyzed.csv"
        if csv_file.exists():
            df_enhanced = extractor.enhance_year_data(csv_file)
            df_enhanced.to_csv(csv_file, index=False, encoding='utf-8')
            print(f"✅ 已保存增强后的数据: {csv_file}")
        else:
            print(f"❌ 文件不存在: {csv_file}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

