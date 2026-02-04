# Backend
from .python_flavor import PythonAnalyzer
from .cpp_flavor import CppAnalyzer
from .go_flavor import GoAnalyzer
from .java_flavor import JavaAnalyzer
from .csharp_flavor import CsharpAnalyzer

# Frontend
from .frontend.vue_flavor import VueAnalyzer
from .frontend.react_flavor import ReactAnalyzer
from .frontend.web_basic import HtmlAnalyzer, CssAnalyzer, JsAnalyzer

# 注册支持的语言和后缀
REGISTRY = {
    # --- Backend ---
    'python': {
        'extensions': ['.py'],
        'class': PythonAnalyzer
    },
    'cpp': {
        'extensions': ['.cpp', '.cc', '.c', '.cxx', '.h', '.hpp'],
        'class': CppAnalyzer
    },
    'go': {
        'extensions': ['.go'],
        'class': GoAnalyzer
    },
    'java': {
        'extensions': ['.java'],
        'class': JavaAnalyzer
    },
    'csharp': {
        'extensions': ['.cs'],
        'class': CsharpAnalyzer
    },

    # --- Frontend ---
    'vue': {
        'extensions': ['.vue'],
        'class': VueAnalyzer
    },
    'react': {
        'extensions': ['.jsx', '.tsx'], # .tsx 也可以被视为 React
        'class': ReactAnalyzer
    },
    'html': {
        'extensions': ['.html', '.htm'],
        'class': HtmlAnalyzer
    },
    'css': {
        'extensions': ['.css', '.scss', '.less', '.sass'],
        'class': CssAnalyzer
    },
    'javascript': {
        'extensions': ['.js', '.mjs', '.ts'], # .ts 暂时用 JS 分析器或复用 React 分析器
        'class': JsAnalyzer
    }
}

def get_analyzer_for_file(file_path, target_language=None):
    """
    根据文件后缀和用户指定的目标语言，返回对应的分析器实例。
    """
    ext = file_path.suffix.lower()

    for lang, config in REGISTRY.items():
        # 如果用户指定了语言，且当前遍历到的语言不匹配，则跳过
        if target_language and lang != target_language:
            continue
            
        if ext in config['extensions']:
            return config['class']()
    
    return None