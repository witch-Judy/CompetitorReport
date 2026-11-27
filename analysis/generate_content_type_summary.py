#!/usr/bin/env python3
"""
生成综合内容类型统计表
显示不同公司的不同种类材料的数量，以及网站的总内容数
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List


class ContentTypeSummaryGenerator:
    """内容类型统计生成器"""
    
    def __init__(self):
        """初始化生成器"""
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        
        self.output_data_dir = project_root / "output_data"
        self.knowledge_dir = project_root / "Knowledge"
        
        # 创建输出目录
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_company_content(self, company: str) -> Dict:
        """分析单个公司的内容类型"""
        csv_file = self.output_data_dir / f"{company}_analyzed.csv"
        
        if not csv_file.exists():
            return None
        
        df = pd.read_csv(csv_file)
        
        # 统计内容类型
        content_type_counts = df['content_type'].value_counts().to_dict()
        
        # 总内容数
        total_content = len(df)
        
        return {
            'company': company,
            'total_content': total_content,
            'content_types': content_type_counts
        }
    
    def generate_summary_table(self) -> pd.DataFrame:
        """生成综合统计表"""
        print("=" * 80)
        print("生成综合内容类型统计表")
        print("=" * 80)
        print()
        
        # 获取所有公司
        csv_files = sorted(self.output_data_dir.glob("*_analyzed.csv"))
        companies = [f.stem.replace('_analyzed', '') for f in csv_files]
        
        # 收集所有内容类型
        all_content_types = set()
        company_data = {}
        
        for company in companies:
            result = self.analyze_company_content(company)
            if result:
                company_data[company] = result
                all_content_types.update(result['content_types'].keys())
        
        # 排序内容类型（按常见顺序）
        common_order = ['product', 'company', 'industry', 'blog', 'webinar', 'resource', 
                       'customer_story', 'newsroom', 'legal', 'other']
        ordered_types = []
        for ct in common_order:
            if ct in all_content_types:
                ordered_types.append(ct)
                all_content_types.remove(ct)
        # 添加其他类型
        ordered_types.extend(sorted(all_content_types))
        
        # 构建表格
        rows = []
        for company in companies:
            if company not in company_data:
                continue
            
            data = company_data[company]
            row = {'公司': company, '总内容数': data['total_content']}
            
            # 添加各内容类型的数量
            for content_type in ordered_types:
                count = data['content_types'].get(content_type, 0)
                row[content_type] = count
            
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        # 按总内容数排序
        df = df.sort_values('总内容数', ascending=False)
        
        return df
    
    def save_summary_table(self, df: pd.DataFrame) -> str:
        """保存统计表"""
        # 保存CSV
        csv_file = self.knowledge_dir / "综合内容类型统计表.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"✅ CSV表格已保存: {csv_file}")
        
        # 保存Markdown表格
        md_file = self.knowledge_dir / "综合内容类型统计表.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write("# 综合内容类型统计表\n\n")
            f.write("=" * 80 + "\n\n")
            f.write("**说明**: 本表格显示各公司的不同内容类型数量及总内容数\n\n")
            f.write("=" * 80 + "\n\n")
            
            # 生成Markdown表格
            f.write("## 详细统计表\n\n")
            
            # 表头
            headers = list(df.columns)
            f.write("| " + " | ".join(headers) + " |\n")
            f.write("|" + "|".join(["---"] * len(headers)) + "|\n")
            
            # 数据行
            for _, row in df.iterrows():
                values = []
                for col in headers:
                    val = row[col]
                    if col == '公司':
                        values.append(str(val))
                    elif pd.isna(val) or val == 0:
                        values.append("-")
                    else:
                        values.append(str(int(val)))
                f.write("| " + " | ".join(values) + " |\n")
            
            f.write("\n")
            
            # 统计摘要
            f.write("## 统计摘要\n\n")
            f.write(f"- **总公司数**: {len(df)}\n")
            f.write(f"- **总内容数**: {df['总内容数'].sum():,}\n")
            f.write(f"- **平均每公司内容数**: {df['总内容数'].mean():.0f}\n")
            f.write(f"- **最多内容的公司**: {df.loc[df['总内容数'].idxmax(), '公司']} ({int(df['总内容数'].max()):,}个)\n")
            f.write(f"- **最少内容的公司**: {df.loc[df['总内容数'].idxmin(), '公司']} ({int(df['总内容数'].min()):,}个)\n")
            f.write("\n")
            
            # 各内容类型的统计
            f.write("## 各内容类型统计\n\n")
            content_type_cols = [col for col in df.columns if col not in ['公司', '总内容数']]
            
            for col in content_type_cols:
                total = df[col].sum()
                if total > 0:
                    companies_with_content = len(df[df[col] > 0])
                    f.write(f"### {col}\n\n")
                    f.write(f"- **总数量**: {int(total):,}\n")
                    f.write(f"- **有该类型内容的公司**: {companies_with_content} 个\n")
                    f.write(f"- **平均每公司**: {total/len(df):.0f} 个\n")
                    f.write(f"- **最多**: {df.loc[df[col].idxmax(), '公司']} ({int(df[col].max()):,}个)\n")
                    f.write("\n")
            
            f.write("=" * 80 + "\n")
        
        print(f"✅ Markdown表格已保存: {md_file}")
        
        return str(csv_file)
    
    def generate_summary(self):
        """生成综合统计"""
        df = self.generate_summary_table()
        
        if df is not None and len(df) > 0:
            self.save_summary_table(df)
            
            # 显示预览
            print("\n" + "=" * 80)
            print("表格预览（前10行）")
            print("=" * 80)
            print()
            print(df.head(10).to_string(index=False))
            print()
            
            return df
        else:
            print("❌ 未生成数据")
            return None


def main():
    """主函数"""
    generator = ContentTypeSummaryGenerator()
    generator.generate_summary()
    
    print("\n" + "=" * 80)
    print("✅ 综合内容类型统计表生成完成！")
    print("=" * 80)
    print()
    print("📁 生成的文件:")
    print("  - Knowledge/综合内容类型统计表.csv")
    print("  - Knowledge/综合内容类型统计表.md")


if __name__ == "__main__":
    main()

