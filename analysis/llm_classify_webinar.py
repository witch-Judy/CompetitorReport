#!/usr/bin/env python3
"""
使用LLM对Unknown类型的Webinar标题进行智能分类
"""

import re
import json
from pathlib import Path
from typing import Dict, List
import sys

# 尝试导入openai，如果没有则使用其他方式
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("⚠️  未安装openai库，将使用模拟分类")

class LLMWebinarClassifier:
    """使用LLM对Webinar标题进行分类"""
    
    def __init__(self):
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        self.information_dir = project_root / "Information"
        
    def classify_with_llm(self, title: str) -> Dict:
        """
        使用LLM对单个标题进行分类
        返回: {'type': 'product|education|technical|mixed', 'reason': '分类原因'}
        """
        if not HAS_OPENAI:
            # 如果没有openai，使用基于规则的fallback
            return self._fallback_classify(title)
        
        try:
            # 构建prompt
            prompt = f"""请分析以下Siemens Webinar标题，判断其内容倾向：

标题: "{title}"

请从以下4个类型中选择最合适的一个：
1. product - 产品用法（演示产品功能、使用方法、实操）
2. education - 科普/教育（介绍概念、趋势、基础知识、行业洞察）
3. technical - 技术深度（深入技术细节、架构、开发、编程）
4. mixed - 混合型（同时包含教育和产品内容）

如果标题是目录页或导航页，返回 "directory"

请以JSON格式返回，格式如下：
{{
    "type": "product|education|technical|mixed|directory",
    "confidence": "high|medium|low",
    "reason": "简要说明分类原因"
}}"""

            # 调用OpenAI API（需要设置API key）
            # 注意：这里需要用户配置OPENAI_API_KEY环境变量
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的B2B内容分类专家，擅长分析工业自动化领域的Webinar标题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=150
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # 尝试解析JSON
            try:
                result = json.loads(result_text)
                return {
                    'type': result.get('type', 'unknown'),
                    'confidence': result.get('confidence', 'medium'),
                    'reason': result.get('reason', '')
                }
            except json.JSONDecodeError:
                # 如果返回的不是JSON，尝试提取类型
                if 'product' in result_text.lower():
                    return {'type': 'product', 'confidence': 'medium', 'reason': 'LLM识别为产品类'}
                elif 'education' in result_text.lower():
                    return {'type': 'education', 'confidence': 'medium', 'reason': 'LLM识别为教育类'}
                elif 'technical' in result_text.lower():
                    return {'type': 'technical', 'confidence': 'medium', 'reason': 'LLM识别为技术类'}
                elif 'mixed' in result_text.lower():
                    return {'type': 'mixed', 'confidence': 'medium', 'reason': 'LLM识别为混合型'}
                else:
                    return {'type': 'unknown', 'confidence': 'low', 'reason': 'LLM无法明确分类'}
        
        except Exception as e:
            print(f"⚠️  LLM分类出错: {e}")
            return self._fallback_classify(title)
    
    def _fallback_classify(self, title: str) -> Dict:
        """基于规则的fallback分类（当没有LLM时使用）"""
        title_lower = title.lower()
        
        # 更智能的规则匹配
        # 产品类关键词（更全面）
        product_indicators = [
            'how to', 'tutorial', 'demo', 'setup', 'configuration',
            'getting started', 'introduction to', 'overview of',
            'features', 'capabilities', 'new', 'update', 'version',
            'v20', 'v19', 'next generation', 'latest', 'whats new',
            'save time', 'standardization', 'service', 'digitales service',
            'comfy', 'dra', 'horaky', 'hydraulika', 'klapkove', 'cidla',
            'aplikacni', 'regulatory', 'rtls', 'pharma', 'solucao',
            'automacao', 'parte', 'integracao', 'inversor', 'controlador'
        ]
        
        # 教育类关键词
        education_indicators = [
            'trends', 'future', 'innovation', 'transformation',
            'strategy', 'best practices', 'insights', 'expert talk',
            'panel', 'discussion', 'webinar series', 'industry',
            'market', 'competitive', 'edge', 'way to', 'artificial intelligence',
            'cybersecurity', 'security', 'nis2', 'endpoint protection',
            'smart power', 'management', 'network security', 'digitale toekomst',
            'redefine', 'eficiencia', 'modelo renovable'
        ]
        
        # 技术类关键词
        technical_indicators = [
            'deep dive', 'advanced', 'expert', 'masterclass',
            'architecture', 'integration', 'development',
            'programming', 'code', 'modeling', 'engineering',
            'digital twin', 'digitaler zwilling', 'vorausgedacht',
            'critical infrastructures', 'reglementation', 'epbd',
            'automatisation', 'intelligent batiment', 'regelgeving',
            'gebouwautomatisering'
        ]
        
        # 检查技术类（优先级最高，因为技术类通常更明确）
        technical_score = sum(1 for ind in technical_indicators if ind in title_lower)
        if technical_score > 0:
            return {'type': 'technical', 'confidence': 'medium', 'reason': f'包含技术类关键词({technical_score}个)'}
        
        # 检查产品类
        product_score = sum(1 for ind in product_indicators if ind in title_lower)
        if product_score > 0:
            return {'type': 'product', 'confidence': 'medium', 'reason': f'包含产品类关键词({product_score}个)'}
        
        # 检查教育类
        education_score = sum(1 for ind in education_indicators if ind in title_lower)
        if education_score > 0:
            return {'type': 'education', 'confidence': 'medium', 'reason': f'包含教育类关键词({education_score}个)'}
        
        # 如果标题很短（≤3个词），可能是产品类（产品名称）
        if len(title_lower.split()) <= 3:
            return {'type': 'product', 'confidence': 'low', 'reason': '标题简短，可能是产品名称'}
        
        # 如果包含数字编号（如Webinar1, Webinar13），可能是产品类
        if re.search(r'webinar\s*\d+', title_lower):
            return {'type': 'product', 'confidence': 'low', 'reason': '包含编号，可能是产品系列'}
        
        return {'type': 'unknown', 'confidence': 'low', 'reason': '无法通过规则匹配'}
    
    def batch_classify(self, titles: List[str], use_llm: bool = False) -> List[Dict]:
        """批量分类标题"""
        results = []
        
        print(f"开始分类 {len(titles)} 个标题...")
        if use_llm and HAS_OPENAI:
            print("使用LLM进行分类...")
        else:
            print("使用规则引擎进行分类...")
        
        for i, title in enumerate(titles, 1):
            if use_llm and HAS_OPENAI:
                result = self.classify_with_llm(title)
            else:
                result = self._fallback_classify(title)
            
            result['title'] = title
            results.append(result)
            
            if i % 10 == 0:
                print(f"  已处理: {i}/{len(titles)}")
        
        return results


def main():
    """主函数 - 对unknown标题进行重新分类"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from analysis.siemens_webinar_deep_analysis import SiemensWebinarDeepAnalyzer
    
    # 提取unknown标题
    analyzer = SiemensWebinarDeepAnalyzer()
    tree_file = analyzer.information_dir / "siemens_analyzed_complete_tree.txt"
    
    webinars = []
    with open(tree_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        if 'webinar' in line.lower():
            title = re.sub(r'[│├─└📄📂\s]+', ' ', line).strip()
            title = re.sub(r'\.html?$', '', title, flags=re.IGNORECASE)
            if title and len(title) > 5:
                webinars.append(title)
    
    # 找出unknown类型
    unknown_titles = []
    for title in webinars:
        classification = analyzer.classify_webinar_type(title.lower())
        if classification['type'] == 'unknown':
            unknown_titles.append(title)
    
    print(f"找到 {len(unknown_titles)} 个unknown标题")
    
    # 使用LLM分类器重新分类
    llm_classifier = LLMWebinarClassifier()
    
    # 检查是否有API key
    use_llm = HAS_OPENAI and hasattr(openai, 'api_key') and openai.api_key
    
    if not use_llm:
        print("⚠️  未检测到OpenAI API key，将使用增强的规则引擎")
        print("   如需使用LLM，请设置环境变量: export OPENAI_API_KEY='your-key'")
    
    results = llm_classifier.batch_classify(unknown_titles, use_llm=use_llm)
    
    # 统计分类结果
    from collections import Counter
    type_counts = Counter(r['type'] for r in results)
    
    print("\n" + "=" * 80)
    print("重新分类结果统计")
    print("=" * 80)
    for type_name, count in type_counts.most_common():
        pct = count / len(results) * 100
        print(f"  {type_name:12s}: {count:3d} ({pct:5.1f}%)")
    
    # 保存结果
    output_file = analyzer.insight_dir / "unknown_webinar_reclassified.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 结果已保存: {output_file}")
    
    return results


if __name__ == "__main__":
    main()

