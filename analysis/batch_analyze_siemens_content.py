#!/usr/bin/env python3
"""
Siemens 内容批量分析脚本
一次性分析多个内容类型
"""

import subprocess
import sys
from pathlib import Path


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='批量分析Siemens内容')
    parser.add_argument('--content-types', nargs='+',
                       default=['blog', 'webinar', 'industry', 'customer_story'],
                       help='要分析的内容类型')
    parser.add_argument('--limit', type=int, default=20,
                       help='每个类型的分析数量限制')
    parser.add_argument('--skip-analysis', action='store_true',
                       help='跳过分析，只总结模式')
    parser.add_argument('--skip-summary', action='store_true',
                       help='跳过总结，只进行分析')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("Siemens 内容批量分析")
    print("=" * 80)
    print()
    
    script_dir = Path(__file__).parent
    
    # 分析每个内容类型
    if not args.skip_analysis:
        print("阶段1: 深度内容分析")
        print("-" * 80)
        print()
        
        for content_type in args.content_types:
            print(f"分析: {content_type}")
            print("-" * 80)
            
            cmd = [
                sys.executable,
                str(script_dir / "siemens_content_deep_analyzer.py"),
                "--content-type", content_type,
                "--limit", str(args.limit)
            ]
            
            try:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                print(result.stdout)
                if result.stderr:
                    print(result.stderr)
            except subprocess.CalledProcessError as e:
                print(f"❌ 分析 {content_type} 时出错:")
                print(e.stderr)
            
            print()
    
    # 总结模式
    if not args.skip_summary:
        print("阶段2: 总结内容模式")
        print("-" * 80)
        print()
        
        for content_type in args.content_types:
            print(f"总结: {content_type}")
            print("-" * 80)
            
            cmd = [
                sys.executable,
                str(script_dir / "siemens_content_pattern_summarizer.py"),
                "--content-type", content_type
            ]
            
            try:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                print(result.stdout)
                if result.stderr:
                    print(result.stderr)
            except subprocess.CalledProcessError as e:
                print(f"❌ 总结 {content_type} 时出错:")
                print(e.stderr)
            
            print()
        
        # 生成综合总结
        print("生成综合模式总结")
        print("-" * 80)
        
        cmd = [
            sys.executable,
            str(script_dir / "siemens_content_pattern_summarizer.py")
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ 生成综合总结时出错:")
            print(e.stderr)
    
    print()
    print("=" * 80)
    print("✅ 批量分析完成！")
    print("=" * 80)
    print()
    print("📁 查看结果:")
    print("  Knowledge/Siemens内容营销策略研究/内容深度分析/")


if __name__ == "__main__":
    main()



