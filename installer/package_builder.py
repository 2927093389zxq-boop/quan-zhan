# installer/package_builder.py
import os
import shutil
import json
import zipfile
from datetime import datetime
import uuid
import argparse

def build_distribution_package(output_dir, version, feature_set="standard"):
    """
    构建分发安装包
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建临时目录
    temp_dir = os.path.join(output_dir, "temp")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    # 源代码目录
    src_dir = "."
    
    # 需要包含的文件夹
    include_folders = ["core", "ui", "publishers", "config", "distribution"]
    
    # 需要包含的根目录文件
    include_files = [
        "run_launcher.py",
        "scheduler.py",
        "config.json",
        "requirements.txt",
        "smart_start.bat",
        "README.txt"
    ]
    
    # 需要排除的文件夹或文件
    exclude_patterns = [
        "master_panel",      # 主控面板
        "installer",         # 安装包生成器
        "__pycache__",       # Python缓存
        ".git",              # Git仓库
        ".venv",             # 虚拟环境
        "*.pyc",             # 编译的Python文件
        "data/telemetry",    # 遥测数据
        "license.json"       # 许可证文件
    ]
    
    # 复制文件夹
    for folder in include_folders:
        src_folder = os.path.join(src_dir, folder)
        if os.path.exists(src_folder):
            dst_folder = os.path.join(temp_dir, folder)
            shutil.copytree(
                src_folder, 
                dst_folder,
                ignore=shutil.ignore_patterns(*exclude_patterns)
            )
    
    # 复制根目录文件
    for file in include_files:
        src_file = os.path.join(src_dir, file)
        if os.path.exists(src_file):
            shutil.copy2(src_file, os.path.join(temp_dir, file))
    
    # 创建版本信息文件
    version_info = {
        "version": version,
        "build_date": datetime.now().isoformat(),
        "feature_set": feature_set,
        "distribution_id": str(uuid.uuid4())
    }
    
    with open(os.path.join(temp_dir, "version.json"), "w") as f:
        json.dump(version_info, f, indent=2)
    
    # 创建空的许可证文件
    with open(os.path.join(temp_dir, "license.json.template"), "w") as f:
        json.dump({
            "note": "请将有效的许可证文件替换此文件并重命名为license.json",
            "instructions": "联系软件提供者获取许可证"
        }, f, indent=2)
    
    # 创建ZIP文件
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    zip_filename = f"market_intelligence_{feature_set}_v{version}_{timestamp}.zip"
    zip_path = os.path.join(output_dir, zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, temp_dir))
    
    # 清理临时文件
    shutil.rmtree(temp_dir)
    
    return zip_path

def main():
    parser = argparse.ArgumentParser(description="构建跨境电商智能体分发包")
    parser.add_argument("--output", default="dist", help="输出目录")
    parser.add_argument("--version", default="1.0.0", help="版本号")
    parser.add_argument("--feature-set", default="standard", choices=["standard", "professional", "enterprise"], help="功能集")
    
    args = parser.parse_args()
    
    zip_path = build_distribution_package(
        args.output,
        args.version,
        args.feature_set
    )
    
    print(f"分发包已生成: {zip_path}")

if __name__ == "__main__":
    main()