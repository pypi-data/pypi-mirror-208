'''
Created on 2023年5月12日

@author: 86139
'''
import shutil 
def install():
    # 获取gradio的安装位置
    import pkg_resources 

    # 指定你的HTML和JS文件的位置 
    html_file_path = pkg_resources.resource_filename('gradiop', 'templates')  
    gradio_path = pkg_resources.resource_filename('gradio','templates') 

    print("gradio_path:",gradio_path)
    print("html_file_path:",html_file_path)
    
    # 复制文件到gradio的安装位置
    shutil.copytree(html_file_path, gradio_path, dirs_exist_ok=True)
    
if __name__ == '__main__':
    print("start")