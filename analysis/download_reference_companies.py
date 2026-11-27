#!/usr/bin/env python3
"""
下载参考公司的sitemap文件
这些公司作为参考，用于对比分析
"""

import sys
from pathlib import Path

# 添加analysis目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from find_sitemap_intelligent import IntelligentSitemapFinder


def main():
    """下载参考公司的sitemap"""
    
    # 参考公司列表及其可能的URL
    reference_companies = {
        'stripe': [
            'https://stripe.com',
            'https://www.stripe.com',
        ],
        'samsara': [
            'https://www.samsara.com',
            'https://samsara.com',
        ],
        'palantir': [
            'https://www.palantir.com',
            'https://palantir.com',
        ],
        'apple': [
            'https://www.apple.com',
            'https://apple.com',
        ],
        'tesla': [
            'https://www.tesla.com',
            'https://tesla.com',
        ],
        'xiaomi': [
            'https://www.mi.com',
            'https://www.xiaomi.com',
            'https://mi.com',
        ],
        'huawei': [
            'https://www.huawei.com',
            'https://consumer.huawei.com',
            'https://huawei.com',
        ],
        'BYD': [
            'https://www.byd.com',
            'https://byd.com',
            'https://www.bydglobal.com',
        ],
    }
    
    # 创建参考目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    reference_dir = project_root / "raw_data" / "reference"
    reference_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print("下载参考公司Sitemap")
    print("=" * 80)
    print()
    print(f"参考目录: {reference_dir}")
    print(f"公司数量: {len(reference_companies)}")
    print()
    
    finder = IntelligentSitemapFinder(timeout=15)
    results = {}
    
    for company_name, base_urls in reference_companies.items():
        print(f"\n{'='*80}")
        print(f"处理: {company_name}")
        print(f"{'='*80}")
        
        # 查找sitemap
        sitemap_url = finder.find_sitemap(company_name, base_urls)
        
        if sitemap_url:
            # 下载sitemap
            file_path = finder.download_sitemap(company_name, sitemap_url, reference_dir)
            if file_path:
                results[company_name] = (True, sitemap_url, file_path)
            else:
                results[company_name] = (False, None, None)
        else:
            results[company_name] = (False, None, None)
            print(f"❌ 未找到 {company_name} 的sitemap")
    
    # 打印总结
    print("\n" + "=" * 80)
    print("下载总结")
    print("=" * 80)
    
    success_count = 0
    for company_name, (success, url, file_path) in results.items():
        if success:
            success_count += 1
            file_size = file_path.stat().st_size if file_path else 0
            print(f"✅ {company_name:15s} -> {file_path.name if file_path else 'N/A'}")
            print(f"   URL: {url}")
            print(f"   大小: {file_size:,} 字节")
        else:
            print(f"❌ {company_name:15s} -> 未找到")
        print()
    
    print(f"成功: {success_count}/{len(reference_companies)} 个")
    print()
    
    # 验证下载的文件
    print("=" * 80)
    print("文件验证")
    print("=" * 80)
    
    for company_name, (success, url, file_path) in results.items():
        if success and file_path:
            # 检查文件大小
            file_size = file_path.stat().st_size
            if file_size < 1000:
                print(f"⚠️  {company_name:15s}: 文件过小 ({file_size} 字节)，可能不完整")
            else:
                print(f"✅ {company_name:15s}: {file_size:,} 字节")
    
    print()


if __name__ == "__main__":
    main()



