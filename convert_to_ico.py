from PIL import Image
import os

def png_to_ico(png_file, ico_file):
    img = Image.open(png_file)
    # 创建多种尺寸的图标
    icon_sizes = [(16,16), (32,32), (48,48), (64,64), (128,128)]
    img.save(ico_file, sizes=icon_sizes)

# 当前文件夹的logo.png转换为logo.ico
script_dir = os.path.dirname(os.path.abspath(__file__))
png_file = os.path.join(script_dir, "logo.png")
ico_file = os.path.join(script_dir, "logo.ico")
png_to_ico(png_file, ico_file)