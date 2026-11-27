#!/usr/bin/env python3
"""
重新检查ABB的Webinar内容
遍历所有content类别，查找可能被误分类的webinar内容
"""

import pandas as pd
from pathlib import Path
from collections import Counter
import re

def analyze_abb_webinar():
    """分析ABB的Webinar内容"""
    project_root = Path(__file__).parent.parent
    csv_file = project_root / "output_data" / "abb_analyzed.csv"
    
    if not csv_file.exists():
        print(f"❌ 文件不存在: {csv_file}")
        return
    
    df = pd.read_csv(csv_file)
    print(f"✅ 加载数据: {len(df)}行")
    
    # 1. 检查is_webinar列
    print("\n" + "="*80)
    print("1. is_webinar列统计")
    print("="*80)
    if 'is_webinar' in df.columns:
        webinar_count = df['is_webinar'].sum()
        print(f"is_webinar=True的数量: {webinar_count}")
        if webinar_count > 0:
            webinar_rows = df[df['is_webinar'] == True]
            print("\nWebinar URL:")
            for url in webinar_rows['url']:
                print(f"  - {url}")
    
    # 2. 检查content_type列
    print("\n" + "="*80)
    print("2. content_type列统计")
    print("="*80)
    if 'content_type' in df.columns:
        content_type_counts = df['content_type'].value_counts()
        print(content_type_counts)
    
    # 3. 检查URL中包含webinar的行
    print("\n" + "="*80)
    print("3. URL中包含'webinar'的行")
    print("="*80)
    if 'url' in df.columns:
        webinar_urls = df[df['url'].str.contains('webinar', case=False, na=False)]
        print(f"数量: {len(webinar_urls)}")
        if len(webinar_urls) > 0:
            print("\n前20个URL:")
            for url in webinar_urls['url'].head(20):
                print(f"  - {url}")
    
    # 4. 检查path中包含webinar的行
    print("\n" + "="*80)
    print("4. path中包含'webinar'的行")
    print("="*80)
    if 'path' in df.columns:
        webinar_paths = df[df['path'].str.contains('webinar', case=False, na=False)]
        print(f"数量: {len(webinar_paths)}")
        if len(webinar_paths) > 0:
            print("\n所有path:")
            for path in webinar_paths['path']:
                print(f"  - {path}")
    
    # 5. 检查可能包含webinar的关键词
    print("\n" + "="*80)
    print("5. 检查可能包含webinar的关键词")
    print("="*80)
    keywords = ['event', 'events', 'online', 'virtual', 'video', 'videos', 'training', 
                'seminar', 'workshop', 'session', 'live', 'streaming', 'recorded', 
                'on-demand', 'ondemand', 'webcast', 'webinar-series']
    
    for keyword in keywords:
        matches = df[df['path'].str.contains(keyword, case=False, na=False)]
        if len(matches) > 0:
            print(f"\n{keyword}: {len(matches)}个")
            # 按content_type分组
            if 'content_type' in matches.columns:
                type_counts = matches['content_type'].value_counts()
                print(f"  按content_type分组:")
                for ct, count in type_counts.items():
                    print(f"    - {ct}: {count}")
            # 显示前5个path
            print(f"  前5个path:")
            for path in matches['path'].head(5):
                print(f"    - {path}")
    
    # 6. 检查events相关的内容
    print("\n" + "="*80)
    print("6. Events相关内容的详细分析")
    print("="*80)
    events_df = df[df['path'].str.contains('event', case=False, na=False)]
    print(f"Events相关路径总数: {len(events_df)}")
    
    if len(events_df) > 0:
        print("\n按content_type分组:")
        if 'content_type' in events_df.columns:
            type_counts = events_df['content_type'].value_counts()
            for ct, count in type_counts.items():
                print(f"  - {ct}: {count}")
        
        print("\n所有events路径:")
        for idx, row in events_df.iterrows():
            print(f"  - {row['path']} (content_type: {row.get('content_type', 'N/A')})")
    
    # 7. 检查resource类型的内容
    print("\n" + "="*80)
    print("7. Resource类型内容的详细分析")
    print("="*80)
    if 'content_type' in df.columns:
        resources = df[df['content_type'] == 'resource']
        print(f"Resource总数: {len(resources)}")
        
        if len(resources) > 0:
            print("\n所有resource路径:")
            for path in resources['path']:
                print(f"  - {path}")
            
            # 检查resource中是否包含webinar相关内容
            webinar_resources = resources[resources['path'].str.contains(
                'webinar|event|video|training|seminar|workshop', case=False, na=False)]
            if len(webinar_resources) > 0:
                print(f"\nResource中包含webinar相关关键词的路径: {len(webinar_resources)}")
                for path in webinar_resources['path']:
                    print(f"  - {path}")
    
    # 8. 建议的webinar计数
    print("\n" + "="*80)
    print("8. 建议的Webinar计数方法")
    print("="*80)
    
    # 方法1: 使用is_webinar列
    method1_count = df['is_webinar'].sum() if 'is_webinar' in df.columns else 0
    
    # 方法2: URL或path中包含webinar
    if 'url' in df.columns and 'path' in df.columns:
        method2_df = df[
            df['url'].str.contains('webinar', case=False, na=False) |
            df['path'].str.contains('webinar', case=False, na=False)
        ]
        method2_count = len(method2_df)
    else:
        method2_count = 0
    
    # 方法3: events页面（可能包含webinar）
    if 'path' in df.columns:
        events_count = len(df[df['path'].str.contains('event', case=False, na=False)])
    else:
        events_count = 0
    
    print(f"方法1 (is_webinar列): {method1_count}")
    print(f"方法2 (URL/path包含webinar): {method2_count}")
    print(f"方法3 (events页面): {events_count}")
    print(f"\n建议: 如果events页面下实际包含webinar内容，应该访问这些页面进行验证")

if __name__ == "__main__":
    analyze_abb_webinar()

