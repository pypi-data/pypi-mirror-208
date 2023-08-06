# -*- coding: utf-8 -*-
# @Time : 2023/3/31 13:50
# @Author : Zhan Yong
# @System : jk
import os
import shutil
from pathlib import Path
import hashlib
import json
from tqdm import tqdm
import zipfile
from PIL import Image
import psutil
from multiprocessing import Pool, Manager
from pypinyin import pinyin, Style


class LabelmeLoad(object):

    def __init__(self, *args, **kwargs):
        self.parameter = args[0]
        self.group_error_path = ''
        self.out_of_bounds_path = ''
        self.error_path = ''
        # self.pool = multiprocessing.Pool(processes=psutil.cpu_count(logical=False))
        # self.data_paths = multiprocessing.Manager().list()

        # self.jobs = []

    # async def load_data_info(self):
    #     # 在这个方法中执行耗时的操作，例如读取文件、网络请求等
    #     # 并将结果返回给调用者
    #     return None

    def get_dir_currency(self, input_labelme_dir):
        """
        路径加载后，标注输入数据结果封装实现方法
        @param input_labelme_dir: 输入路径形参
        @return:
        """
        data_paths = list()
        print(f'加载labelme数据集并封装数据结构')
        # 将字符串从 UTF-8 编码转换为UTF-8 编码
        # root_path = self.parameter.input_datasets[0].get('input_dir').encode('utf-8').decode('utf-8')
        for root, dirs, files in tqdm(os.walk(input_labelme_dir, topdown=True)):
            for file in files:
                path_name = os.path.join(root, file).replace('\\', '/')
                obj_path = Path(file)  # 初始化路径对象为对象
                if obj_path.suffix in self.parameter.file_formats:
                    # 所有labelme数据集存放规则为：图像必须存放在00.images目录中，图像对应的json文件必须存放在01.labelme中
                    if root.count('00.images') == 1:  # 设计规则，根据图片文件查找json文件，同时根据约定的目录规则封装labelme数据集
                        # print('字符串''中出现了1次')
                        relative_path = os.path.join('..', os.path.basename(root), file)
                        image_dir = root.replace(input_labelme_dir, '').strip('\\/')
                        labelme_dir = os.path.join(image_dir.replace('00.images', '').strip('\\/'), '01.labelme')
                        labelme_file = obj_path.stem + '.json'
                        # input_dir = self.parameter.input_datasets[0].get('input_dir')
                        json_path = os.path.join(input_labelme_dir, labelme_dir, labelme_file)
                        md5_value = self.get_md5_value(path_name)
                        if self.parameter.output_dir:  # 如果有输出路径，则自定义错误输出目录
                            self.group_error_path = os.path.join(self.parameter.output_dir, 'group_error_path')
                            self.out_of_bounds_path = os.path.join(self.parameter.output_dir, 'out_of_bounds_path')
                            self.error_path = os.path.join(self.parameter.output_dir, 'error_path')
                        image = Image.open(path_name)  # 通过PIL模块获取图像宽高
                        data_path = dict(image_dir=image_dir,  # 封装图像目录相对路径，方便后期路径重组及拼接
                                         image_file=file,  # 封装图像文件名称
                                         image_width=image.width,  # 封装图像宽度
                                         image_height=image.height,  # 封装图像高度
                                         labelme_dir=labelme_dir,  # 封装json文件相对目录
                                         labelme_file=labelme_file,  # 封装json文件名称
                                         input_dir=input_labelme_dir,  # 封装输入路径目录
                                         output_dir=self.parameter.output_dir,  # 封装输出路径目录
                                         group_error_path=self.group_error_path,  # 标注分组出错路径
                                         out_of_bounds_path=self.out_of_bounds_path,  # 标注超出图像边界错误路径
                                         error_path=self.error_path,  # 错误数据存放总目录，不分错误类别
                                         http_url=None,  # 封装http对象存储服务访问服务地址
                                         point_number=self.parameter.point_number,
                                         # 封装数据处理类型，包含base_labelme基类和coco基类
                                         data_type=self.parameter.input_datasets[0].get('type'),
                                         labelme_info=None,  # 封装一张图像标注属性信息
                                         background=False,  # 封装一张图像属于负样本还是正样本，默认为负样本即没有任何标注属性
                                         full_path=path_name,  # 封装一张图像绝对路径
                                         json_path=json_path,  # 封装一张图像对应json文件绝对路径
                                         md5_value=md5_value,  # 封装一张图像MD5值，用于唯一性判断
                                         relative_path=relative_path,
                                         # 封装图像使用标注工具读取相对路径，格式为：..\\00.images\\000000000419.jpg
                                         only_annotation=False, )  # 封装是图像还是处理图像对应标注内容的判断条件，默认图片和注释文件一起处理
                        labelme_info = self.load_labelme(data_path)  # 加载json内容
                        data_paths.append(labelme_info)
                    else:
                        print('文件夹目录不符合约定标准，请检查')
                        print(path_name)
        return data_paths

    @staticmethod
    def get_md5_value(path_name):
        """
        获取图像文件MD5值
        :param path_name:
        :return:
        """
        md5_obj = hashlib.md5()
        with open(path_name, 'rb') as f:
            while True:
                data = f.read(1024 * 1024)
                if not data:
                    break
                md5_obj.update(data)
        return md5_obj.hexdigest()

    @staticmethod
    def load_labelme(data_path):
        """
        获取图像文件对应的json文件内容
        :param data_path:
        :return:
        """
        # 组合加载json文件的路径
        labelme_path = os.path.join(data_path['input_dir'], data_path['labelme_dir'], data_path['labelme_file'])
        try:
            with open(labelme_path, 'r', encoding='UTF-8') as labelme_fp:
                data_path['labelme_info'] = json.load(labelme_fp)
                if data_path['labelme_info']['imageData'] is not None:
                    data_path['labelme_info']['imageData'] = None
                if not data_path['labelme_info']['shapes']:
                    data_path['background'] = True
        except Exception as e:
            # 如果没有json文件，读取就跳过，并设置为背景
            if 'No such file or directory' in e.args:
                data_path['background'] = True
                data_path['labelme_file'] = None
            else:  # 如果是其它情况错误（内容为空、格式错误），就删除json文件并打印错误信息
                print(e)
                print(labelme_path)
                # os.remove(labelme_path)
            data_path['background'] = True
        return data_path

    def compress_labelme(self):
        """
        封装压缩对象为字典，注意只对输入目录遍历一次，如果输入目录不对，封装结果就会出错
        :return:
        """
        print(f'封装压缩对象')
        for root, dirs, files in tqdm(os.walk(self.parameter.input_datasets[0].get('input_dir'), topdown=True)):
            zip_data = {}
            for directory in dirs:
                rebuild_input_dir = os.path.join(self.parameter.input_datasets[0].get('input_dir'), directory)
                zipfile_obj = os.path.join(self.parameter.output_dir, directory + '.zip')
                zip_data.update({rebuild_input_dir: zipfile_obj})
            return zip_data

    @staticmethod
    def make_compress(zip_package):
        """
        针对封装好的压缩目录进行迭代写入压缩对象包中
        该算法可以跨平台解压
        :param zip_package:
        """
        print(f'开始压缩')
        for zip_key, zip_value in tqdm(zip_package.items()):
            # zip_value：压缩包名称路径
            os.makedirs(os.path.dirname(zip_value), exist_ok=True)
            with zipfile.ZipFile(zip_value, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zip:  # 创建一个压缩文件对象
                for root, dirs, files in os.walk(zip_key):  # 递归遍历写入压缩文件到指定压缩文件对象中
                    for file in files:
                        file_path = os.path.join(root, file)
                        relative_path = os.path.join(os.path.basename(zip_key), os.path.relpath(file_path, zip_key))
                        # file_path：压缩文件绝对路径，relative_path：压缩文件相对路径，相对于压缩目录
                        zip.write(file_path, relative_path)

    @classmethod
    def get_videos_path(cls, root_dir, file_formats):
        """
        视频帧提取组合路径
        :param root_dir:
        :param file_formats:
        :return:
        """
        # dir_name_list = list()  # 文件夹名称
        # files_name = list()  # 文件名称
        # path_name = list()  # 文件夹路径
        file_path_name = list()  # 文件路径
        for root, dirs, files in os.walk(root_dir, topdown=True):
            dirs.sort()
            files.sort()
            # for dir_name in dirs:
            # if dir_name != '00.images' and dir_name != '01.labelme':
            # dir_name_list.append(dir_name)
            # 遍历文件名称列表
            for file in files:
                # 获取文件后缀
                file_suffix = os.path.splitext(file)[-1]
                # 如果读取的文件后缀，在指定的后缀列表中，则返回真继续往下执行
                if file_suffix in file_formats:
                    # 如果文件在文件列表中，则返回真继续往下执行
                    # files_name.append(file)
                    # path_name.append(root)
                    file_path_name.append(os.path.join(root, file))
        return file_path_name

    def get_multiprocess_dir_currency(self):
        """
        根据空闲CPU核数，使用多进程加载并封装labelme数据集
        使用共享队列进行进程间通信是一种高效且具有可扩展性的方法，能够满足各种不同的并行处理需求。
        """
        multiprocess_data_paths = list()  # 我们创建了一个用于存储处理结果的空列表 multiprocess_data_paths
        # 获取逻辑 CPU 数量
        cpu_count = psutil.cpu_count(logical=True)
        # 获取未使用的 CPU 核心数量
        unused_cpu_count = psutil.cpu_count(logical=False)
        print(f"本计算机上有 {cpu_count} 个逻辑 CPU 核心")
        print(f"未使用的 CPU 核心数量为 {unused_cpu_count}")
        # 我们使用 Manager 对象创建了一个共享的队列 queue，该队列可以安全地在多个进程之间传递数据。
        with Manager() as manager:
            queue = manager.Queue()  # 我们使用了 Queue 对象来在多进程之间传递文件处理结果。
            if unused_cpu_count < 20:
                pool = Pool(processes=unused_cpu_count)
            else:
                pool = Pool(processes=20)  # 如果未使用CPU核数大于20个，则指定默认值
            for root, dirs, files in tqdm(os.walk(self.parameter.input_datasets[0].get('input_dir'), topdown=True)):
                for file in files:
                    path_name = os.path.join(root, file).replace('\\', '/')
                    obj_path = Path(path_name)  # 初始化路径对象为对象
                    if obj_path.suffix in self.parameter.file_formats:  # 异步多进程任务只能是图片路径，否则会存在空进程任务返回，使用文件后缀格式进行过滤
                        # 我们使用 Pool 对象创建了一个进程池，并对于每个文件异步地提交一个文件处理任务。对于每个处理任务，我们使用 callback 参数将处理结果添加到队列中。
                        pool.apply_async(self.process_file, args=(path_name, root, obj_path), callback=queue.put)
            pool.close()
            pool.join()
            # 当所有处理任务完成后，我们进入一个循环，并不断从队列中获取处理结果并将其添加到 result 列表中，直到队列为空。
            while not queue.empty():
                multiprocess_data_paths.append(queue.get())
        return multiprocess_data_paths

    def process_file(self, file_path, root, obj_path):
        """
        异步处理多进程封装文件
        保证子进程的执行不会受到主进程的阻塞
        @param file_path:
        @param root:
        @param obj_path:
        """
        # 所有labelme数据集存放规则为：图像必须存放在00.images目录中，图像对应的json文件必须存放在01.labelme中
        if root.count('00.images') == 1:  # 设计规则，根据图片文件查找json文件，同时根据约定的目录规则封装labelme数据集
            # print('字符串''中出现了1次')
            relative_path = os.path.join('..', os.path.basename(root), obj_path.name)
            image_dir = root.replace(self.parameter.input_datasets[0].get('input_dir'), '').strip('\\/')
            labelme_dir = os.path.join(image_dir.replace('00.images', '').strip('\\/'), '01.labelme')
            labelme_file = obj_path.stem + '.json'
            input_dir = self.parameter.input_datasets[0].get('input_dir')
            json_path = os.path.join(input_dir, labelme_dir, labelme_file)
            md5_value = self.get_md5_value(file_path)
            if self.parameter.output_dir:  # 如果有输出路径，则自定义错误输出目录
                self.group_error_path = os.path.join(self.parameter.output_dir, 'group_error_path')
                self.out_of_bounds_path = os.path.join(self.parameter.output_dir, 'out_of_bounds_path')
                self.error_path = os.path.join(self.parameter.output_dir, 'error_path')
            image = Image.open(file_path)  # 通过PIL模块获取图像宽高
            data_path = dict(image_dir=image_dir,  # 封装图像目录相对路径，方便后期路径重组及拼接
                             image_file=obj_path.name,  # 封装图像文件名称
                             image_width=image.width,  # 封装图像宽度
                             image_height=image.height,  # 封装图像高度
                             labelme_dir=labelme_dir,  # 封装json文件相对目录
                             labelme_file=labelme_file,  # 封装json文件名称
                             input_dir=input_dir,  # 封装输入路径目录
                             output_dir=self.parameter.output_dir,  # 封装输出路径目录
                             group_error_path=self.group_error_path,  # 标注分组出错路径
                             out_of_bounds_path=self.out_of_bounds_path,  # 标注超出图像边界错误路径
                             error_path=self.error_path,  # 错误数据存放总目录，不分错误类别
                             http_url=None,  # 封装http对象存储服务访问服务地址
                             point_number=self.parameter.point_number,
                             # 封装数据处理类型，包含base_labelme基类和coco基类
                             data_type=self.parameter.input_datasets[0].get('type'),
                             labelme_info=None,  # 封装一张图像标注属性信息
                             background=False,  # 封装一张图像属于负样本还是正样本，默认为负样本即没有任何标注属性
                             full_path=file_path,  # 封装一张图像绝对路径
                             json_path=json_path,  # 封装一张图像对应json文件绝对路径
                             md5_value=md5_value,  # 封装一张图像MD5值，用于唯一性判断
                             relative_path=relative_path,
                             # 封装图像使用标注工具读取相对路径，格式为：..\\00.images\\000000000419.jpg
                             only_annotation=False, )  # 封装是图像还是处理图像对应标注内容的判断条件，默认图片和注释文件一起处理
            labelme_info = self.load_labelme(data_path)  # 加载json内容
            return labelme_info
        else:
            print('文件夹目录不符合约定标准，请检查')
            print(file_path)

    def hanzi_to_pinyin(self):
        file_path = list()
        for root, dirs, files in tqdm(os.walk(self.parameter.input_datasets[0].get('input_dir'), topdown=True)):
            for file in files:
                path_name = os.path.join(root, file).replace('\\', '/')
                obj_path = Path(file)  # 初始化路径对象为对象
                if obj_path.suffix in self.parameter.file_formats:
                    # 所有labelme数据集存放规则为：图像必须存放在00.images目录中，图像对应的json文件必须存放在01.labelme中
                    if root.count('00.images') == 1:  # 设计规则，根据00.images目录，做唯一判断
                        if path_name not in file_path:
                            file_path.append(path_name)
        # 重命名路径
        print(f'重命名中文路径为英文开始')
        for rename_dir in tqdm(file_path):
            obj_path = Path(rename_dir)  # 初始化路径对象为对象
            input_dir = self.parameter.input_datasets[0].get('input_dir').replace('\\', '/')
            replace_path = str(obj_path.parent).replace('\\', '/')
            relateve_path = replace_path.replace(input_dir, '').strip('\\/')
            rebuild_output_dir = os.path.join(self.parameter.output_dir, relateve_path)
            rebuild_new_dir = self.convert_path_to_pinyin(rebuild_output_dir)
            labelme_dir = os.path.join(os.path.dirname(rebuild_new_dir), '01.labelme')
            json_file_name = obj_path.stem + '.json'
            src_json_file_path = os.path.join(obj_path.parent.parent, '01.labelme', json_file_name)
            # 创建输出目录
            os.makedirs(labelme_dir, exist_ok=True)
            os.makedirs(rebuild_new_dir, exist_ok=True)
            try:
                shutil.copy(rename_dir, rebuild_new_dir)
                shutil.copy(src_json_file_path, labelme_dir)
            except Exception as e:
                print(f"拷贝 {rename_dir} 失败: {e}")

    @staticmethod
    def convert_path_to_pinyin(path):
        """
        将给定路径中的汉字转换为拼音。
        path: 需要转换的路径。
        """
        # 获取路径的父目录和文件名
        parent_path, filename = os.path.split(path)
        # 将路径中的汉字转换为拼音并拼接成新的路径
        pinyin_list = pinyin(parent_path, style=Style.NORMAL)
        pinyin_path = ''.join([py[0] for py in pinyin_list])  # 提取每个汉字的首字母拼接成新的路径
        new_path = os.path.join(pinyin_path, filename)
        return new_path
