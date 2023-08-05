import base64
import hashlib
import os
import random
import time
import uuid

from PIL import Image, ImageDraw, ImageFont


def gen_code(noise, len=4):
    # 获取noise的md5,取md5的前4个奇数位字符串作为图片验证码
    md5 = hashlib.md5()
    md5.update(noise.encode('utf-8'))
    md5_str = md5.hexdigest()
    img_code = ""
    for i in range(len):
        img_code += md5_str[i * 2 + 1]
    return img_code


# print(gen_img_code("123456"))

# 根据img_code生成带混淆的图片，返回图片的base64编码
def gen_noise_img(img_code):
    # 生成图片
    # 1.创建画布
    img = Image.new('RGB', (100, 40), color=(255, 255, 255))
    # 2.创建画笔
    draw = ImageDraw.Draw(img, mode='RGB')
    # 3.绘制文字
    font = ImageFont.truetype('Arial.ttf', 30)
    for i in range(len(img_code)):
        draw.text((20 + i * 20, 0), img_code[i], fill=(0, 0, 0), font=font)
    # 4.绘制干扰线
    width = 100
    height = 40
    for i in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill=(0, 0, 0))
    # 5.绘制干扰点
    for i in range(100):
        draw.point([random.randint(0, width), random.randint(0, height)], fill=(0, 0, 0))
    # # 6.保存图片
    path = f'tmp/noise_img_{img_code}.png'

    # 如果不存在tmp文件夹，则创建
    if not os.path.exists('tmp'):
        os.mkdir('tmp')

    img.save(path)
    # 获取本地图片的base64编码
    with open(path, 'rb') as f:
        img = base64.b64encode(f.read())
    # 删除本地图片
    os.remove(path)
    # 7.返回图片的base64编码
    return img.decode('utf-8')

