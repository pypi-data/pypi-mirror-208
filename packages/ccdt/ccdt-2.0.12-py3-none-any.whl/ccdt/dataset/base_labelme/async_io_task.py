# -*- coding: utf-8 -*-
# @Time : 2023/3/31 15:40
# @Author : Zhan Yong
# @System : jk
from ccdt.dataset.utils import Encoder
import shutil
import json
import os
from pathlib import Path
import argparse
import zipfile

"""
使用异步编程：Python的asyncio模块提供了异步编程的支持，可以在执行IO操作期间允许程序在其他任务中并行执行。
"""


def save_image(image_path, save_images_dir, index):
    """
    拷贝图片
    :param image_path:
    :param save_images_dir:
    :param index:判断是拷贝还是剪切
    """
    # print(image_path)
    try:
        if index is True:  # 剪切
            shutil.move(image_path, save_images_dir)
        else:  # 拷贝
            shutil.copy(image_path, save_images_dir)  # shutil.SameFileError,当同一文件夹拷贝相同文件会出错
    except Exception as e:
        print(e)
        print(image_path)


def save_json(json_path, labelme_info, index):
    """
    重写json文件实现
    :param json_path:
    :param labelme_info:
    :param index:判断是拷贝还是剪切
    """
    # print(json_path)
    try:
        if index is True:  # 剪切
            shutil.move(json_path, labelme_info)
        else:  # 拷贝
            with open(json_path, "w", encoding='UTF-8', ) as labelme_fp:  # 以写入模式打开这个文件
                json.dump(labelme_info, labelme_fp, indent=2, cls=Encoder)
    except Exception as e:
        print(e)
        print(json_path)


def compress_file(rebuild_zip, file_path, relative_path):
    """
    压缩文件实现
    :param rebuild_zip: 压缩包名称路径
    :param file_path: 压缩文件绝对路径
    :param relative_path: 压缩文件相对路径，相对于压缩目录
    """
    with zipfile.ZipFile(rebuild_zip, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zip:
        # print(rebuild_zip)
        # print(file_path)
        # print(relative_path)
        # file_path文件绝对路径，os.path.relpath(file_path, rebuild_dir)为文件相对路径
        zip.write(file_path, relative_path)


class AsyncIoTask(object):
    """
    异步协程IO处理实现类
    参考网址：https://zhuanlan.zhihu.com/p/59621713
    """

    @staticmethod
    async def json_dump(data_info, output_dir, index, custom_label):
        """
        异步协程IO：写json数据到磁盘，拷贝图片数据到磁盘
        :param data_info:图像标注数据集封装
        :param output_dir:输出路径，根据输出路径判断数据集是拷贝一份，还是重写当前这一份的json文件
        :param index:形参，字符串、bool类型
        :param custom_label:自定义标签名称，用于抽取份数时创建目录
        """
        if output_dir:  # 传递输出路径的表示要拷贝数据，不传递表示就在输入路径下重写
            obj_path = Path(data_info.get('image_file'))  # 初始化文件为对象
            # 如果图片名称后缀格式重复多次，就进行重写json文件后保存，重命名图片名称
            if data_info['image_file'].count(obj_path.suffix) >= 2:
                image_file = os.path.join(data_info['input_dir'], data_info['image_dir'], data_info['image_file'])
                if data_info['labelme_file']:
                    labelme_file = os.path.join(data_info['input_dir'], data_info['image_dir'],
                                                data_info['labelme_file'])
                    print(labelme_file)
                print(f'图像数据文件格式存在双后缀：{image_file}  请核对数据')
                # exit()
            else:
                if isinstance(index, argparse.Namespace):
                    image_path = data_info['full_path']  # 针对合并数据集时，原始图像目录被重组后，需要重新指定原始路径
                else:
                    # 定义输出目录后，程序内部不做任何目录改变操作逻辑实现
                    image_path = os.path.join(data_info['input_dir'], data_info['image_dir'], data_info['image_file'])
                if isinstance(output_dir, str) or isinstance(index, bool) \
                        or isinstance(index, str) or isinstance(index, argparse.Namespace):
                    save_images_dir = os.path.join(data_info['output_dir'], data_info['image_dir'])
                    os.makedirs(save_images_dir, exist_ok=True)
                    save_image(image_path, save_images_dir, index)
                    save_labelme_dir = os.path.join(data_info['output_dir'], data_info['labelme_dir'])
                    os.makedirs(save_labelme_dir, exist_ok=True)
                    if data_info['labelme_file']:
                        if index is True:
                            json_path = os.path.join(data_info['input_dir'], data_info['labelme_dir'],
                                                     data_info['labelme_file']).replace("\\", "/")
                            save_json(json_path, save_labelme_dir, index)  # 剪切
                        else:
                            json_path = os.path.join(save_labelme_dir, data_info['labelme_file']).replace("\\", "/")
                            save_json(json_path, data_info['labelme_info'], index)  # 拷贝即重写
                else:  # 人工定义输出目录后，程序自动根据序号、按label标签名称重组目录，逻辑实现
                    if isinstance(index, int) and isinstance(custom_label, str):
                        custom_dir = '{:0>4d}'.format(index) + '_' + custom_label
                        rebuild_dir = os.path.join(data_info['output_dir'], custom_dir)
                        # 重构压缩包名称路径
                        # rebuild_zip = os.path.join(data_info['output_dir'], custom_dir + '.zip')
                        # 重构压缩文件绝对路径
                        # rebuild_zip_relative_filename = os.path.relpath(image_path, data_info['input_dir'])
                        # 重构压缩文件相对路径
                        # rebuild_zip_file_path = os.path.join(rebuild_dir, rebuild_zip_relative_filename)
                        extract_images_dir = os.path.join(rebuild_dir, data_info['image_dir'])
                        os.makedirs(extract_images_dir, exist_ok=True)
                        save_image(image_path, extract_images_dir, False)
                        extract_labelme_dir = os.path.join(rebuild_dir, data_info['labelme_dir'])
                        os.makedirs(extract_labelme_dir, exist_ok=True)
                        # compress_file(rebuild_zip, rebuild_zip_file_path, rebuild_zip_relative_filename)
                        if data_info['labelme_file']:
                            json_path = os.path.join(extract_labelme_dir, data_info['labelme_file']).replace("\\", "/")
                            save_json(json_path, data_info['labelme_info'], False)
                            # 重构压缩文件相对路径
                            # rebuild_zip_relative_filename = os.path.relpath(json_path, rebuild_dir)
                            # compress_file(rebuild_zip, json_path, rebuild_zip_relative_filename)
                    else:
                        print(f'自定义目录格式不符合要求{custom_label}，请输入字符串')
                        exit()
        else:  # 直接重写输入路径下的json文件，不用拷贝一份
            if data_info.get('labelme_info'):
                if data_info['labelme_file']:
                    json_path = os.path.join(data_info['input_dir'], data_info['labelme_dir'],
                                             data_info['labelme_file'])
                    save_json(json_path, data_info['labelme_info'], False)
