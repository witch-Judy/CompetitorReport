#!/usr/bin/env python3
"""
使用LLM重新分类的结果更新Webinar分析报告
"""

import json
from pathlib import Path
from collections import Counter
import sys
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from analysis.siemens_webinar_deep_analysis import SiemensWebinarDeepAnalyzer

def update_classification():
    """使用LLM重新分类的结果更新报告"""
    
    analyzer = SiemensWebinarDeepAnalyzer()
    
    # 读取LLM重新分类结果
    reclassified_file = analyzer.insight_dir / "unknown_webinar_reclassified.json"
    
    if not reclassified_file.exists():
        print("❌ 未找到重新分类结果文件")
        return
    
    with open(reclassified_file, 'r', encoding='utf-8') as f:
        reclassified = json.load(f)
    
    # 构建标题到新分类的映射
    title_to_new_type = {r['title']: r['type'] for r in reclassified}
    
    # 重新分析所有Webinar
    webinars = analyzer.extract_webinar_titles()
    
    # 更新分类
    updated_type_dist = Counter()
    updated_tendency_dist = Counter()
    valid_webinars = []
    directory_count = 0
    
    for webinar in webinars:
        original_classification = analyzer.classify_webinar_type(webinar['title_lower'])
        
        # 如果是unknown，使用LLM重新分类的结果
        if original_classification['type'] == 'unknown':
            if webinar['title'] in title_to_new_type:
                new_type = title_to_new_type[webinar['title']]
                # 更新分类
                original_classification['type'] = new_type
                if new_type == 'product':
                    original_classification['tendency'] = '产品用法'
                elif new_type == 'education':
                    original_classification['tendency'] = '科普/教育'
                elif new_type == 'technical':
                    original_classification['tendency'] = '技术深度'
                elif new_type == 'mixed':
                    original_classification['tendency'] = '混合型'
        
        # 跳过目录页
        if original_classification['type'] == 'directory':
            directory_count += 1
            continue
        
        updated_type_dist[original_classification['type']] += 1
        updated_tendency_dist[original_classification['tendency']] += 1
        webinar['classification'] = original_classification
        valid_webinars.append(webinar)
    
    # 生成更新后的报告
    report_file = analyzer.insight_dir / "Siemens_Webinar深度分析报告_LLM增强.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Siemens Webinar 深度分析报告 (LLM增强版)\n\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"**分析日期**: {pd.Timestamp.now().strftime('%Y-%m-%d')}\n")
        f.write(f"**总Webinar数**: {len(webinars):,}\n")
        f.write(f"**目录/导航页**: {directory_count}\n")
        f.write(f"**有效Webinar**: {len(valid_webinars):,}\n")
        f.write(f"**使用LLM重新分类**: ✅ 是\n\n")
        f.write("=" * 80 + "\n\n")
        
        # 类型分布
        f.write("## 1. 内容倾向分析 (LLM增强)\n\n")
        f.write("### 类型分布\n\n")
        f.write("| 类型 | 数量 | 占比 | 说明 |\n")
        f.write("|------|------|------|------|\n")
        
        total = len(valid_webinars)
        type_descriptions = {
            'education': '科普/教育 - 介绍概念、趋势、基础知识',
            'product': '产品用法 - 演示功能、使用方法、实操',
            'technical': '技术深度 - 深入技术细节、架构、开发',
            'mixed': '混合型 - 同时包含教育和产品内容',
            'unknown': '未知 - 无法明确分类'
        }
        
        for type_name, count in updated_type_dist.most_common():
            pct = count / total * 100 if total > 0 else 0
            desc = type_descriptions.get(type_name, '未知')
            f.write(f"| {type_name} | {count:,} | {pct:.1f}% | {desc} |\n")
        
        f.write("\n")
        
        # 对比原始分类
        f.write("### 分类改进对比\n\n")
        f.write("| 类型 | 原始数量 | LLM增强后数量 | 变化 |\n")
        f.write("|------|----------|--------------|------|\n")
        
        original_counts = {
            'unknown': 210,
            'product': 118,
            'technical': 38,
            'education': 33,
            'mixed': 18
        }
        
        for type_name in ['unknown', 'product', 'education', 'technical', 'mixed']:
            original = original_counts.get(type_name, 0)
            new = updated_type_dist.get(type_name, 0)
            change = new - original
            change_pct = (change / original * 100) if original > 0 else 0
            f.write(f"| {type_name} | {original} | {new} | {change:+.0f} ({change_pct:+.1f}%) |\n")
        
        f.write("\n")
        f.write("=" * 80 + "\n")
    
    print(f"✅ 更新后的报告已保存: {report_file}")
    
    # 打印统计
    print("\n" + "=" * 80)
    print("LLM增强分类结果")
    print("=" * 80)
    print()
    print("类型分布:")
    for type_name, count in updated_type_dist.most_common():
        pct = count / total * 100 if total > 0 else 0
        print(f"  {type_name:12s}: {count:3d} ({pct:5.1f}%)")
    
    print()
    print("改进效果:")
    original_unknown = 210
    new_unknown = updated_type_dist.get('unknown', 0)
    reduction = original_unknown - new_unknown
    reduction_pct = (reduction / original_unknown * 100) if original_unknown > 0 else 0
    print(f"  Unknown减少: {reduction} ({reduction_pct:.1f}%)")
    print(f"  Unknown比例: 从50.4%降至{new_unknown/total*100:.1f}%")


if __name__ == "__main__":
    update_classification()

