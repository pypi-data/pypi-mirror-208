import click
import shutil
from pathlib import Path
import re
from out_dutys import out_duty
import os
from copyallmp4 import cmp4, createTurnTxt, turnToMp4

asa_home = os.environ.get('ASA_HOME')


@click.group()
def cli():
    """
    待完成：
        - 下载进度条，可传递视频传入的格式avi、mp4等
        - 抖音下载并有进度条
        - git管理，更新就自动发布pypi
    """
    pass


@click.command()
@click.argument('source')
def ra(source):
    """
    removeAnnotate  去掉注解
    """
    source = asa_home+"/"+source+'_copy'
    folder_path = Path(source)  # 替换为文件夹实际路径
    files = folder_path.glob("**/*")  # 匹配文件夹下所有文件，包括子目录中的文件
    for file in files:
        file_extension = file.suffix
        if file_extension == '.py':
            with open(file, 'r', encoding='utf-8') as f:
                contents = f.read()
                # (?m)多行匹配  \s匹配空格或制表符  #后匹配空格，为了避免有些md5被去掉
                contents = re.sub(r'(?m)\s*#\s.*\n?', '\n', contents)
                contents = re.sub(
                    r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')', '', contents)
                contents = contents.replace('\n\n', '\n')    # 去掉连续换行
                contents = re.sub(r'^\n', '', contents)      # 去掉换行开头的
            with open(file, 'w', encoding='utf-8') as f:
                f.write(contents)
            print("转换文件", file)  # 打印文件路径


@click.command()
@click.argument('source')
def cf(source):
    """
    copyFolder  复制所有源代码文件到asahome的文件夹下
    """
    src_folder = source
    dst_folder = asa_home+"/"+source+'_copy'
    shutil.copytree(src_folder, dst_folder)


@click.command()
def od():
    """
    调用out_dutys  转换值班为js
    """
    out_duty()


@click.command()
def cp4():
    """
    mp4拷贝到asa_home的环境变量的目录中，并重命名为合法字符
    """
    cmp4()


@click.command()
def ctt():
    """
    mp4目录下文件生成要转换的txt文件
    """
    createTurnTxt()


@click.command()
@click.option('--e', default="pc")
def ttm4(e):
    """
    合并mp4视频，转为h264编码mp4或海信电视可播放的mp4
    equipment ： --e
    """
    turnToMp4(e)


cli.add_command(ra)
cli.add_command(cf)
cli.add_command(od)
cli.add_command(cp4)
cli.add_command(ctt)
cli.add_command(ttm4)
