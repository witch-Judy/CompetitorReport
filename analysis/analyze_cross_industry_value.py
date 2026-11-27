#!/usr/bin/env python3
"""
分析跨To C/To B、跨行业分析的价值
对比参考公司和竞品公司的内容策略差异
"""

import pandas as pd
from pathlib import Path
from collections import defaultdict
import sys

sys.path.insert(0, str(Path(__file__).parent))


def analyze_cross_industry_value():
    """分析跨行业分析的价值"""
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    insight_dir = project_root / "insight"
    insight_dir.mkdir(parents=True, exist_ok=True)
    
    # 读取竞品公司统计表
    competitor_file = insight_dir / "综合内容类型统计表.csv"
    reference_file = insight_dir / "参考公司综合内容类型统计表.csv"
    
    if not competitor_file.exists() or not reference_file.exists():
        print("❌ 统计表文件不存在，请先生成统计表")
        return
    
    df_competitors = pd.read_csv(competitor_file)
    df_reference = pd.read_csv(reference_file)
    
    # 行业分类
    # To B工业自动化竞品
    competitors = df_competitors['公司'].tolist()
    
    # To B科技/软件参考公司
    to_b_tech = ['stripe', 'samsara', 'palantir']
    
    # To C消费品参考公司
    to_c_consumer = ['apple', 'xiaomi', 'byd']
    
    print("=" * 80)
    print("跨To C/To B、跨行业分析价值评估")
    print("=" * 80)
    print()
    
    # 计算平均值
    def calculate_avg(df, companies, col):
        subset = df[df['公司'].isin(companies)]
        if len(subset) > 0:
            return subset[col].mean()
        return 0
    
    # 对比分析
    analysis = {
        '竞品公司（To B工业自动化）': {
            'companies': competitors,
            'avg_total': calculate_avg(df_competitors, competitors, '总内容数'),
            'avg_product': calculate_avg(df_competitors, competitors, 'product'),
            'avg_blog': calculate_avg(df_competitors, competitors, 'blog'),
            'avg_webinar': calculate_avg(df_competitors, competitors, 'webinar'),
            'avg_resource': calculate_avg(df_competitors, competitors, 'resource'),
            'avg_newsroom': calculate_avg(df_competitors, competitors, 'newsroom'),
        },
        '参考公司（To B科技/软件）': {
            'companies': to_b_tech,
            'avg_total': calculate_avg(df_reference, to_b_tech, '总内容数'),
            'avg_product': calculate_avg(df_reference, to_b_tech, 'product'),
            'avg_blog': calculate_avg(df_reference, to_b_tech, 'blog'),
            'avg_webinar': calculate_avg(df_reference, to_b_tech, 'webinar'),
            'avg_resource': calculate_avg(df_reference, to_b_tech, 'resource'),
            'avg_newsroom': calculate_avg(df_reference, to_b_tech, 'newsroom'),
        },
        '参考公司（To C消费品）': {
            'companies': to_c_consumer,
            'avg_total': calculate_avg(df_reference, to_c_consumer, '总内容数'),
            'avg_product': calculate_avg(df_reference, to_c_consumer, 'product'),
            'avg_blog': calculate_avg(df_reference, to_c_consumer, 'blog'),
            'avg_webinar': calculate_avg(df_reference, to_c_consumer, 'webinar'),
            'avg_resource': calculate_avg(df_reference, to_c_consumer, 'resource'),
            'avg_newsroom': calculate_avg(df_reference, to_c_consumer, 'newsroom'),
        }
    }
    
    # 生成报告
    report_file = insight_dir / "跨行业分析价值评估报告.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 跨To C/To B、跨行业分析价值评估报告\n\n")
        f.write("=" * 80 + "\n\n")
        f.write("**分析日期**: " + pd.Timestamp.now().strftime('%Y-%m-%d') + "\n\n")
        f.write("=" * 80 + "\n\n")
        
        # 执行摘要
        f.write("## 执行摘要\n\n")
        f.write("本报告评估跨To C/To B、跨行业分析的价值，对比工业自动化竞品公司、")
        f.write("To B科技/软件参考公司和To C消费品参考公司的内容策略差异。\n\n")
        
        # 数据对比
        f.write("## 1. 内容策略对比\n\n")
        f.write("### 平均内容分布对比\n\n")
        f.write("| 指标 | 竞品公司<br/>(To B工业自动化) | 参考公司<br/>(To B科技/软件) | 参考公司<br/>(To C消费品) |\n")
        f.write("|------|---------------------------|------------------------|------------------------|\n")
        
        metrics = [
            ('总内容数', 'avg_total'),
            ('Product', 'avg_product'),
            ('Blog', 'avg_blog'),
            ('Webinar', 'avg_webinar'),
            ('Resource', 'avg_resource'),
            ('Newsroom', 'avg_newsroom'),
        ]
        
        for metric_name, metric_key in metrics:
            comp_val = analysis['竞品公司（To B工业自动化）'][metric_key]
            ref_b_val = analysis['参考公司（To B科技/软件）'][metric_key]
            ref_c_val = analysis['参考公司（To C消费品）'][metric_key]
            
            f.write(f"| {metric_name} | {comp_val:,.0f} | {ref_b_val:,.0f} | {ref_c_val:,.0f} |\n")
        
        f.write("\n")
        
        # 关键发现
        f.write("## 2. 关键发现\n\n")
        
        # To B vs To B对比
        f.write("### 2.1 To B工业自动化 vs To B科技/软件\n\n")
        comp = analysis['竞品公司（To B工业自动化）']
        ref_b = analysis['参考公司（To B科技/软件）']
        
        f.write("**相似点**:\n")
        f.write("- 都注重产品文档和技术资源\n")
        f.write("- 都使用Webinar进行B2B营销\n")
        f.write("- 都有较强的技术内容输出\n\n")
        
        f.write("**差异点**:\n")
        if ref_b['avg_resource'] > comp['avg_resource']:
            f.write(f"- To B科技/软件公司更注重资源内容（平均{ref_b['avg_resource']:.0f} vs {comp['avg_resource']:.0f}）\n")
        if ref_b['avg_blog'] > comp['avg_blog']:
            f.write(f"- To B科技/软件公司更注重博客内容（平均{ref_b['avg_blog']:.0f} vs {comp['avg_blog']:.0f}）\n")
        f.write("\n")
        
        # To B vs To C对比
        f.write("### 2.2 To B工业自动化 vs To C消费品\n\n")
        ref_c = analysis['参考公司（To C消费品）']
        
        f.write("**差异点**:\n")
        f.write("- **内容规模**: To C公司内容量通常更大（产品SKU多）\n")
        f.write(f"- **Webinar使用**: To B公司大量使用Webinar（平均{comp['avg_webinar']:.0f}），To C公司很少使用（平均{ref_c['avg_webinar']:.0f}）\n")
        f.write(f"- **Resource内容**: To B公司更注重技术资源（平均{comp['avg_resource']:.0f}），To C公司更注重产品展示\n")
        f.write(f"- **Blog使用**: To C公司可能使用其他内容形式（视频、社交媒体）替代传统博客\n\n")
        
        # 跨行业分析价值
        f.write("## 3. 跨行业分析的价值\n\n")
        
        f.write("### 3.1 ✅ 有价值的方面\n\n")
        f.write("#### A. 内容策略创新\n")
        f.write("- **To C公司的产品展示方式**: Apple、Xiaomi的产品页面设计可以借鉴到To B产品的展示\n")
        f.write("- **内容组织方式**: 消费品公司的信息架构可能更简洁直观\n")
        f.write("- **用户体验设计**: To C公司在UX方面通常更成熟，可以学习其导航和内容发现机制\n\n")
        
        f.write("#### B. 数字化转型参考\n")
        f.write("- **内容管理系统**: 大型To C公司通常有更完善的内容管理系统\n")
        f.write("- **多语言策略**: 全球化消费品公司的多语言内容组织方式\n")
        f.write("- **内容分发**: To C公司在内容分发和SEO方面的最佳实践\n\n")
        
        f.write("#### C. 营销渠道创新\n")
        f.write("- **视频内容**: To C公司大量使用视频内容，To B公司可以借鉴\n")
        f.write("- **社交媒体整合**: To C公司的社交媒体内容策略\n")
        f.write("- **内容切片**: To C公司将长内容切片分发的策略\n\n")
        
        f.write("#### D. 技术栈参考\n")
        f.write("- **To B科技公司的技术文档**: Stripe、Samsara的开发者文档组织方式\n")
        f.write("- **API文档**: 科技公司的API文档设计可以借鉴\n")
        f.write("- **开发者资源**: 科技公司的开发者社区建设\n\n")
        
        f.write("### 3.2 ⚠️ 需要注意的局限性\n\n")
        f.write("#### A. 行业差异\n")
        f.write("- **购买决策周期**: To B购买决策周期长，需要更多教育内容；To C决策快，需要快速产品信息\n")
        f.write("- **目标受众**: To B面向企业决策者，To C面向个人消费者\n")
        f.write("- **内容深度**: To B需要深度技术内容，To C需要简洁易懂的产品介绍\n\n")
        
        f.write("#### B. 营销方式差异\n")
        f.write("- **Webinar**: To B大量使用，To C几乎不用（消费品更倾向于发布会、直播）\n")
        f.write("- **案例研究**: To B需要详细案例，To C更注重用户评价和社交媒体\n")
        f.write("- **资源下载**: To B需要白皮书、技术文档，To C需要产品手册、使用指南\n\n")
        
        f.write("#### C. 内容组织差异\n")
        f.write("- **产品分类**: To B按行业/解决方案分类，To C按产品线/价格分类\n")
        f.write("- **内容层级**: To B内容层级更深（技术细节），To C层级更浅（快速浏览）\n")
        f.write("- **SEO策略**: To B注重行业关键词，To C注重产品关键词\n\n")
        
        # 实际应用场景
        f.write("## 4. 实际应用场景\n\n")
        
        f.write("### 4.1 可以借鉴的场景\n\n")
        f.write("1. **产品页面设计**\n")
        f.write("   - 参考Apple、Xiaomi的产品页面布局和视觉设计\n")
        f.write("   - 学习其产品对比和规格展示方式\n")
        f.write("   - 借鉴其产品视频和图片的使用\n\n")
        
        f.write("2. **内容发现机制**\n")
        f.write("   - 学习To C公司的搜索和筛选功能设计\n")
        f.write("   - 借鉴其内容推荐和个性化展示\n")
        f.write("   - 参考其移动端内容组织方式\n\n")
        
        f.write("3. **技术文档组织**\n")
        f.write("   - 参考Stripe、Samsara的API文档结构\n")
        f.write("   - 学习其开发者资源的组织方式\n")
        f.write("   - 借鉴其代码示例和教程的设计\n\n")
        
        f.write("4. **内容营销创新**\n")
        f.write("   - 学习To C公司的视频内容策略\n")
        f.write("   - 借鉴其社交媒体内容切片方式\n")
        f.write("   - 参考其内容系列化和IP化运营\n\n")
        
        f.write("### 4.2 需要谨慎应用的场景\n\n")
        f.write("1. **直接复制内容策略**\n")
        f.write("   - ❌ 不要直接复制To C的营销方式到To B场景\n")
        f.write("   - ✅ 应该提取其底层逻辑，适配To B场景\n\n")
        
        f.write("2. **忽略行业特点**\n")
        f.write("   - ❌ 不要忽略工业自动化行业的专业性和技术深度要求\n")
        f.write("   - ✅ 应该在保持专业性的基础上，借鉴To C的用户体验设计\n\n")
        
        f.write("3. **过度简化内容**\n")
        f.write("   - ❌ To C的简洁风格不适合To B的深度技术内容\n")
        f.write("   - ✅ 应该在深度和可读性之间找到平衡\n\n")
        
        # 结论
        f.write("## 5. 结论与建议\n\n")
        f.write("### 跨行业分析的价值\n\n")
        f.write("**✅ 有价值，但需要选择性借鉴**\n\n")
        f.write("跨To C/To B、跨行业分析的价值主要体现在：\n\n")
        f.write("1. **启发创新**: 不同行业的做法可以启发新的思路\n")
        f.write("2. **最佳实践**: 学习优秀公司的通用最佳实践（UX、内容组织、技术实现）\n")
        f.write("3. **趋势洞察**: 了解不同行业的内容营销趋势\n")
        f.write("4. **差异化**: 通过对比发现自身优势和可改进空间\n\n")
        
        f.write("### 建议\n\n")
        f.write("1. **保持行业专业性**: 在借鉴To C经验时，保持To B行业的技术深度和专业性\n")
        f.write("2. **选择性借鉴**: 重点学习用户体验设计、内容组织方式、技术实现等通用最佳实践\n")
        f.write("3. **适配转化**: 将To C的经验适配到To B场景，而不是直接复制\n")
        f.write("4. **持续对比**: 定期对比不同行业的内容策略，发现新趋势和机会\n")
        f.write("5. **数据驱动**: 基于数据对比，而非主观判断，来决定借鉴哪些做法\n\n")
        
        f.write("=" * 80 + "\n")
    
    print(f"✅ 报告已保存: {report_file}")
    
    # 生成对比表格
    comparison_file = insight_dir / "跨行业内容策略对比表.csv"
    
    comparison_data = []
    for category, data in analysis.items():
        comparison_data.append({
            '类别': category,
            '公司数': len(data['companies']),
            '平均总内容数': int(data['avg_total']),
            '平均Product': int(data['avg_product']),
            '平均Blog': int(data['avg_blog']),
            '平均Webinar': int(data['avg_webinar']),
            '平均Resource': int(data['avg_resource']),
            '平均Newsroom': int(data['avg_newsroom']),
        })
    
    df_comparison = pd.DataFrame(comparison_data)
    df_comparison.to_csv(comparison_file, index=False, encoding='utf-8-sig')
    print(f"✅ 对比表已保存: {comparison_file}")
    
    print()
    print("=" * 80)
    print("分析完成")
    print("=" * 80)


if __name__ == "__main__":
    analyze_cross_industry_value()



