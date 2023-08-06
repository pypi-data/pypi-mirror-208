# -*- coding: utf-8 -*-
# @Time    : 2023/4/6 23:25
# @Author  : hxq
# @Software: PyCharm
# @File    : pic_code.py
import importlib


def qrcode(text):
    qr_code = importlib.import_module('qrcode')
    qr = getattr(qr_code, "QRCode")(version=1, box_size=10, border=5)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save('qrcode_img.png')


if __name__ == '__main__':
    qrcode("qrcode_img.png")
