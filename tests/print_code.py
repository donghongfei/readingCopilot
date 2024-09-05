import os


def print_directory_tree(root_dir, prefix="", output_file=None):
    """打印项目树形结构，忽略指定的目录"""
    for i, (root, dirs, files) in enumerate(os.walk(root_dir)):
        # 忽略指定的目录
        dirs[:] = [d for d in dirs if d not in {'__pycache__', 'venv', '.git', 'run.log', 'tests'}]
        
        # 打印目录结构
        if i == 0:
            line = f"{prefix}{root}/\n"
        else:
            line = f"{prefix}{'|-- ' if prefix else ''}{root[len(root_dir) + 1:]}/\n"
        
        if output_file:
            output_file.write(line)
        else:
            print(line, end='')

        # 打印文件列表，扩展支持 .py 和 .yml 文件
        for file in files:
            if file.endswith('.py') or file.endswith('.yml'):
                line = f"{prefix}|-- {file}\n"
                if output_file:
                    output_file.write(line)
                else:
                    print(line, end='')

def print_python_files_content(root_dir, output_file=None):
    """打印所有 .py 和 .yml 文件的路径、文件名及其内容"""
    for root, _, files in os.walk(root_dir):
        if 'venv' in root or '.git' in root or 'tests' in root:
            continue  # 忽略 venv、.git 和 tests 目录
        for file in files:
            if file.endswith('.py') or file.endswith('.yml'):
                file_path = os.path.join(root, file)
                line = f"\n\n--- File: {file_path} ---\n"
                if output_file:
                    output_file.write(line)
                else:
                    print(line, end='')

                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if output_file:
                        output_file.write(content)
                    else:
                        print(content, end='')

if __name__ == "__main__":
    # 获取当前脚本所在目录的上一级目录，即项目根目录
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 将 code.txt 文件生成在当前脚本所在的目录
    code_output_path = os.path.join(current_dir, "code.txt")
    
    with open(code_output_path, "w", encoding="utf-8") as output_file:
        output_file.write("项目树形结构：\n\n")
        print_directory_tree(project_root, output_file=output_file)
        
        output_file.write("\n\n所有 .py 和 .yml 文件内容：\n\n")
        print_python_files_content(project_root, output_file=output_file)
    
    print(f"代码输出已保存到 {code_output_path} 文件中")