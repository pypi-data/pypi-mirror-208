#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import gzip
import os
import shutil
from multiprocessing.dummy import Lock

import pandas as pd
import requests
from ykenan_log import Logger
from pandas import DataFrame

'''
 * @Author       : YKenan
 * @Description  : file handler
'''


class Create:
    """
    初始化文件
    """

    def __init__(self, sep='\t',
                 line_terminator="\n",
                 encoding: str = 'utf_8_sig',
                 index: bool = False,
                 header: bool = True,
                 sheet_name='new_sheet',
                 log_file: str = "YKenan_file",
                 is_form_log_file: bool = True):
        """
        Initialization creation information, public information
        :param sep: File Separator
        :param line_terminator: File Line Break
        :param encoding: Document code
        :param index: Whether there is a row index
        :param header: Whether there is a title
        :param sheet_name: sheet name
        :param log_file: Path to form a log file
        :param is_form_log_file: Is a log file formed
        """
        self.log = Logger(name="YKenan file", log_path=log_file, is_form_file=is_form_log_file)
        self.sep = sep
        self.line_terminator = line_terminator
        self.encoding = encoding
        self.index = index
        self.header = header
        self.sheet_name = sheet_name

    def to_file(self, df: DataFrame, file: str) -> None:
        """
        :param df: DataFrame
        :param file: File path plus name
        """
        self.log.debug(f"create a file: {file}")
        # 导出文件
        if str(file).endswith(".txt") or str(file).endswith(".bed"):
            df.to_csv(file, sep=self.sep, lineterminator=self.line_terminator, header=self.header, encoding=self.encoding, index=self.index)
        elif str(file).endswith(".csv"):
            df.to_csv(file, sep=',', lineterminator=self.line_terminator, header=self.header, encoding=self.encoding, index=self.index)
        elif str(file).endswith(".xls") or str(file).endswith(".xlsx"):
            df.to_excel(file, sheet_name=self.sheet_name, header=self.header, index=self.index)
        else:
            with open(file, 'w', encoding='UTF-8') as f:
                df.to_string(f)

    def rename(self, df: DataFrame, columns: list, output_file: str = None) -> None:
        """
        Modify the file column name
        :param df: source document
        :param columns: New column name
        :param output_file: Output file path
        :return:
        """
        # 重新命名
        self.log.debug(f"Modify the file column name: {columns}")
        df.columns = columns
        # 保存
        if output_file is not None:
            self.to_file(df, output_file)

    def drop_columns(self, df: DataFrame, columns: list, output_file: str = None) -> None:
        """
        Delete File Column Name
        :param df: source document
        :param columns: 删除的列名
        :param output_file: Output file path
        :return:
        """
        # 删除列
        self.log.debug(f"删除文件列名: {columns}")
        df.drop(columns, axis=1, inplace=True)
        # 保存文件
        if output_file is not None:
            self.to_file(df, output_file)

    def add_content(self, df: DataFrame, list_content: list, columns=None, is_log: bool = False, output_file: str = None) -> None:
        """
        向创建的文件添加内容
        :param df: DataFrame
        :param list_content: 一列的内容信息, 数组形式
        :param columns: 列信息
        :param output_file: Output file path
        :param is_log: 是否打印 log
        :return:
        """
        # 添加内容
        if columns is None:
            columns: list = list(df.columns)
        if is_log:
            self.log.debug(f"添加内容 {list_content} ...")
        df.loc[len(df)] = pd.Series(list_content, index=columns)
        # 保存文件
        if output_file is not None:
            self.to_file(df, output_file)

    def add_difference_column(self, df: DataFrame, column: str, a: str, b: str, output_file: str = None) -> None:
        """
        添加一个减法列 (column = a - b)
        :param df: DataFrame
        :param column: 添加的一个新列名
        :param a: 被减数
        :param b: 减数
        :param output_file: Output file path
        :return:
        """
        self.log.debug(f"添加一个减法列: {column}")
        df[column] = df[a] - df[b]
        # 保存文件
        if output_file is not None:
            self.to_file(df, output_file)

    def add_rank_group_by(self, df: DataFrame, group: list, column: str, output_file: str = None) -> None:
        """
        添加五个 rank 列
        :param df: DataFrame
        :param group: 分组的列
        :param column: 需要秩的列
        :param output_file: Output file path
        :return:
        """
        self.log.debug(f"添加五个 rank 列: {group}, {column}")
        # 添加排名
        for method in ['average', 'min', 'max', 'dense', 'first']:
            df[f'{method}_rank'] = df.groupby(group)[column].rank(method)
        # 保存文件
        if output_file is not None:
            self.to_file(df, output_file)

    def sum_group_by(self, df: DataFrame, group: list, column: str, output_file: str = None) -> DataFrame:
        """
        通过分组计算某列数总和
        :param df: DataFrame
        :param group: 分组的列
        :param column: 需要和的列
        :param output_file: Output file path
        :return:
        """
        # 总和
        self.log.debug(f"通过分组计算某列数总和: {group}, {column}")
        column_sum = df.groupby(group)[column].sum().reset_index()
        new_column = group.copy()
        new_column.append(f"{column}_sum")
        column_sum.columns = new_column
        # 保存文件
        if output_file is not None:
            self.to_file(column_sum, output_file)
        return column_sum

    def count_group_by(self, df: DataFrame, group: list, column: str, output_file: str = None) -> DataFrame:
        """
        通过分组计算某列数数量
        :param df: DataFrame
        :param group: 分组的列
        :param column: 需要数量的列
        :param output_file: Output file path
        :return:
        """
        # 总和
        self.log.debug(f"通过分组计算某列数总和: {group}, {column}")
        column_sum = df.groupby(group)[column].count().reset_index()
        group.append(f"{column}_count")
        column_sum.columns = group
        # 保存文件
        if output_file is not None:
            self.to_file(column_sum, output_file)
        return column_sum

    def calculation_group_by(self, df: DataFrame, group: list, column: str, on: str, output_file: str = None, add_merge_files: list = None) -> DataFrame:
        """
        通过分组进行一系列数值计算
        :param df: DataFrame
        :param group: 分组的列
        :param column: 需要秩的列
        :param on: 合并的列
        :param output_file: Output file path
        :param add_merge_files: 添加 merge 文件
        :return:
        """
        # 总和
        self.log.debug(f"通过分组进行一系列数值计算: {group}, {column}")
        # 个数大小
        column_size = df.groupby(group)[column].size().reset_index()
        new_column = group.copy()
        new_column.append(f"{column}_size")
        column_size.columns = new_column
        # 平均值
        column_mean = df.groupby(group)[column].mean().reset_index()
        new_column = group.copy()
        new_column.append(f"{column}_mean")
        column_mean.columns = new_column
        # 方差 (size == 1 的值为 NaN)
        column_var = df.groupby(group)[column].var().reset_index()
        new_column = group.copy()
        new_column.append(f"{column}_var")
        column_var.columns = new_column
        # 标准误差 (size == 1 的值为 NaN)
        column_sem = df.groupby(group)[column].sem().reset_index()
        new_column = group.copy()
        new_column.append(f"{column}_sem")
        column_sem.columns = new_column
        # 标准偏差 (size == 1 的值为 NaN)
        column_std = df.groupby(group)[column].std().reset_index()
        new_column = group.copy()
        new_column.append(f"{column}_std")
        column_std.columns = new_column
        # 中位数值
        column_median = df.groupby(group)[column].median().reset_index()
        new_column = group.copy()
        new_column.append(f"{column}_median")
        column_median.columns = new_column
        # 最小值
        column_min = df.groupby(group)[column].min().reset_index()
        new_column = group.copy()
        new_column.append(f"{column}_min")
        column_min.columns = new_column
        # 最大值
        column_max = df.groupby(group)[column].max().reset_index()
        new_column = group.copy()
        new_column.append(f"{column}_max")
        column_max.columns = new_column
        # 总和
        column_sum = self.sum_group_by(df, group, column)
        # 乘积
        column_prod = df.groupby(group)[column].prod().reset_index()
        new_column = group.copy()
        new_column.append(f"{column}_prod")
        column_prod.columns = new_column
        # 保存文件
        all_merge_files: list = [column_size, column_mean, column_var, column_sem, column_std,
                                 column_median, column_min, column_max, column_sum, column_prod]

        if output_file is not None:
            if add_merge_files is not None:
                all_merge_files.extend(add_merge_files)
                return self.merge_files(all_merge_files, on=on, output_file=output_file)
            else:
                return self.merge_files(all_merge_files, on=on, output_file=output_file)

    def merge_files(self, files: list, on: str, output_file: str = None) -> DataFrame:
        """
        将文件进行合并
        :param files: 多个文件
        :param on: 关键 key
        :param output_file: Output file path
        :return:
        """
        # 总和
        size = len(files)
        self.log.debug(f"将文件进行合并: {size}, {on}")
        new_file = files[0]
        i = 1
        while i < size:
            self.log.debug(f"将文件进行合并第 {i} 次")
            new_file = pd.merge(new_file, files[i], on=on)
            i += 1
        # 保存文件
        if output_file is not None:
            self.to_file(new_file, output_file)
        return new_file


class Read:
    """
    Read file content
    """

    def __init__(self, sep='\t',
                 line_terminator="\n",
                 encoding: str = "utf-8",
                 orient: str = "records",
                 lines: bool = True,
                 header="infer",
                 sheet_name=0,
                 low_memory: bool = False,
                 log_file: str = "ykenan_file",
                 is_form_log_file: bool = True):
        """
        Read file initialization information, public information
        :param sep: file separator
        :param line_terminator: file line break
        :param encoding: file encoding
        :param orient: Indicates the expected JSON string format, which is valid only when reading a json file
        :param lines: Read the file as a json object per line
        :param header: The first row header situation
        :param sheet_name: Specify the sheet number when reading Excel
        :param low_memory: Process files in internal chunks to reduce memory usage during parsing
        :param log_file: Path to form a log file
        :param is_form_log_file: Is a log file formed
        """
        self.log = Logger(name="YKenan file", log_path=log_file, is_form_file=is_form_log_file)
        self.sep = sep
        self.line_terminator = line_terminator
        self.encoding = encoding
        self.orient = orient
        self.lines = lines
        self.header = header
        self.sheet_name = sheet_name
        self.low_memory = low_memory

    def get_content(self, file: str):
        """
        Get file content
        :param file: File path information
        :return:
        """
        self.log.debug(f"Start reading {file} file...")
        if str(file).endswith(".txt") or str(file).endswith(".bed"):
            return pd.read_table(file, sep=self.sep, header=self.header, encoding=self.encoding, low_memory=self.low_memory)
        elif str(file).endswith(".csv"):
            return pd.read_csv(file, sep=',', header=self.header, encoding=self.encoding, low_memory=self.low_memory)
        elif str(file).endswith(".xls") or str(file).endswith(".xlsx"):
            return pd.read_excel(file, sheet_name=self.sheet_name, header=self.header if isinstance(self.header, int) else 0)
        elif str(file).endswith(".html") or str(file).endswith(".htm"):
            return pd.read_html(file, header=self.header, encoding=self.encoding)
        elif str(file).endswith(".json"):
            return pd.read_json(file, orient=self.orient, lines=self.lines, encoding=self.encoding)

    def read_file(self, *files):
        """
        Read multiple files
        :param files:
        :return:
        """
        files_return = []
        for file in files:
            files_return.append(self.get_content(file))
        return files_return

    def file_concat_output(self, *files, output_file, join="inner", index=False, encoding="utf_8_sig"):
        """
        Merge two files and export the file
        :param files:
        :param output_file:
        :param join: How to merge files
        :param index:
        :param encoding: Encoding of output files
        :return:
        """
        file_content = self.read_file(*files)
        self.log.debug(f"Start merging files {files} ...")
        pd_concat = pd.concat(file_content, join=join, ignore_index=True)
        pd.DataFrame(pd_concat).to_csv(output_file, encoding=encoding, sep=self.sep, index=index)


class StaticMethod:
    """
    文件或者路径的静态方法
    """

    def __init__(self, log_file: str = "YKenan_file", is_form_log_file: bool = True):
        """
        :param log_file: Path to form a log file
        :param is_form_log_file: Is a log file formed
        """
        self.log = Logger(name="YKenan file", log_path=log_file, is_form_file=is_form_log_file)

    def read_file_line(self, path: str, mode: str = 'r', encoding: str = "utf-8") -> list:
        """
        Read file by line
        :param path:
        :param mode:
        :param encoding:
        :return:
        """
        content = []
        self.log.info(f"Start reading file {path}")
        with open(path, mode, encoding=encoding) as f:
            while True:
                line = f.readline().strip()
                content.append(line)
                if not line:
                    break
        return content

    def write_file_line(self, path: str, content: list, line: str = '\n', mode: str = 'a', encoding: str = "utf-8") -> None:
        """
        Write a file (write by line, and it will not be cleared if the original file is called again by default)
        :param path:
        :param content:
        :param line:
        :param mode:
        :param encoding:
        :return:
        """
        self.log.info(f"Start writing file {path}")
        with open(path, mode, encoding=encoding) as f:
            for li in content:
                f.write(li + line)

    def read_write_line(self, path: str, output: str, callback, column=None, rm: str = 'r', om: str = 'w',
                        encoding: str = "utf-8", buffering: int = 1, newline: str = "\n") -> None:
        """
        Write one file to another
        :param column: Output column name
        :param path: Enter a path
        :param output: output path
        :param callback: A callback function that returns the input data
        :param rm: Read mode
        :param om: Output mode
        :param encoding: encoding
        :param buffering: Number of loaded lines in the output file
        :param newline: The newline character of the output file
        :return:
        """
        with open(output, om, encoding=encoding, buffering=buffering, newline=newline) as w:
            with open(path, rm, encoding=encoding) as f:
                if column:
                    name: str = "\t".join(column)
                    self.log.debug(f"Add Column Name: {name}")
                    w.write(f"{name}\n")
                while True:
                    line: str = f.readline().strip()
                    if not line:
                        break
                    new_line: list = callback(line)
                    if new_line and len(new_line) != 0 and new_line != "":
                        content = "\t".join(new_line)
                        w.write(f"{content}\n")

    def get_contents(self, path: str) -> list:
        """
        Obtain all files and folders under the specified path
        :param path: path
        :return: files and folders
        """
        self.log.info("Starting to retrieve content under this path")
        return list(os.listdir(path))

    def entry_contents(self, path: str, type_: int = 0) -> list:
        """
        Obtain all files and (or) folders under the specified path
        :param path: path
        :param type_: judge file or dir
        :return: files and (or) folders
        """
        self.log.info("Starting to retrieve content under this path")
        contents: list = []
        with os.scandir(path) as it:
            for entry in it:
                entry: os.DirEntry
                if type_ == 0:
                    contents.append(entry.name)
                elif type_ == 1 and entry.is_file():
                    contents.append(entry.name)
                elif type_ == 2 and entry.is_dir():
                    contents.append(entry.name)
                else:
                    raise ValueError("type input error, type is 0 or 1 or 2.")
        return contents

    def entry_contents_path(self, path: str, type_: int = 0) -> list:
        """
        Obtain all files and (or) folders under the specified path
        :param path: path
        :param type_: judge file or dir
        :return: files and (or) folders path
        """
        self.log.info("Starting to retrieve content under this path")
        contents: list = []
        with os.scandir(path) as it:
            for entry in it:
                entry: os.DirEntry
                if type_ == 0:
                    contents.append(entry.path)
                elif type_ == 1:
                    if entry.is_file():
                        contents.append(entry.path)
                elif type_ == 2:
                    if entry.is_dir():
                        contents.append(entry.path)
                else:
                    raise ValueError("type input error, type is 0 or 1 or 2.")
        return contents

    def get_files(self, path: str) -> list:
        """
        Obtain all files in the specified path
        :param path:  path
        :return: files
        """
        self.log.info("Starting to retrieve files under this path")
        files: list = []
        with os.scandir(path) as it:
            for entry in it:
                entry: os.DirEntry
                if entry.is_file():
                    files.append(entry.name)
        return files

    def get_files_path(self, path: str) -> list:
        """
        Obtain all files in the specified path
        :param path:  path
        :return: files
        """
        self.log.info("Starting to retrieve files under this path")
        files: list = []
        with os.scandir(path) as it:
            for entry in it:
                entry: os.DirEntry
                if entry.is_file():
                    files.append(entry.path)
        return files

    def get_dirs(self, path: str) -> list:
        """
        Obtain all files in the specified path
        :param path:  path
        :return: dirs
        """
        self.log.info("Starting to retrieve directories under this path")
        dirs: list = []
        with os.scandir(path) as it:
            for entry in it:
                entry: os.DirEntry
                if entry.is_dir():
                    dirs.append(entry.name)
        return dirs

    def get_dirs_path(self, path: str) -> list:
        """
        Obtain all files in the specified path
        :param path:  path
        :return: dirs
        """
        self.log.info("Starting to retrieve directories under this path")
        dirs: list = []
        with os.scandir(path) as it:
            for entry in it:
                entry: os.DirEntry
                if entry.is_dir():
                    dirs.append(entry.path)
        return dirs

    def entry_contents_dict(self, path: str, type_: int = 0, suffix: str = None) -> dict:
        """
        Obtain all files in the specified path
        :param path: path
        :param type_: type_
        :param suffix: 筛选的条件
        :return: files and (or) dirs
        """
        self.log.info("Starting to retrieve content under this path")
        files: list = []
        dirs: list = []
        contents: list = []
        dict_: dict = {}
        with os.scandir(path) as it:
            for entry in it:
                entry: os.DirEntry
                # 判断是否满足情况
                if suffix is None or entry.name.endswith(suffix):
                    if type_ == 0:
                        contents.append(entry.name)
                        dict_.update({entry.name: entry.path})
                    elif type_ == 1:
                        # 此处判断不能和 type_ == 1 连写，因为需要进行提示 ValueError("type input error, type is 0 or 1 or 2.")
                        if entry.is_file():
                            files.append(entry.name)
                            dict_.update({entry.name: entry.path})
                    elif type_ == 2:
                        if entry.is_dir():
                            dirs.append(entry.name)
                            dict_.update({entry.name: entry.path})
                    else:
                        raise ValueError("type input error, type is 0 or 1 or 2.")
        dict_.update({"name": contents if type_ == 0 else files if type_ == 1 else dirs})
        return dict_

    def entry_files_dict(self, path: str) -> dict:
        """
        Obtain all files in the specified path
        :param path: path
        :return: files
        """
        return self.entry_contents_dict(path, 1)

    def entry_dirs_dict(self, path: str) -> dict:
        """
        Obtain all files in the specified path
        :param path: path
        :return: dirs
        """
        return self.entry_contents_dict(path, 2)

    def unzip_gz(self, gz_file: str, generate_file: str = None, is_force: bool = False) -> list:
        if generate_file:
            if os.path.exists(generate_file) and is_force:
                self.log.warn(f"{generate_file} The file already exists, it has been moved by default")
            else:
                self.log.info(f"Start unzip file {gz_file}")
                w = open(generate_file, 'wb')
                f = gzip.open(gz_file, 'rb')
                read = f.read()
                # Form a file
                w.write(read)
                # Obtaining Content Information
                file_content: list = read.decode().rstrip().split("\n")
                f.close()
                w.close()
                self.log.info(f"End of unzip file  {gz_file}")
                return file_content
        f = gzip.open(gz_file, 'rb')
        # Obtaining Content Information
        file_content: list = f.read().decode().rstrip().split("\n")
        f.close()
        return file_content

    def download_file(self, url: str, filename: str, chunk_size: int = 1024, is_force: bool = False):
        """
        download file
        :param url: 下载的 url
        :param filename: 下载后的文件名
        :param chunk_size: 下载流的大小
        :param is_force: 是否强制覆盖
        :return:
        """
        if os.path.exists(filename) and is_force:
            self.log.warn(f"{filename} The file already exists, it has been downloaded by default")
        else:
            self.log.info(f"下载 {url} 文件")
            response_data_file = requests.get(url, stream=True)
            self.log.info(f"创建 {filename} 文件")
            with open(filename, 'wb') as f:
                for chunk in response_data_file.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
            self.log.info(f"下载 {url} ===> {filename} 文件完成")

    def copy_file(self, source_file: str, target_file: str, is_force: bool = False) -> None:
        """
        复制文件
        :param source_file: 源文件
        :param target_file: 目标文件
        :param is_force: 是否强制覆盖
        :return:
        """
        if os.path.exists(target_file) and is_force:
            self.log.warn(f"{target_file} The file already exists, it has been copied by default")
        else:
            self.log.info(f"Start copying file {source_file}")
            shutil.copy(source_file, target_file)
            self.log.info(f"End of copying file  {source_file}")

    def move_file(self, source_file: str, target_file: str, is_force: bool = False) -> None:
        """
        移动文件
        :param source_file: 源文件
        :param target_file: 目标文件
        :param is_force: 是否强制覆盖
        :return:
        """
        if os.path.exists(target_file) and is_force:
            self.log.warn(f"{target_file} The file already exists, it has been moved by default")
        else:
            self.log.info(f"Start moving file {source_file}")
            shutil.move(source_file, target_file)
            self.log.info(f"End of moving file  {source_file}")

    def makedirs(self, dirs: str, is_lock: bool = False):
        lock = Lock()
        if is_lock:
            lock.locked()
        if not os.path.exists(dirs):
            self.log.info(f"创建 {dirs} 文件夹")
            os.makedirs(dirs)
        if is_lock:
            lock.release()
