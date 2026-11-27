#!/usr/bin/env python3
"""
修复参考公司的内容类型分类
扩展分类逻辑以识别更多newsroom变体
"""

import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))


def fix_content_type_classification(csv_file: Path) -> pd.DataFrame:
    """修复内容类型分类"""
    df = pd.read_csv(csv_file)
    
    # 扩展newsroom识别逻辑
    newsroom_keywords = [
        'newsroom', 'press', 'media', 'announcement', 'news-list', 
        'news_list', 'mediakit', 'media-kit', 'press-kit', 'presskit',
        'press-release', 'press_release', 'pressreleases'
    ]
    
    # 扩展webinar识别逻辑
    webinar_keywords = [
        'webinar', 'webinars', 'on-demand', 'on_demand', 'event', 'events',
        'workshop', 'workshops', 'live-session', 'live_session'
    ]
    
    # 修复分类
    for idx, row in df.iterrows():
        path_lower = str(row.get('path', '')).lower()
        
        # 检查newsroom
        if any(keyword in path_lower for keyword in newsroom_keywords):
            if df.loc[idx, 'content_type'] != 'newsroom':
                df.loc[idx, 'content_type'] = 'newsroom'
        
        # 检查webinar
        elif any(keyword in path_lower for keyword in webinar_keywords):
            if df.loc[idx, 'content_type'] != 'webinar':
                df.loc[idx, 'content_type'] = 'webinar'
    
    return df


def main():
    """修复所有参考公司的分类"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    output_data_dir = project_root / "output_data" / "reference"
    
    print("=" * 80)
    print("修复参考公司内容类型分类")
    print("=" * 80)
    print()
    
    csv_files = sorted(output_data_dir.glob("*_analyzed.csv"))
    
    for csv_file in csv_files:
        company = csv_file.stem.replace('_analyzed', '')
        print(f"修复 {company}...")
        
        try:
            df = df_original = pd.read_csv(csv_file)
            
            # 修复分类
            df_fixed = fix_content_type_classification(csv_file)
            
            # 统计变化
            newsroom_before = len(df_original[df_original['content_type'] == 'newsroom'])
            newsroom_after = len(df_fixed[df_fixed['content_type'] == 'newsroom'])
            
            webinar_before = len(df_original[df_original['content_type'] == 'webinar'])
            webinar_after = len(df_fixed[df_fixed['content_type'] == 'webinar'])
            
            # 保存修复后的文件
            df_fixed.to_csv(csv_file, index=False, encoding='utf-8-sig')
            
            print(f"  ✅ 修复完成")
            print(f"     Newsroom: {newsroom_before} -> {newsroom_after} (+{newsroom_after - newsroom_before})")
            print(f"     Webinar: {webinar_before} -> {webinar_after} (+{webinar_after - webinar_before})")
            
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            import traceback
            traceback.print_exc()
        print()
    
    print("=" * 80)
    print("修复完成")
    print("=" * 80)
    print()
    print("请重新运行 generate_reference_content_type_summary.py 更新统计表")


if __name__ == "__main__":
    main()



