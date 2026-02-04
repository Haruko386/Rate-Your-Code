import re
from ..base import BaseAnalyzer, AnalysisResult

class VueAnalyzer(BaseAnalyzer):
    def analyze(self, file_path) -> AnalysisResult:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return AnalysisResult(file_path.name, "Vue", 0, "D", [f"无法展开画卷: {str(e)}"])

        issues = []
        score = 100.0
        
        # --- 1. 架构风格 (Composition API vs Options API) ---
        if '<script setup' in content:
            # 现代风味，加分项（不扣分）
            pass
        elif 'defineComponent' in content or 'export default {' in content:
            # 传统风味，如果混用过多 Options API 可能会扣分
            pass
        
        # --- 2. 模板反模式 (Bad Patterns) ---
        # v-if 和 v-for 同时出现 (Vue 性能杀手)
        # 简单正则：同一行里同时包含 v-if 和 v-for
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if 'v-if=' in line and 'v-for=' in line:
                score -= 10
                issues.append(f"⚔️ 冲突的口感: 第 {i+1} 行同时使用了 v-if 和 v-for (性能大忌)")

        # --- 3. 模板深度 ---
        # 统计 template 标签内的缩进深度
        template_match = re.search(r'<template>(.*?)</template>', content, re.DOTALL)
        if template_match:
            template_content = template_match.group(1)
            max_indent = 0
            for line in template_content.splitlines():
                if line.strip():
                    indent = len(line) - len(line.lstrip())
                    max_indent = max(max_indent, indent)
            
            # 假设2空格或4空格缩进，超过 40 字符的缩进通常意味着 10-20 层
            if max_indent > 40:
                score -= 5
                issues.append(f"🏗️ 摆盘过于繁复: Template 嵌套深度过高 (DOM 树过深)")

        # --- 4. 样式污染 ---
        # 检查是否使用了 scoped
        if '<style' in content and 'scoped' not in content:
            score -= 5
            issues.append(f"🎨 味道串味: Style 标签未使用 'scoped'，可能污染全局样式")

        # --- 5. Props 传递 ---
        # 检查是否透传过多 props (简单的 heuristic)
        if len(re.findall(r'defineProps', content)) == 0 and 'props:' in content:
             # Options API props 检查，如果 props 列表过长
             pass 

        final_score = max(0, min(100, score))
        return AnalysisResult(
            file_name=file_path.name,
            language="Vue",
            score=final_score,
            rating=self.calculate_rating(final_score),
            issues=issues
        )