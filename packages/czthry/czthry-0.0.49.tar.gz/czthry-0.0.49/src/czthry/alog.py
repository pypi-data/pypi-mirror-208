import logging
import datetime
import os, sys


class Logger(object):
    __msgfmt = '%(asctime)s.%(msecs)03d | %(filename)s:%(funcName)s[%(lineno)d] | %(levelname)s : %(message)s'
    __datefmt = '%Y-%m-%d %H:%M:%S'

    def __init__(self, filename=None):
        if filename is None:
            filename = ''
        logname = '{:%Y%m%d%H%M%S%f}'.format(datetime.datetime.now())+filename
        self.logger = logging.getLogger(logname)
        self.__checkFilePath(filename)
        self.__setupFileLog(filename)
        self.__setupConsoleLog()

        # python 3.6 版本 不支持`stacklevel`参数关键字，需要另设置 `.d .i .w .e .x` 方法
        ver = sys.version_info
        if ver.major < 3 or (ver.major == 3 and ver.minor <= 6):
            self.d = self.logger.debug
            self.i = self.logger.info
            self.w = self.logger.warning
            self.e = self.logger.error
            self.x = self.logger.critical
            self.exc = self.logger.exception

    def __setupFileLog(self, file):
        if file is None or len(file) == 0:
            return
        formatter = logging.Formatter(self.__msgfmt)
        formatter.datefmt = self.__datefmt
        file_handler = logging.FileHandler(file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)

    def __setupConsoleLog(self):
        formatter = logging.Formatter(self.__msgfmt)
        formatter.datefmt = self.__datefmt
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(console_handler)

    def __checkFilePath(self, filename):
        arr = filename.split('/')
        if len(arr) == 1:
            return
        makeFilePath(filename)

    def d(self, *args, **kwargs):
        msg = ' '.join(['%s'%i for i in args])
        stacklevel = kwargs.get('stacklevel', 2)
        self.logger.debug(msg, stacklevel=stacklevel)

    def i(self, *args, **kwargs):
        msg = ' '.join(['%s'%i for i in args])
        stacklevel = kwargs.get('stacklevel', 2)
        self.logger.info(msg, stacklevel=stacklevel)

    def w(self, *args, **kwargs):
        msg = ' '.join(['%s'%i for i in args])
        stacklevel = kwargs.get('stacklevel', 2)
        self.logger.warning(msg, stacklevel=stacklevel)

    def e(self, *args, **kwargs):
        msg = ' '.join(['%s'%i for i in args])
        stacklevel = kwargs.get('stacklevel', 2)
        self.logger.error(msg, stacklevel=stacklevel)

    def exc(self, *args, **kwargs):
        msg = ' '.join(['%s'%i for i in args])
        stacklevel = kwargs.get('stacklevel', 3)
        self.logger.exception(msg, stacklevel=stacklevel)

    def x(self, *args, **kwargs):
        msg = ' '.join(['%s'%i for i in args])
        stacklevel = kwargs.get('stacklevel', 2)
        self.logger.critical(msg, stacklevel=stacklevel)


class Printer(object):
    __msgfmt = '%(message)s'

    def __init__(self, terminator=None):
        logname = '{:%Y%m%d%H%M%S%f}'.format(datetime.datetime.now())
        self.logger = logging.getLogger(logname)
        self.__terminator = terminator
        self.__setupConsoleLog()
        self.__setupAlias()


    def __setupConsoleLog(self):
        formatter = logging.Formatter(self.__msgfmt)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        if self.__terminator is not None:
            console_handler.terminator = self.__terminator
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(console_handler)

    def __setupAlias(self):
        self.d = self.logger.debug
        self.i = self.logger.info
        self.w = self.logger.warning
        self.e = self.logger.error
        self.x = self.logger.critical


def makeFilePath(path):
    arr = path.split('/')
    if len(arr) == 1:
        return
    filepath = os.path.join(*arr[:-1])
    if os.path.exists(filepath):
        return
    paths = filepath.split('/')
    for i in range(len(paths)):
        folder = '/'.join(paths[:i + 1])
        if not os.path.exists(folder):
            os.mkdir(folder)
    return filepath


def test():
    log = Logger()
    log.d('debug')
    log.i('info')
    log.e('error')
    try:
        a = 1/0
        log.d(a)
    except:
        log.exc('做除法的时候出错')
    log.i('come here')
    pass


if __name__ == '__main__':
    test()
