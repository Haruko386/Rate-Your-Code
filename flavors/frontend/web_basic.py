import re
from ..base import BaseAnalyzer, AnalysisResult

class HtmlAnalyzer(BaseAnalyzer):
    def analyze(self, file_path) -> AnalysisResult:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except: return AnalysisResult(file_path.name, "HTML", 0, "D", ["读取失败"])

        issues = []
        score = 100.0

        # 1. 语义化标签 (Div Soup 检测)
        div_count = content.count('<div')
        semantic_count = sum(content.count(tag) for tag in ['<header', '<footer', '<main', '<article', '<section'])
        
        if div_count > 20 and semantic_count == 0:
            score -= 10
            issues.append(f"🍲 只有汤底: 代码充满了 <div>，缺乏语义化标签 (Header/Main/Footer)")

        # 2. 内联样式
        if 'style="' in content:
            count = content.count('style="')
            score -= 5 * min(count, 4)
            issues.append(f"🎨 乱涂乱画: 发现 {count} 处内联 style 属性")

        return AnalysisResult(file_path.name, "HTML", max(0, score), self.calculate_rating(score), issues)


class CssAnalyzer(BaseAnalyzer):
    def analyze(self, file_path) -> AnalysisResult:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except: return AnalysisResult(file_path.name, "CSS", 0, "D", ["读取失败"])

        issues = []
        score = 100.0

        # 1. !important 滥用
        importants = content.count('!important')
        if importants > 2:
            score -= 5 * importants
            issues.append(f"🌶️ 口感过重: 滥用 !important ({importants}次)，破坏了层叠规则")

        # 2. 嵌套过深 (针对 SCSS 或 LESS)
        selectors = re.findall(r'([^{]+)\{', content)
        for sel in selectors:
            if len(sel.split()) > 5:
                score -= 2
                issues.append(f"🕸️ 选择器过于纠结: '{sel.strip()[:30]}...'")
                break

        return AnalysisResult(file_path.name, "CSS", max(0, score), self.calculate_rating(score), issues)


class JsAnalyzer(BaseAnalyzer):
    def analyze(self, file_path) -> AnalysisResult:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except: return AnalysisResult(file_path.name, "JS", 0, "D", ["读取失败"])

        issues = []
        score = 100.0

        # 1. 变量声明 (var vs let/const)
        var_count = len(re.findall(r'\bvar\s+', content))
        if var_count > 0:
            score -= 5 * min(var_count, 5)
            issues.append(f"🕰️ 陈旧风味: 发现了 {var_count} 处 'var' 声明，建议使用 let/const")

        # 2. Console.log
        if 'console.log' in content:
            score -= 5
            issues.append(f"🗑️ 调试残留: 代码中包含 console.log")

        # 3. 回调地狱 (简单的缩进检测)
        lines = content.splitlines()
        max_indent = 0
        for line in lines:
            indent = len(line) - len(line.lstrip())
            max_indent = max(max_indent, indent)
        
        if max_indent > 40: # 假设4空格，10层
            score -= 15
            issues.append(f"🌀 回调漩涡: 缩进过深，疑似回调地狱")

        return AnalysisResult(file_path.name, "JavaScript", max(0, score), self.calculate_rating(score), issues)