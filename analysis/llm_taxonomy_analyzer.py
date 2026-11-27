#!/usr/bin/env python3
"""
LLM Taxonomy Intelligence Analyzer
使用LLM对Taxonomy Intelligence分析结果进行深度解读
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional
import concurrent.futures
import sys

sys.path.insert(0, str(Path(__file__).parent))


class LLMTaxonomyAnalyzer:
    """LLM分类情报分析器"""
    
    def __init__(self):
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        
        self.insight_dir = project_root / "insight"
        self.company_reports_dir = self.insight_dir / "reports" / "company_reports"
    
    def call_llm_for_analysis(self, prompt: str, company_name: str) -> str:
        """
        调用LLM进行分析
        这里使用OpenAI API，也可以替换为其他LLM服务
        """
        try:
            import openai
            
            # 检查是否有API key
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                # 如果没有API key，返回占位符
                return f"""
## LLM深度分析（需要配置OPENAI_API_KEY）

**提示**: 要启用LLM深度分析，请设置环境变量 OPENAI_API_KEY

**分析提示词已生成**，包含以下内容：
- 执行漏洞分析
- 竞争机会识别
- 战略洞察总结

如需启用，请运行：
```bash
export OPENAI_API_KEY='your-api-key'
python3 analysis/taxonomy_intelligence_analyzer.py --use-llm
```
"""
            
            client = openai.OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model="gpt-4o",  # 或使用 gpt-4-turbo-preview
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位资深的竞争情报分析师，擅长通过网站结构分析企业的业务成熟度、数字化执行力和GTM策略。你的分析要深入、具体、可执行。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            return response.choices[0].message.content
            
        except ImportError:
            return """
## LLM深度分析（需要安装openai库）

**提示**: 要启用LLM深度分析，请先安装openai库：

```bash
pip install openai
export OPENAI_API_KEY='your-api-key'
python3 analysis/taxonomy_intelligence_analyzer.py --use-llm
```
"""
        except Exception as e:
            return f"""
## LLM深度分析（调用失败）

**错误**: {str(e)}

**提示**: 请检查：
1. OPENAI_API_KEY 是否正确设置
2. 网络连接是否正常
3. API配额是否充足
"""
    
    def generate_analysis_with_llm(self, analysis_data: Dict) -> str:
        """生成LLM分析"""
        from analysis.taxonomy_intelligence_analyzer import TaxonomyIntelligenceAnalyzer
        
        analyzer = TaxonomyIntelligenceAnalyzer()
        company_name = analysis_data['company_info']['name']
        
        prompt = analyzer.generate_llm_analysis_prompt(company_name, analysis_data)
        
        return self.call_llm_for_analysis(prompt, company_name)
    
    def enhance_all_reports(self):
        """增强所有报告，添加LLM分析"""
        print("=" * 80)
        print("LLM深度分析增强")
        print("=" * 80)
        print()
        
        # 找到所有报告文件
        report_files = list(self.company_reports_dir.glob("*_Taxonomy_Intelligence_分析报告.md"))
        
        print(f"找到 {len(report_files)} 份报告\n")
        
        # 重新运行分析并添加LLM
        from analysis.taxonomy_intelligence_analyzer import TaxonomyIntelligenceAnalyzer
        
        analyzer = TaxonomyIntelligenceAnalyzer()
        
        # 找到所有complete_tree文件
        tree_files = list(analyzer.information_dir.glob("*_analyzed_complete_tree.txt"))
        company_keys = [f.stem.replace('_analyzed_complete_tree', '') for f in tree_files]
        
        # 并行分析
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_company = {
                executor.submit(analyzer.analyze_company, company_key): company_key 
                for company_key in company_keys
            }
            
            for future in concurrent.futures.as_completed(future_to_company):
                company_key = future_to_company[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    print(f"  ❌ {company_key} 分析失败: {e}")
        
        print()
        print("调用LLM进行深度分析...")
        
        # 并行调用LLM
        enhanced_results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_result = {
                executor.submit(self.generate_analysis_with_llm, result): result
                for result in results
            }
            
            for future in concurrent.futures.as_completed(future_to_result):
                result = future_to_result[future]
                try:
                    llm_insights = future.result()
                    result['llm_insights'] = llm_insights
                    enhanced_results.append(result)
                    print(f"  ✅ {result['company_info']['name']} LLM分析完成")
                except Exception as e:
                    print(f"  ❌ {result['company_info']['name']} LLM分析失败: {e}")
                    enhanced_results.append(result)
        
        print()
        print("更新报告...")
        
        # 重新生成报告
        for analysis_data in enhanced_results:
            llm_insights = analysis_data.get('llm_insights')
            report_file = analyzer.generate_report(analysis_data, llm_insights)
            print(f"  ✅ {analysis_data['company_info']['name']}: {report_file.name}")
        
        print()
        print("=" * 80)
        print("LLM增强完成")
        print("=" * 80)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='LLM Taxonomy Intelligence Analyzer')
    parser.add_argument('--use-llm', action='store_true', help='启用LLM深度分析')
    args = parser.parse_args()
    
    if args.use_llm:
        analyzer = LLMTaxonomyAnalyzer()
        analyzer.enhance_all_reports()
    else:
        print("提示: 使用 --use-llm 参数启用LLM深度分析")
        print("需要先设置 OPENAI_API_KEY 环境变量")



