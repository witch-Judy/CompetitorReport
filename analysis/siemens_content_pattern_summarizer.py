#!/usr/bin/env python3
"""
Siemens 内容模式总结器
从深度分析结果中总结内容架构模式和写作原因
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List


class SiemensContentPatternSummarizer:
    """Siemens内容模式总结器"""
    
    def __init__(self):
        """初始化总结器"""
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        
        self.analysis_dir = project_root / "Knowledge" / "Siemens内容营销策略研究" / "内容深度分析"
        self.output_dir = self.analysis_dir / "写作模式"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_analysis_data(self, content_type: str = None) -> List[Dict]:
        """加载分析数据"""
        all_results = []
        
        if content_type:
            json_file = self.analysis_dir / f"{content_type}_analysis_data.json"
            if json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    all_results = json.load(f)
        else:
            # 加载所有分析数据
            for json_file in self.analysis_dir.glob("*_analysis_data.json"):
                with open(json_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                    all_results.extend(results)
        
        return all_results
    
    def summarize_content_architecture(self, results: List[Dict]) -> Dict:
        """总结内容架构模式"""
        patterns = {
            'title_patterns': Counter(),
            'heading_structure': defaultdict(int),
            'content_organization': defaultdict(int),
            'formatting_patterns': defaultdict(int),
        }
        
        for result in results:
            structure = result.get('structure', {})
            
            # 标题模式
            title_fmt = structure.get('title_structure', {}).get('format', 'unknown')
            patterns['title_patterns'][title_fmt] += 1
            
            # 标题层级
            max_depth = structure.get('heading_hierarchy', {}).get('max_depth', 0)
            patterns['heading_structure'][max_depth] += 1
            
            # 内容组织
            word_count = result.get('content_data', {}).get('word_count', 0)
            if word_count < 300:
                patterns['content_organization']['short'] += 1
            elif word_count < 1000:
                patterns['content_organization']['medium'] += 1
            else:
                patterns['content_organization']['long'] += 1
            
            # 格式化
            fmt = structure.get('formatting_patterns', {})
            if fmt.get('has_lists'):
                patterns['formatting_patterns']['uses_lists'] += 1
            if fmt.get('has_images'):
                patterns['formatting_patterns']['uses_images'] += 1
            if fmt.get('has_links'):
                patterns['formatting_patterns']['uses_links'] += 1
        
        return patterns
    
    def summarize_writing_reasons(self, results: List[Dict]) -> Dict:
        """总结写作原因"""
        reasons = {
            'seo_focus': Counter(),
            'ux_focus': Counter(),
            'marketing_focus': Counter(),
            'content_strategy': Counter(),
        }
        
        for result in results:
            reasons_data = result.get('reasons', {})
            
            # SEO焦点
            seo = reasons_data.get('seo_optimization', {})
            if seo.get('has_meta_description'):
                reasons['seo_focus']['meta_description'] += 1
            if seo.get('has_structured_data'):
                reasons['seo_focus']['structured_data'] += 1
            if seo.get('title_optimized'):
                reasons['seo_focus']['title_optimized'] += 1
            
            # UX焦点
            ux = reasons_data.get('user_experience', {})
            readability = ux.get('readability', {}).get('score', 0)
            if readability >= 2:
                reasons['ux_focus']['high_readability'] += 1
            
            scannability = ux.get('scannability', {}).get('score', 0)
            if scannability >= 2:
                reasons['ux_focus']['high_scannability'] += 1
            
            # 营销焦点
            marketing = reasons_data.get('marketing_goals', {})
            cta = marketing.get('call_to_action', [])
            if cta:
                reasons['marketing_focus']['has_cta'] += 1
            
            content_depth = marketing.get('content_depth', '')
            reasons['marketing_focus'][f'depth_{content_depth}'] += 1
            
            # 内容策略
            strategy = reasons_data.get('content_strategy', {})
            content_type = strategy.get('content_type', 'unknown')
            reasons['content_strategy'][content_type] += 1
            
            purpose = strategy.get('content_purpose', 'unknown')
            reasons['content_strategy'][f'purpose_{purpose}'] += 1
        
        return reasons
    
    def generate_pattern_report(self, content_type: str = None) -> str:
        """生成模式总结报告"""
        results = self.load_analysis_data(content_type)
        
        if not results:
            print(f"❌ 未找到分析数据（content_type: {content_type}）")
            return ""
        
        # 总结模式
        architecture = self.summarize_content_architecture(results)
        reasons = self.summarize_writing_reasons(results)
        
        # 生成报告
        if content_type:
            report_file = self.output_dir / f"{content_type}_内容模式总结.md"
        else:
            report_file = self.output_dir / "内容模式总结.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Siemens 内容架构与写作模式总结\n\n")
            f.write("=" * 80 + "\n\n")
            if content_type:
                f.write(f"**内容类型**: {content_type}\n")
            f.write(f"**分析样本数**: {len(results)}\n\n")
            f.write("=" * 80 + "\n\n")
            
            # 内容架构模式
            f.write("## 内容架构模式\n\n")
            
            f.write("### 标题结构模式\n\n")
            for pattern, count in architecture['title_patterns'].most_common():
                pct = count / len(results) * 100
                f.write(f"- **{pattern}**: {count} 个 ({pct:.1f}%)\n")
            f.write("\n")
            
            f.write("### 标题层级结构\n\n")
            f.write("| 最大深度 | 内容数 | 占比 |\n")
            f.write("|----------|--------|------|\n")
            total = sum(architecture['heading_structure'].values())
            for depth, count in sorted(architecture['heading_structure'].items()):
                pct = count / total * 100 if total > 0 else 0
                f.write(f"| {depth} 层 | {count} | {pct:.1f}% |\n")
            f.write("\n")
            
            f.write("### 内容长度分布\n\n")
            for length_type, count in architecture['content_organization'].items():
                pct = count / len(results) * 100
                f.write(f"- **{length_type}** (<300字/300-1000字/>1000字): {count} 个 ({pct:.1f}%)\n")
            f.write("\n")
            
            f.write("### 格式化元素使用\n\n")
            for element, count in architecture['formatting_patterns'].items():
                pct = count / len(results) * 100
                f.write(f"- **{element}**: {count} 个 ({pct:.1f}%)\n")
            f.write("\n")
            
            # 写作原因总结
            f.write("## 写作原因总结\n\n")
            
            f.write("### SEO优化策略\n\n")
            for strategy, count in reasons['seo_focus'].most_common():
                pct = count / len(results) * 100
                f.write(f"- **{strategy}**: {count} 个 ({pct:.1f}%)\n")
            f.write("\n")
            
            f.write("### 用户体验设计\n\n")
            for ux_element, count in reasons['ux_focus'].most_common():
                pct = count / len(results) * 100
                f.write(f"- **{ux_element}**: {count} 个 ({pct:.1f}%)\n")
            f.write("\n")
            
            f.write("### 营销目标\n\n")
            for goal, count in reasons['marketing_focus'].most_common():
                pct = count / len(results) * 100
                f.write(f"- **{goal}**: {count} 个 ({pct:.1f}%)\n")
            f.write("\n")
            
            f.write("### 内容策略\n\n")
            for strategy, count in reasons['content_strategy'].most_common():
                pct = count / len(results) * 100
                f.write(f"- **{strategy}**: {count} 个 ({pct:.1f}%)\n")
            f.write("\n")
            
            # 架构与原因关联分析
            f.write("## 架构与原因关联分析\n\n")
            f.write("### 为什么这样写？\n\n")
            
            # 标题格式原因
            f.write("#### 标题格式选择的原因\n\n")
            dash_count = architecture['title_patterns'].get('dash_separated', 0)
            if dash_count > 0:
                f.write(f"- **Dash分隔符** ({dash_count}个): 用于SEO优化，便于搜索引擎理解标题结构\n")
            pipe_count = architecture['title_patterns'].get('pipe_separated', 0)
            if pipe_count > 0:
                f.write(f"- **Pipe分隔符** ({pipe_count}个): 用于品牌标识，格式如\"标题 | 品牌名\"\n")
            f.write("\n")
            
            # 内容组织原因
            f.write("#### 内容组织的原因\n\n")
            short_count = architecture['content_organization'].get('short', 0)
            if short_count > 0:
                f.write(f"- **短内容** ({short_count}个): 快速传达信息，适合移动端阅读\n")
            long_count = architecture['content_organization'].get('long', 0)
            if long_count > 0:
                f.write(f"- **长内容** ({long_count}个): 深度教育，建立权威，SEO友好\n")
            f.write("\n")
            
            # 格式化元素原因
            f.write("#### 格式化元素使用的原因\n\n")
            if architecture['formatting_patterns'].get('uses_lists', 0) > 0:
                f.write("- **列表**: 提高可扫描性，便于快速理解要点\n")
            if architecture['formatting_patterns'].get('uses_images', 0) > 0:
                f.write("- **图片**: 增强视觉吸引力，提高参与度\n")
            if architecture['formatting_patterns'].get('uses_links', 0) > 0:
                f.write("- **链接**: 引导用户深入探索，提高网站停留时间\n")
            f.write("\n")
            
            # 总结
            f.write("## 总结\n\n")
            f.write("### Siemens内容架构特点\n\n")
            f.write("1. **标题结构**: 主要使用dash或pipe分隔符，便于SEO和品牌识别\n")
            f.write("2. **内容组织**: 根据内容类型调整长度，平衡信息量和可读性\n")
            f.write("3. **格式化**: 使用列表、图片、链接等元素提高用户体验\n\n")
            
            f.write("### 写作原因分析\n\n")
            f.write("1. **SEO优先**: 重视Meta标签、标题优化、结构化数据\n")
            f.write("2. **用户体验**: 注重可读性和可扫描性\n")
            f.write("3. **营销目标**: 根据内容类型调整深度和CTA使用\n")
            f.write("4. **内容策略**: 明确的内容类型和目的定位\n\n")
        
        print(f"✅ 模式总结报告已保存: {report_file}")
        return str(report_file)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Siemens内容模式总结')
    parser.add_argument('--content-type', type=str,
                       help='内容类型（如: blog, webinar）')
    
    args = parser.parse_args()
    
    summarizer = SiemensContentPatternSummarizer()
    summarizer.generate_pattern_report(args.content_type)
    
    print("\n" + "=" * 80)
    print("✅ Siemens 内容模式总结完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()



