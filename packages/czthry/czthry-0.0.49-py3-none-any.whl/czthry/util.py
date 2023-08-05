from datetime import datetime
import json
import re
import os
import requests
import shutil
import time
import traceback
import sys
import inspect
import os, xlsxwriter


def parse_arguments():
    '''
    获取命令行参数
    参数名需要带前缀`--`
    如果没有参数值，则值默认为True
    如果有多个参数值，则值为list，[参数值1, 参数值2, ...]
    '''
    PARAM_PREFIX = '--'
    args = sys.argv[1:]
    if not args:
        return {}
    result = {}
    key = None
    while True:
        arg = args.pop(0) # 从头部取出一个参数
        if arg.startswith(PARAM_PREFIX):
            key = arg[len(PARAM_PREFIX):]
            result[key] = True
        else:
            if key:
                value = result.get(key)
                if type(value) == bool:
                    result[key] = arg
                elif value:
                    if type(value) == list:
                        value.append(arg)
                    else:
                        result[key] = [value, arg]
                else:
                    if type(result[key]) is not bool:
                        result[key] = arg
        if not args:
            break
    return result


def jobj(obj) -> str:
    # json对象的格式化文本
    return json.dumps(obj, ensure_ascii=False, indent=2)


def date_str(formatter="%Y-%m-%d %H:%M:%S", date=None) -> str:
    fmt = "{:" + formatter + "}"
    if not date:
        date = datetime.now()
    return fmt.format(date)


def reg_find(exp, text):
    result = re.search(exp, text)
    if not result:
        return None
    ret = result.groups()
    if not ret:
        ret = result.group()
    return ret


def excludeFiles(files, exc=None):
    if exc is None:
        exc = ['.DS_Store', '__pycache__']
    arr = []
    for f in files:
        ok = 1
        for e in exc:
            if e in f:
                ok = 0
                break
        if ok:
            arr.append(f)
    return arr


def getFilesTree(root_path=os.getcwd()):
    folder = root_path.split('/')[-1]
    tree = {folder: []}
    for file_dir, path, files in os.walk(root_path):
        path = excludeFiles(path)
        for p in path:
            tree[folder].append(getFilesTree(os.path.join(file_dir, p)))
        if len(files) > 0:
            files = excludeFiles(files)
            tree[folder].extend(files)
        break
    return tree


def makeDir(path):
    if os.path.exists(path):
        return
    paths = path.split('/')
    for i in range(len(paths)):
        folder = '/'.join(paths[:i + 1])
        if not os.path.exists(folder):
            os.mkdir(folder)
    return path


def saveFile(content, fullpath):
    file_comp = fullpath.split('/')
    if len(file_comp) > 1:
        folder = '/'.join(file_comp[:-1])
        makeDir(folder)
    with open(fullpath, 'w') as file:
        file.write(content)


def saveData(obj, fullpath):
    if obj is None:
        return
    # if type(obj) == list or type(obj) == dict:
    #     if len(obj) == 0:
    #         return
    saveFile(jobj(obj), fullpath)


def loadData(fullpath):
    if not fullpath:
        return None
    if not os.path.exists(fullpath):
        return None
    with open(fullpath, 'r') as file:
        content = file.read()
    try:
        return json.loads(content)
    except Exception as e:
        return None


def requestJson(url):
    text = requests.get(url).text
    return json.loads(text)


def dumps(data):
    return json.dumps(data, ensure_ascii=False, indent=2)


def getFiles(file_path='.'):
    arr = []
    for file_dir, path, files in os.walk(file_path):
        arr = [os.path.join(file_dir, f) for f in files]
        break  # 一级目录
    arr = excludeFiles(arr)
    arr.sort()
    return arr


def hasFile(code, path):
    files = getFiles(path)
    file = '%s/%s.json' % (path, code)
    return file in files


def getByPath(data, paths, default=None, ch='.'):
    if default is None:
        default = []
    keys = paths.split(ch)
    obj = data
    for k in keys:
        if k in obj:
            obj = obj[k]
            if obj is None:
                return default
        else:
            return default
    return obj


def makeFilePath(path):
    arr = path.split('/')
    if len(arr) == 1:
        return
    filepath = os.path.join(*arr[:-1])
    makeDir(filepath)


def copyfile(src, dest):
    makeFilePath(src)
    makeFilePath(dest)
    shutil.copy(src, dest)


class FileTree(object):
    def __init__(self, root_path='.'):
        self.__root_path = root_path
        self.__files = []
        self.__paths = []
        if root_path == '':
            return
        self.__getFileAndFolder()

    def __getFileAndFolder(self):
        for file_dir, path, files in os.walk(self.__root_path):
            path = excludeFiles(path)
            files = excludeFiles(files)
            for p in path:
                t = FileTree(os.path.join(file_dir, p))
                self.__paths.append(t)
            if len(files) > 0:
                arr_files = []
                for file in files:
                    full_name = os.path.join(file_dir, file)
                    tmp = {
                        'name': file,
                        'full_name': full_name,
                        'size': os.path.getsize(full_name),  # bytes
                    }
                    arr_files.append(tmp)
                self.__files.extend(arr_files)
            break

    def __sortFiles(self, files):
        a = []
        b = []
        for f in files[:]:
            if re.findall(r'^\d+', f):
                a.append(f)
            else:
                b.append(f)
        a = sorted(a, key=lambda f: int(re.findall(r'^\d+', f)[0]))
        b = sorted(b, key=lambda f: f)
        return a+b

    def files(self):
        files = [it['name'] for it in self.__files]
        return self.__sortFiles(files)

    def files_full(self):
        files = [it['full_name'] for it in self.__files]
        return self.__sortFiles(files)

    def paths(self):
        arr = [t.root() for t in self.__paths]
        return self.__sortFiles(arr)

    def paths_full(self):
        arr = [t.root_full() for t in self.__paths]
        return self.__sortFiles(arr)

    def get_size(self):
        size = 0
        for p in self.__paths:
            size += p.get_size()
        for f in self.__files:
            size += f.get('size', 0)
        return size

    def cd(self, path):
        for tree in self.__paths:
            if path == tree.root():
                return tree
        return FileTree('')

    def root(self):
        return self.__root_path.split('/')[-1]

    def root_full(self):
        return self.__root_path

    def obj(self):
        arr = []
        arr.extend(self.files())
        for p in self.__paths:
            arr.append({p.root(): p.obj()})
        return arr

    def __str__(self):
        return '%s:\n%s' % (self.root(), dumps(self.obj()))


def get_files(dir):
    arr = []
    for file_dir, path, files in os.walk(dir):
        # arr = [os.path.join(file_dir, f) for f in files]
        arr = files[:]
        break  # 一级目录
    arr = excludeFiles(arr)
    arr.sort()
    return arr


class Progress(object):

    _flag = 0

    @classmethod
    def go(cls, idx, n, msg='', delta=0):
        index = idx + 1
        scale = 1
        if n > 1000:
            scale = 100
        percent = index / n * 100 * scale
        if percent >= cls._flag or index == n:
            cls._flag = cls._flag + delta
            length = len(str(scale))-1
            fmt = '%6.'+str(length)+'f%% - %4d/%4d'
            string = fmt % (percent/scale, index, n), msg
            if index == n:
                cls._flag = 0
            print(*string)


class Retry(object):
    def __init__(self, func, args=(), xargs=(), kwargs={}, retry=3, delay=60, default=None, error_callback=None):
        """
        对方法进行重试
        :param func: 需要重试的方法
        :param args: 方法携带的参数
        :param xargs: 方法携带的可变参数
        :param kwargs: 方法携带的关键字参数
        :param retry: （除了初次执行的一次）额外重试的次数
        :param delay: 重试时间间隔
        :param default: 默认的返回值
        :param error_callback: 错误处理的回调
        """
        self._func = func
        self._args = args
        self._xargs = xargs
        self._kwargs = kwargs
        self._retry = retry
        self._delay = delay
        self._default = default
        self._error_callback = error_callback

    def start(self):
        result = self._default
        while self._retry >= 0:
            try:
                result = self._func(*self._args, *self._xargs, **self._kwargs)
                break
            except Exception as e:
                if callable(self._error_callback):
                    self._error_callback(traceback.format_exc())
                if self._retry == 0:
                    print("[Retry]Retry failed, error: %s" % e)
                    break
            time.sleep(self._delay)
            self._retry = self._retry - 1
        return result



def print_args(logger=print, stacklevel=2):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if args:
                kw = {'stacklevel':stacklevel}
                if logger == print:
                    kw = {}
                if logger and callable(logger):
                    logger(args[-1], **kw)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def print_start_end(logger=print, stacklevel=3):
    frame = inspect.stack()[1]
    file_name = frame.filename
    def decorator(func):
        def wrapper(*args, **kwargs):
            kw = {'stacklevel':stacklevel}
            if logger == print:
                kw = {}
            if logger and callable(logger):
                logger(file_name+' start', **kw)
            result = func(*args, **kwargs)
            if logger and callable(logger):
                logger(file_name+' end', **kw)
            return result
        return wrapper
    return decorator


def make_excel(data, file_name, titles=[], widths=[], columns=[]):
    '''
    data: 数据
    file_name: 文件名，比如`data.xlsx`
    titles: 表头，['ID', '昵称', '账号', '消息内容']
    widths: 列宽，[10, 20, 30, 60]
    columns: 选取的列，如果不指定，按照data[i].values()顺序
    titles/widths/columns要对应
    '''
    path = os.path.dirname(file_name)
    if not os.path.exists(path):
        os.makedirs(path) # 创建多级目录

    rows = []
    cell_fmt = 'A%d'
    if titles:
        rows.append(titles)
    if not columns:
        # 未指定列，按顺序填充表格
        for it in data:
            row = list(it.values())
            rows.append(row)
    else:
        # 指定列，按指定次序填充表格
        for it in data:
            row = []
            for k in columns:
                row.append(it[k])
            rows.append(row)

    workbook = xlsxwriter.Workbook(file_name)
    worksheet = workbook.add_worksheet()

    for i in range(len(rows)):
        row = rows[i]
        cell = cell_fmt % (i+1)
        worksheet.write_row(cell, row)

    if widths:
        for i in range(len(widths)):
            worksheet.set_column(i,i,widths[i])
    workbook.close()


def save_excel(path, data, file_name, titles=[], widths=[], columns=[]):
    file_path = os.path.join(path, file_name)
    make_excel(data, file_path, titles, widths, columns)
    return file_path


if __name__ == '__main__':
    # def test():
    #     data = [
    #         {'id':1, 'name':'tao', 'msg': 'hello'},
    #         {'id':2, 'name':'xia', 'msg': 'world'},
    #         {'id':3, 'name':'mao', 'msg': 'hi'},
    #     ]
    #     save_excel('.', data, 'test.xlsx', ['NAME', 'MSG'], [20, 30], ['name', 'msg'])
    # test()
    pass
