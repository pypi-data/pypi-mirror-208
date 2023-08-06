import glob
from io import BytesIO
from PIL import Image
import streamlit as st
from table_ocr import TableOCR
from common import ocr, pdf2png
import time
import os
import os.path as osp
import shutil
import base64

is_admin = False


def get_binary_file_downloader_html(bin_file, txt):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">{txt}</a>'
    return href


def show_ret(vis_img, json_ret, html, name):
    st.write("---")
    st.write("## Result")
    # if vis_img is not None:
    #     st.image(Image.fromarray(vis_img), caption="Output", use_column_width=True)
    if json_ret != {}:
        st.json(json_ret)
        st.markdown(get_binary_file_downloader_html(f"{name}/result.json", "点击下载json"),
                    unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)
        st.markdown(get_binary_file_downloader_html(f"{name}/result.xlsx", "点击下载excel"),
                    unsafe_allow_html=True)


def batch_process(option):
    # 创建file_uploader组件
    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)
    num_file = len(uploaded_files)
    if num_file > 0:
        start = time.time()
        save_folder = "tmp/batch"
        if os.path.exists(save_folder):
            shutil.rmtree(save_folder)
        os.makedirs(save_folder)

        progress_bar = st.progress(0)
        for i, file in enumerate(uploaded_files):
            name = osp.splitext(file.name)[0]
            bytes_data = file.getvalue()
            if option == 'OCR':
                ocr(name, bytes_data)
                st.markdown(get_binary_file_downloader_html(f"{name}.txt", "点击下载txt"),
                            unsafe_allow_html=True)
            else:
                kie = False
                if option == '信息抽取':
                    kie = True
                table_ocr = TableOCR(kie=kie)
                img = Image.open(BytesIO(bytes_data))
                table_ocr(img, name, is_streamlit=False)
                progress_bar.progress((i + 1) / num_file)

        shutil.make_archive(save_folder, 'zip', save_folder)
        with open(save_folder + ".zip", 'rb') as f:
            bytes = f.read()
            b64 = base64.b64encode(bytes).decode()
            href = f'<a href="data:file/zip;base64,{b64}" download=\'result\'>\
                                    download zip file </a>'
            st.markdown(href, unsafe_allow_html=True)
        total_time = time.time() - start
        print(f"all time: {total_time}")
        print(f"average time: {total_time}/{num_file}={total_time / num_file}")


def process(option):
    # 创建file_uploader组件
    file = st.file_uploader("Choose files (PDF or image)")
    save_folder = "tmp"
    if not osp.exists(save_folder):
        os.makedirs(save_folder)
    if file is not None:
        path = osp.join(save_folder, file.name)
        name, ext = osp.splitext(path)
        bytes_data = file.getvalue()

        if option == 'OCR':
            all_txts = ocr(path, bytes_data, is_streamlit=True)
            st.text(all_txts)
            st.markdown(get_binary_file_downloader_html(f"{name}.txt", "点击下载txt"),
                        unsafe_allow_html=True)
        elif option in ['表格识别', '信息抽取']:
            kie = False
            if option == '信息抽取':
                kie = True
            table_ocr = TableOCR(kie=kie, angle=False, use_pp=False)
            if ext == ".pdf":
                pdf2png(bytes_data, name)
                paths = glob.glob(f"{name}/*.png")
                paths.sort()
                imgs = [Image.open(path).convert('RGB') for path in paths]
            else:
                imgs = [Image.open(BytesIO(bytes_data)).convert('RGB')]
            for i, img in enumerate(imgs):
                if i > 0:
                    name = f"{name}_{i}"
                st.image(img, caption="Input", use_column_width=True)
                html, json_ret, vis_img, warp_img, warp_mask, cells = table_ocr(img, name, is_streamlit=True)
                show_ret(vis_img, json_ret, html, name)

                if is_admin:
                    flag = False
                    if st.button('Fill missing lines', help='Fill missing lines to improve result'):
                        flag = True
                        html, vis_img, cells = table_ocr.fill_lines(warp_img, name, warp_mask)

                    if st.button('Draw template',
                                 help='Draw template to improve result, the template will be used next time'):
                        flag = True
                        html, json_ret, vis_img = table_ocr.manual_template(warp_img, name, cells)
                    if flag:
                        show_ret(vis_img, json_ret, html, name)


if __name__ == "__main__":
    st.set_page_config(page_title="OCR在线服务")

    # # 背景图片的网址
    # img_url = 'https://img.zcool.cn/community/0156cb59439764a8012193a324fdaa.gif'
    # # 修改背景样式
    # st.markdown('''<style>.css-fg4pbf{background-image:url(''' + img_url + ''');
    # background-size:100% 100%;background-attachment:fixed;}</style>
    # ''', unsafe_allow_html=True)

    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    st.write("# OCR")
    option = st.selectbox('请选择任务', ('OCR', '表格识别', '信息抽取'))
    process(option)
