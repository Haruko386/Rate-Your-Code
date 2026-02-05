import os
import re
from pathlib import Path
from .base import AnalysisResult

class ProjectStructureAnalyzer:
    """
    项目整体结构品鉴师
    不针对单一文件，而是评价整个项目的组织架构
    """
    
    # 标准化文档清单 (加分项/扣分项)
    STANDARD_DOCS = {
        'README.md': 10,       # 门面，必须有
        '.gitignore': 10,      # 工程化标配
        'LICENSE': 5,          # 开源规范
        'CONTRIBUTING.md': 5,  # 协作规范
        'Dockerfile': 5,       # 容器化
        'requirements.txt': 5, # Python 依赖
        'package.json': 5,     # JS 依赖
        'go.mod': 5,           # Go 依赖
        'pom.xml': 5,          # Java 依赖
        'build.gradle': 5      # Java/Android 依赖
    }

    def analyze(self, project_root: Path, all_file_paths: list) -> AnalysisResult:
        score = 60.0 # 基础分，只要项目存在给60
        issues = []
        
        # 获取根目录下的文件和文件夹
        try:
            root_items = os.listdir(project_root)
        except Exception as e:
            return AnalysisResult("项目结构", "Structure", 0, "D", [f"无法访问根目录: {str(e)}"])

        #  1. 文档规范性检查 (Documentation) 
        found_docs = []
        doc_score = 0
        
        # 检查是否存在标准文档 (忽略大小写)
        root_items_lower = {f.lower(): f for f in root_items}
        
        for doc, weight in self.STANDARD_DOCS.items():
            if doc.lower() in root_items_lower:
                doc_score += weight
                found_docs.append(doc)
        
        # 修正分数：如果有 README 和 .gitignore，分数大幅提升
        if 'readme.md' in root_items_lower:
            score += 10
        else:
            score -= 10
            issues.append("📜 门面缺失: 缺少 README.md，就像一家没有招牌的餐厅")

        if '.gitignore' not in root_items_lower:
            score -= 10
            issues.append("🗑️ 垃圾混入: 缺少 .gitignore，容易上传临时文件")
        else:
            score += 5

        # 只要有一些规范文档，就加分
        if len(found_docs) > 2:
            score += 5
        
        #  2. 根目录堆积检测 (Root Clutter) 
        # 统计根目录下的"文件"数量（排除文件夹）
        root_files = [f for f in root_items if (project_root / f).is_file()]
        # 排除掉标准文档后，剩下的杂乱文件
        clutter_files = [f for f in root_files if f.lower() not in root_items_lower]
        
        # 如果根目录下非文档类文件超过 15 个，视为堆积
        if len(clutter_files) > 15:
            score -= 15
            issues.append(f"📦 仓库杂乱: 根目录下堆积了 {len(clutter_files)} 个文件，建议归档到子目录 (src, docs, lib)")
        elif len(clutter_files) > 8:
            score -= 5
            issues.append(f"📦 略显拥挤: 根目录下文件较多，建议整理")

        #  3. 文件命名规范 (Naming Conventions) 
        # 检查所有扫描到的文件
        bad_naming_count = 0
        space_naming_count = 0
        
        for file_path in all_file_paths:
            filename = file_path.name
            
            # 检查空格 (大忌)
            if ' ' in filename:
                space_naming_count += 1
                if space_naming_count <= 5: # 避免刷屏
                    issues.append(f"🏷️ 命名禁忌: '{filename}' 包含空格，可能导致脚本错误")
            
            # 检查特殊字符 (只允许 字母 数字 . - _)
            # 排除掉像 .gitignore 这种以.开头的文件
            if not re.match(r'^[a-zA-Z0-9._-]+$', filename) and not filename.startswith('.'):
                 # 简单放宽一点，允许中文但给警告? 这里先严格一点
                 # 如果包含中文
                 if re.search(r'[\u4e00-\u9fa5]', filename):
                     # 中文文件名在某些系统兼容性不好，提示但不重扣
                     pass 
                 else:
                     # 其他怪异字符
                     pass

        if space_naming_count > 0:
            score -= 10
            issues.append(f"🏷️ 命名不规范: 发现 {space_naming_count} 个文件名包含空格")

        #  4. 命名风格一致性 (Consistency) 
        # 统计 _ 和 - 的使用比例
        snake_case = 0 # my_file.py
        kebab_case = 0 # my-file.py
        
        for file_path in all_file_paths:
            if '_' in file_path.name: snake_case += 1
            if '-' in file_path.name: kebab_case += 1
            
        # 如果两者都大量存在，说明风格分裂
        if snake_case > 5 and kebab_case > 5:
            score -= 5
            issues.append(f"🎨 风格分裂: 混用了 snake_case ({snake_case}) 和 kebab-case ({kebab_case}) 命名")

        # 最终算分
        final_score = max(0, min(100, score))
        
        # 评级文本
        rank = "C"
        if final_score >= 90: rank = "S (完美架构)"
        elif final_score >= 80: rank = "A (工整规范)"
        elif final_score >= 60: rank = "B (尚可)"
        else: rank = "D (杂乱无章)"

        return AnalysisResult(
            file_name="[项目整体结构]", # 特殊标记
            language="Project",
            score=final_score,
            rating=rank,
            issues=issues
        )