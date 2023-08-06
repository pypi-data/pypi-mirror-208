import os
import shutil
from pathlib import Path
import re
import subprocess

asa_home = os.environ.get('ASA_HOME')
dst_folder = asa_home + "\\video_copy"


def cmp4():
    """
    复制执行命令文件夹下所有的mp4文件
    """
    source_dir = Path().parent
    if os.path.exists(dst_folder):
        # 如果目录存在，则删除它
        shutil.rmtree(dst_folder)
    # 创建新的目录
    os.mkdir(dst_folder)
    # 拷贝文件夹下所有mp4文件
    for file in source_dir.glob('*.mp4'):
        shutil.copy(file, dst_folder)
    # 重命名拷贝到文件夹中的文件
    # 遍历文件夹中的所有文件
    for filename in os.listdir(dst_folder):
        # 用正则表达式替换特殊字符
        # 去掉 除了字母、数字、下划线、短横线、点号和空格之外的字符
        new_filename = re.sub('[^\w\-_\. ]', '', filename)
        # 将字符串 new_filename 中的多个空格替换为空，并去掉两端空格
        new_filename = re.sub(' +', '', new_filename).strip()
        # 如果文件名有变化，则重命名文件
        if new_filename != filename:
            os.rename(os.path.join(dst_folder, filename),
                      os.path.join(dst_folder, new_filename))


def createTurnTxt():
    # 生成待转码的文件
    source_dir = Path().parent
    video_files = [f"file '{f.absolute()}'" for f in Path(
        dst_folder).glob('*.mp4')]
    with open(source_dir / "files.txt", "w") as f:
        enter_str = '\n'
        f.write(enter_str.join(video_files))


def turnToMp4(equipment):
    # files_path = Path(asa_home) / "video_copy" / "files.txt"
    files_path = "files.txt"
    if equipment == 'tv':
        codev = "libxvid"
    else:
        codev = "libx264"
    command = f'ffmpeg -f concat -safe 0 -i "{files_path}" -c:v {codev} out.mp4'
    process = subprocess.Popen(    # 启动一个新进程并执行指定的命令。
        command,
        stdout=subprocess.PIPE,   # 将标准输出流重定向到一个管道中。
        stderr=subprocess.STDOUT,  # 将标准错误流重定向到标准输出流中，这样可以保证标准错误信息也被包含在输出流中。
        universal_newlines=True,  # 将输出流转换为字符串类型
        bufsize=1,  # 指定行缓冲模式，每次输出一行
        encoding='utf-8', errors='ignore'
    )
    for line in process.stdout:
        print(line)
