#!/usr/bin/env python3
"""
生成Martech自动化运营机制与技术栈分析报告的可视化图表
使用seaborn风格，色系统一
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

# 设置seaborn风格和色系
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']  # 支持中文
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 创建输出目录
output_dir = Path("companyAnalysis/visualizations")
output_dir.mkdir(exist_ok=True)

# 1. Marketing Automation工具分布 - 饼图
def create_marketing_automation_pie():
    """Marketing Automation工具分布饼图"""
    data = {
        'Marketo': 10,
        'Adobe Marketing Cloud': 7,
        'Eloqua': 5,
        'HubSpot': 2,
        'Pardot': 6,
        '未检测到': 3
    }
    
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = sns.color_palette("husl", len(data))
    wedges, texts, autotexts = ax.pie(
        data.values(), 
        labels=data.keys(), 
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        textprops={'fontsize': 12}
    )
    
    # 美化文字
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    ax.set_title('Marketing Automation工具分布（18家公司）', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(output_dir / 'marketing_automation_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Marketing Automation工具分布饼图已生成")

# 2. Analytics工具分布 - 条形图
def create_analytics_bar():
    """Analytics工具分布条形图"""
    data = {
        'Adobe Analytics': 8,
        'Google Analytics 4': 18,  # 实际使用但BuiltWith未检测到
        'Matomo': 2,
        'Marketing Automation内置': 10
    }
    
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = sns.color_palette("husl", len(data))
    bars = ax.barh(data.keys(), data.values(), color=colors)
    
    # 添加数值标签
    for i, (key, value) in enumerate(data.items()):
        ax.text(value + 0.5, i, f'{value}家', va='center', fontsize=11, fontweight='bold')
    
    ax.set_xlabel('公司数量', fontsize=12)
    ax.set_title('Analytics工具分布（18家公司）', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlim(0, 20)
    plt.tight_layout()
    plt.savefig(output_dir / 'analytics_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Analytics工具分布条形图已生成")

# 3. Tag Management工具分布 - 饼图
def create_tag_management_pie():
    """Tag Management工具分布饼图"""
    data = {
        'Google Tag Manager': 17,
        'Adobe Launch': 7,
        'Adobe DTM': 7,
        'Matomo Tag Manager': 1
    }
    
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = sns.color_palette("husl", len(data))
    wedges, texts, autotexts = ax.pie(
        data.values(), 
        labels=data.keys(), 
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        textprops={'fontsize': 12}
    )
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    ax.set_title('Tag Management工具分布（18家公司）', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(output_dir / 'tag_management_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Tag Management工具分布饼图已生成")

# 4. Email Service工具分布 - 条形图
def create_email_service_bar():
    """Email Service工具分布条形图"""
    data = {
        'Amazon SES': 9,
        'Mailgun': 5,
        'SendGrid': 2,
        'HubSpot内置': 1,
        'Adobe MC内置': 1
    }
    
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = sns.color_palette("husl", len(data))
    bars = ax.barh(data.keys(), data.values(), color=colors)
    
    for i, (key, value) in enumerate(data.items()):
        ax.text(value + 0.2, i, f'{value}家', va='center', fontsize=11, fontweight='bold')
    
    ax.set_xlabel('公司数量', fontsize=12)
    ax.set_title('Email Service工具分布（18家公司）', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlim(0, 10)
    plt.tight_layout()
    plt.savefig(output_dir / 'email_service_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Email Service工具分布条形图已生成")

# 5. 内容营销规模对比 - 条形图（Top 10）
def create_content_marketing_bar():
    """内容营销规模对比条形图（Webinar + Blog）"""
    data = {
        'Siemens': 2216,  # Webinar 1952 + Blog 264
        'Yokogawa': 416,  # Webinar 416 + Blog 0
        'Ignition': 788,  # Webinar 187 + Blog 601
        'HiveMQ': 714,  # Webinar 95 + Blog 619
        'Rockwell Automation': 990,  # Webinar 117 + Blog 873
        'Tulip': 397,  # Webinar 0 + Blog 397
        'Aveva': 377,  # Webinar 1 + Blog 376
        'Cognite': 313,  # Webinar 148 + Blog 165
        'C3 AI': 131,  # Webinar 1 + Blog 130
        'Emerson': 16  # Webinar 14 + Blog 2
    }
    
    # 按值排序
    sorted_data = dict(sorted(data.items(), key=lambda x: x[1], reverse=True))
    
    fig, ax = plt.subplots(figsize=(12, 8))
    colors = sns.color_palette("husl", len(sorted_data))
    bars = ax.barh(list(sorted_data.keys()), list(sorted_data.values()), color=colors)
    
    for i, (key, value) in enumerate(sorted_data.items()):
        ax.text(value + 20, i, f'{value}', va='center', fontsize=11, fontweight='bold')
    
    ax.set_xlabel('内容数量（Webinar + Blog）', fontsize=12)
    ax.set_title('内容营销规模对比（Top 10公司）', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(output_dir / 'content_marketing_scale.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ 内容营销规模对比条形图已生成")

# 6. 18家公司内容数量热力图
def create_content_heatmap():
    """18家公司内容数量热力图"""
    # 18家公司的内容数据（Webinar、Blog、Customer Stories、Resources）
    # 数据来源：Content_Marketing_Automation_综合分析报告.md
    content_data = {
        'Siemens': [1952, 264, 27, 10],
        'Yokogawa': [416, 0, 0, 95125],
        'Rockwell': [117, 873, 0, 357],  # 简化名称
        'Ignition': [186, 601, 0, 827],
        'HiveMQ': [95, 619, 0, 59],
        'Cognite': [151, 175, 74, 59],
        'Tulip': [0, 397, 0, 1],
        'Aveva': [1, 376, 0, 4],
        'C3 AI': [1, 130, 0, 38],
        'Emerson': [14, 2, 0, 1],
        'ABB': [1, 0, 2, 5],
        'Honeywell': [7, 9, 1, 4],
        'Schneider': [0, 0, 0, 5],  # 简化名称
        'Bosch': [0, 4, 0, 0],
        'GE': [0, 0, 0, 3],
        'Hitachi': [1, 1, 16, 15],
        'UMH': [0, 1, 0, 1],
        'Univers': [0, 1, 19, 19]
    }
    
    companies = list(content_data.keys())
    content_types = ['Webinar', 'Blog', 'Stories', 'Resources']  # 简化Customer Stories为Stories
    
    # 创建DataFrame
    df = pd.DataFrame(content_data, index=content_types).T
    
    # 使用对数刻度处理大数值差异（Yokogawa的Resources数量很大）
    df_log = np.log1p(df)  # log1p = log(1+x)，避免log(0)
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # 创建热力图，使用原始数值作为注释，全部使用英文
    sns.heatmap(df_log, annot=df, fmt='d', cmap='YlOrRd', 
                cbar_kws={'label': 'Content Count (log scale)'},
                linewidths=0.5, linecolor='gray', ax=ax,
                annot_kws={'size': 8})
    
    ax.set_title('Content Volume Heatmap (18 Companies)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Content Type', fontsize=11)
    ax.set_ylabel('Company', fontsize=11)
    ax.set_xticklabels(content_types, rotation=0, fontsize=10)
    ax.set_yticklabels(companies, rotation=0, fontsize=9)
    
    # 添加英文说明
    fig.text(0.5, 0.01, 'Note: Log scale used for color intensity. Actual values shown in cells.', 
             ha='center', fontsize=9, style='italic')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'content_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ 18家公司内容数量热力图已生成")

# 7. 意识层级覆盖度对比 - 雷达图
def create_awareness_level_radar():
    """意识层级覆盖度对比雷达图（Top 5公司）"""
    categories = ['Unaware', 'Problem Aware', 'Solution Aware', 'Product Aware', 'Most Aware']
    
    companies_data = {
        'Siemens': [5, 4, 5, 5, 4],
        'Cognite': [4, 3, 5, 3, 3],
        'ABB': [3, 3, 4, 3, 2],
        'Ignition': [5, 2, 5, 2, 2],
        'Rockwell Automation': [4, 3, 4, 3, 3]
    }
    
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]  # 闭合
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    colors = sns.color_palette("husl", len(companies_data))
    
    for i, (company, values) in enumerate(companies_data.items()):
        values += values[:1]  # 闭合
        ax.plot(angles, values, 'o-', linewidth=2, label=company, color=colors[i])
        ax.fill(angles, values, alpha=0.25, color=colors[i])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11)
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(['1', '2', '3', '4', '5'], fontsize=10)
    ax.set_title('意识层级覆盖度对比（Top 5公司）', fontsize=16, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    plt.tight_layout()
    plt.savefig(output_dir / 'awareness_level_radar.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ 意识层级覆盖度对比雷达图已生成")

# 8. 内容营销策略与技术栈关联 - 散点图
def create_content_tech_correlation():
    """内容营销规模与技术栈复杂度关联散点图"""
    data = {
        '公司': ['Siemens', 'Yokogawa', 'Rockwell', 'Ignition', 'Cognite', 
                'HiveMQ', 'Tulip', 'Aveva', 'C3 AI', 'Emerson'],
        '内容规模': [2216, 416, 990, 788, 313, 714, 397, 377, 131, 16],
        '技术栈复杂度': [5, 3, 4, 3, 2, 2, 2, 3, 2, 2]  # 1=基础，5=企业级
    }
    
    df = pd.DataFrame(data)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    colors = sns.color_palette("husl", len(df))
    
    scatter = ax.scatter(df['技术栈复杂度'], df['内容规模'], 
                        s=200, c=colors, alpha=0.6, edgecolors='black', linewidth=2)
    
    # 添加公司标签
    for i, row in df.iterrows():
        ax.annotate(row['公司'], (row['技术栈复杂度'], row['内容规模']),
                   xytext=(5, 5), textcoords='offset points', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('技术栈复杂度（1=基础，5=企业级）', fontsize=12)
    ax.set_ylabel('内容营销规模（Webinar + Blog）', fontsize=12)
    ax.set_title('内容营销规模与技术栈复杂度关联', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'content_tech_correlation.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ 内容营销规模与技术栈复杂度关联散点图已生成")

# 9. Webinar vs Blog 对比 - 散点图
def create_webinar_blog_scatter():
    """Webinar vs Blog 对比散点图"""
    data = {
        '公司': ['Siemens', 'Yokogawa', 'Ignition', 'HiveMQ', 'Rockwell', 
                'Cognite', 'Tulip', 'Aveva', 'C3 AI', 'Emerson'],
        'Webinar': [1952, 416, 187, 95, 117, 148, 0, 1, 1, 14],
        'Blog': [264, 0, 601, 619, 873, 165, 397, 376, 130, 2]
    }
    
    df = pd.DataFrame(data)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    colors = sns.color_palette("husl", len(df))
    
    scatter = ax.scatter(df['Blog'], df['Webinar'], 
                        s=300, c=colors, alpha=0.6, edgecolors='black', linewidth=2)
    
    # 添加公司标签
    for i, row in df.iterrows():
        ax.annotate(row['公司'], (row['Blog'], row['Webinar']),
                   xytext=(5, 5), textcoords='offset points', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Blog数量', fontsize=12)
    ax.set_ylabel('Webinar数量', fontsize=12)
    ax.set_title('Webinar vs Blog 内容策略对比', fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'webinar_blog_scatter.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Webinar vs Blog 对比散点图已生成")

# 10. 转化机制对比 - 分组条形图
def create_conversion_mechanisms_grouped():
    """转化机制对比分组条形图（Top 5公司）"""
    companies = ['Siemens', 'Rockwell', 'Yokogawa', 'Ignition', 'Cognite']
    
    contact_forms = [2074, 11635, 4387, 109, 67]
    demo_trial = [3957, 873, 3198, 98, 190]
    content_downloads = [582, 634, 119682, 967, 438]
    
    x = np.arange(len(companies))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(14, 8))
    colors = sns.color_palette("husl", 3)
    
    bars1 = ax.bar(x - width, contact_forms, width, label='Contact Forms', color=colors[0])
    bars2 = ax.bar(x, demo_trial, width, label='Demo/Trial', color=colors[1])
    bars3 = ax.bar(x + width, content_downloads, width, label='Content Downloads', color=colors[2])
    
    ax.set_ylabel('数量', fontsize=12)
    ax.set_title('转化机制对比（Top 5公司）', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(companies, fontsize=11)
    ax.legend(fontsize=11)
    ax.set_yscale('log')  # 使用对数刻度因为数值差异大
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_dir / 'conversion_mechanisms_grouped.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ 转化机制对比分组条形图已生成")

def create_dashboard():
    """创建综合Dashboard，合并所有图表"""
    from PIL import Image
    
    # 定义要合并的图表（按布局顺序）
    charts = [
        'content_heatmap.png',           # 大图：内容数量热力图
        'marketing_automation_distribution.png',  # 饼图
        'analytics_distribution.png',    # 条形图
        'tag_management_distribution.png',  # 饼图
        'email_service_distribution.png',   # 条形图
        'content_marketing_scale.png',   # 条形图
        'awareness_level_radar.png',     # 雷达图
        'webinar_blog_scatter.png',      # 散点图
        'conversion_mechanisms_grouped.png',  # 分组条形图
        'content_tech_correlation.png',  # 散点图
    ]
    
    # 加载所有图片
    images = []
    for chart in charts:
        img_path = output_dir / chart
        if img_path.exists():
            img = Image.open(img_path)
            images.append(img)
    
    if len(images) < 10:
        print(f"警告：只找到 {len(images)} 张图表")
        return
    
    # Dashboard布局：3行4列，第一行热力图占2x2
    # 布局设计：
    # [热力图(2x2)] [饼图1] [条形图1]
    # [热力图(2x2)] [饼图2] [条形图2]
    # [条形图3] [雷达图] [散点图1] [散点图2]
    # [分组条形图(2x1)] [散点图3(2x1)]
    
    # 计算单元格大小
    cell_width = 600
    cell_height = 450
    
    # Dashboard尺寸：4列 x 4行
    dashboard_width = cell_width * 4
    dashboard_height = cell_height * 4
    
    # 创建Dashboard画布
    dashboard = Image.new('RGB', (dashboard_width, dashboard_height), 'white')
    
    # 调整图片大小并放置
    def resize_and_paste(img, x, y, w, h):
        """调整图片大小并粘贴到指定位置"""
        img_resized = img.resize((w, h), Image.Resampling.LANCZOS)
        dashboard.paste(img_resized, (x, y))
    
    # 布局：
    # Row 0-1: 热力图(0,0, 2x2) | 饼图1(2,0) | 条形图1(3,0)
    #                          | 饼图2(2,1) | 条形图2(3,1)
    # Row 2: 条形图3(0,2) | 雷达图(1,2) | 散点图1(2,2) | 散点图2(3,2)
    # Row 3: 分组条形图(0,3, 2x1) | 散点图3(2,3, 2x1)
    
    # 热力图 - 占据左上2x2
    resize_and_paste(images[0], 0, 0, cell_width * 2, cell_height * 2)
    
    # 饼图1 - Marketing Automation (2,0)
    resize_and_paste(images[1], cell_width * 2, 0, cell_width, cell_height)
    
    # 条形图1 - Analytics (3,0)
    resize_and_paste(images[2], cell_width * 3, 0, cell_width, cell_height)
    
    # 饼图2 - Tag Management (2,1)
    resize_and_paste(images[3], cell_width * 2, cell_height, cell_width, cell_height)
    
    # 条形图2 - Email Service (3,1)
    resize_and_paste(images[4], cell_width * 3, cell_height, cell_width, cell_height)
    
    # 条形图3 - Content Marketing Scale (0,2)
    resize_and_paste(images[5], 0, cell_height * 2, cell_width, cell_height)
    
    # 雷达图 - Awareness Level (1,2)
    resize_and_paste(images[6], cell_width, cell_height * 2, cell_width, cell_height)
    
    # 散点图1 - Webinar vs Blog (2,2)
    resize_and_paste(images[7], cell_width * 2, cell_height * 2, cell_width, cell_height)
    
    # 散点图2 - Conversion Mechanisms (3,2)
    resize_and_paste(images[8], cell_width * 3, cell_height * 2, cell_width, cell_height)
    
    # 散点图3 - Content Tech Correlation (0,3, 占2列)
    resize_and_paste(images[9], 0, cell_height * 3, cell_width * 2, cell_height)
    
    # 添加标题区域（在底部右侧留空或添加说明）
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(dashboard)
    
    # 尝试使用系统字体
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # 在右下角添加说明
    info_text = "Martech & Content Marketing Analysis Dashboard\n18 Companies | Data: BuiltWith + Browser Verification"
    draw.text((cell_width * 2 + 50, cell_height * 3 + 150), info_text, fill='#333333', font=subtitle_font)
    
    # 保存Dashboard
    dashboard.save(output_dir / 'dashboard.png', quality=95)
    print("✓ 综合Dashboard已生成")


if __name__ == '__main__':
    print("开始生成Martech分析报告可视化图表...")
    print("=" * 50)
    
    create_marketing_automation_pie()
    create_analytics_bar()
    create_tag_management_pie()
    create_email_service_bar()
    create_content_marketing_bar()
    create_content_heatmap()
    create_awareness_level_radar()
    create_content_tech_correlation()
    create_webinar_blog_scatter()
    create_conversion_mechanisms_grouped()
    create_dashboard()  # 最后生成Dashboard
    
    print("=" * 50)
    print(f"✓ 所有图表已生成完成！")
    print(f"✓ 输出目录: {output_dir.absolute()}")

