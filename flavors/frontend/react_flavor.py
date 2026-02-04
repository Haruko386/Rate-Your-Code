import re
from ..base import BaseAnalyzer, AnalysisResult

class ReactAnalyzer(BaseAnalyzer):
    def analyze(self, file_path) -> AnalysisResult:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return AnalysisResult(file_path.name, "React", 0, "D", [f"读取失败: {str(e)}"])

        issues = []
        score = 100.0
        
        # --- 1. 基本语法错误 ---
        # 检查 class vs className
        # 简单的正则，排除注释
        clean_code = re.sub(r'{/\*.*?\*/}', '', content, flags=re.DOTALL) # 去除 JSX 注释
        
        # 查找 <div class="... (在 JSX 中是错误的)
        if re.search(r'<[a-zA-Z]+\s+[^>]*\bclass=["\']', clean_code):
            score -= 10
            issues.append(f"🏷️ 标签贴错: 在 JSX 中使用了 'class' 而非 'className'")

        # --- 2. 样式风味 ---
        # 检查内联样式 style={{ color: 'red' }}
        inline_styles = len(re.findall(r'style=\{\{', clean_code))
        if inline_styles > 3:
            score -= 5
            issues.append(f"🎨 调味不匀: 发现 {inline_styles} 处内联样式 (style={{...}})，建议使用 CSS 类")

        # --- 3. Hooks 使用 ---
        # useEffect 依赖项缺失
        
        # 检查是否直接修改 state (this.state = ... 或 count = count + 1 在 hooks 里)
        # 略难，但在 regex 层面可以检查 "use" 开头的 hook 是否被放在 if 里 (简单的缩进检查)
        lines = content.splitlines()
        for i, line in enumerate(lines):
            stripped = line.strip()
            # 如果一行以 use开头 (如 useEffect)，但缩进大于 4 (假设在 if/for 内部) 且上一行是 if/for
            if re.match(r'use[A-Z]', stripped):
                # 检查是否在循环或条件中 (TODO: 需要更强的 AST，这里仅做提示)
                pass

        # --- 4. 组件复杂度 ---
        # 检查 render 函数或 return JSX 的长度
        if file_path.suffix == '.tsx':
            # TypeScript 特有检查: any 滥用
            any_count = len(re.findall(r':\s*any\b', clean_code))
            if any_count > 3:
                score -= 10
                issues.append(f"🗑️ 食材不明: 滥用 'any' 类型 ({any_count}次)，丧失了 TS 的严谨口感")

        final_score = max(0, min(100, score))
        return AnalysisResult(
            file_name=file_path.name,
            language="React",
            score=final_score,
            rating=self.calculate_rating(final_score),
            issues=issues
        )