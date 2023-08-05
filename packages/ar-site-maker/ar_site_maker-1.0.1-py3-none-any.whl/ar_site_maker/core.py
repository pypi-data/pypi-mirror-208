import os
import qrcode
import shutil
from pymarker.core import generate_patt, generate_marker
from PIL import Image, ImageOps
from .template import html
from .utlis import *

def make(project_name,glb_path,img=None, url=None,animation=False,site_title=None,scale=1):
    check_args(glb_path,img,url)
    marker_path  = img
    while os.path.exists(project_name) :
        project_name += " copy"
    print("your project is here :", project_name)
    os.mkdir(project_name)

    tmp_dir = f"{project_name}/tmp/"
    os.mkdir(tmp_dir)

    marker_tmp_path = tmp_dir+"marker.png"


    if url is not None:
        print(f"making QR Code.. (Url : {url})")
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)

        # 画像ファイルとして保存する
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(marker_tmp_path)
        # 画像を開く
        img = Image.open(marker_tmp_path)

        # グレースケール画像をRGBに変換
        rgb_img = img.convert("RGB")

        # 変換した画像を保存
        rgb_img.save(marker_tmp_path)


    else :
        with Image.open(marker_path) as im:
            # PNG形式で保存する
            im.save(marker_tmp_path)

    print(f"making pattern file.. (image: {marker_path})")
    marker_output_dir = f"{project_name}/marker"
    os.mkdir(marker_output_dir)
    generate_patt(marker_tmp_path,output=marker_output_dir)
    generate_marker(marker_tmp_path, output=marker_output_dir)

    os.rename(f"{marker_output_dir}/marker_marker.png", f"{marker_output_dir}/marker.png")
    img = Image.open(f"{marker_output_dir}/marker.png")
    padding = 50
    new_img = ImageOps.expand(img, border=padding, fill='white')
    new_img.save(f"{marker_output_dir}/marker_add_padding.png")

    os.mkdir(f"{project_name}/model")
    model_path = f"{project_name}/model/model.glb"
    shutil.copy(glb_path, model_path)

    html_txt = html(project_name if site_title is None else site_title,animation,scale=scale)

    output_html_path = project_name+'/index.html'
    print(f"making html file.. (output: {output_html_path})")
    with open(output_html_path, 'w') as f:
        # 文字列を書き込む
        f.write(html_txt)

    shutil.rmtree(tmp_dir)












