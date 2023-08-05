'''
线程类 MyThread，以及线程管理类MyProcess

MyThread 创建线程，并获取执行结果
MyProcess 从线程池创建/获取线程。阻塞运行，直到所有线程执行完毕，统一返回结果
'''

import threading
import time


class MyThread(threading.Thread):
    def __init__(self, func, args=(), semaphore=None):
        super(MyThread, self).__init__()
        self._func = func
        self._args = args
        self._result = None
        self._semaphore = semaphore

    def reset(self, func, args=()):
        self._started.clear()
        self._func = func
        self._args = args

    def start(self):
        if self._semaphore:
            self._semaphore.acquire()
        super(MyThread, self).start()

    def run(self):
        self._result = self._func(*self._args)
        if self._semaphore:
            self._semaphore.release()

    def get_result(self):
        try:
            return self._result
        except Exception:
            return None


class MyProcess(object):
    def __init__(self, batch=10, semaphore=None):
        self._threads_pool = {}  # 线程池，重复使用，可避免创建新线程导致的内存占用持续增加
        self._batch = batch
        self._start_index = 0
        self._end_index = batch
        self._semaphore = semaphore

    def __del__(self):
        self._semaphore = None
        self._threads_pool = None

    def begin(self, data, func, each_callback=None, finish_callback=None):
        '''
        func处理函数的参数为 index, item
        :param data: 需要处理的数据，数组
        :param func: 处理数据的方法
        :param each_callback: 每处理一个数据，回调方法
        :param finish_callback: 处理完所有数据，回调方法
        :return: 所有数据处理的结果。
                 等同于`finish_callback`的回调参数
        '''
        results = []
        while True:
            if self._start_index >= len(data):
                break
            if self._end_index > len(data):
                self._end_index = len(data)
            threads = []
            for i in range(self._start_index, self._end_index):
                arg = data[i]
                thread = self._threads_pool.get(i%self._batch)
                if thread:
                    thread.reset(func, args=(i, arg,))
                else:
                    thread = MyThread(func, args=(i, arg,), semaphore=self._semaphore)
                    self._threads_pool[i%self._batch] = thread
                thread.start()
                threads.append(thread)
            # 更新下标
            self._start_index = self._end_index
            self._end_index = self._end_index + self._batch
            for thread in threads:
                thread.join()
            for thread in threads:
                result = thread.get_result()
                # result 为 None的情况，外面处理
                if callable(each_callback):
                    each_callback(result)  # 回调本次结果，外面根据自己情况处理
                # 这里只是 append
                # 当 result 为 list 时，
                # 可能需要的是 extend，还可以在外部自行处理
                # 但无法具体分辨实际需求
                results.append(result)
        self._start_index = 0
        self._end_index = self._batch
        if callable(finish_callback):
            finish_callback(results)
        return results  # 返回值可用，可不用

###
### test
###

def go(index, param):
    # 单个线程需要进行的操作
    ret = '%04d-%04d'%(index, param)
    time.sleep(1)
    return ret

def each(result):
    print(result)

def finish(results):
    print('finish', len(results))


if __name__ == '__main__':
    # semaphore = threading.Semaphore(15)  # 限制，也是保护
    process = MyProcess(batch=5)

    while True:
        arr = []
        for i in range(22):
            arr.append(i)

        ret = process.begin(arr, go, each, finish)
        time.sleep(3)
    pass
