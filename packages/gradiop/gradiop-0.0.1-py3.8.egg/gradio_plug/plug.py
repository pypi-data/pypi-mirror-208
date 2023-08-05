'''
Created on 2023年5月12日

@author: 86139
'''
def install():
    import os ,shutil
    # 获取gradio的安装位置
    import gradio,gradio_plug
    gradio_path = os.path.dirname(gradio.__file__)
    gradio_plug_path = os.path.dirname(gradio_plug.__file__)

    # 获取你的HTML和JS文件的位置
    html_file_path = os.path.join(gradio_plug_path, 'templates')

    # 复制文件到gradio的安装位置
    shutil.copytree(html_file_path, gradio_path, dirs_exist_ok=True)
