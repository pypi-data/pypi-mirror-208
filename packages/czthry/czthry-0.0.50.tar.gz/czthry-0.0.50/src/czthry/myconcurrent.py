import concurrent.futures


class Concurrent(object):
    def __init__(self, action, data_list, max_workers=3):
        '''
        :param action: 每个线程执行的函数
        :param data_list: 数据列表
        :param max_workers: 最大线程数
        '''
        self.action = action
        self.data_list = data_list
        self.max_workers = max_workers

    def start(self):
        ''' 开始执行 '''
        total = len(self.data_list)
        # 创建线程池
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for i in range(total):
                data = self.data_list[i]
                # 提交任务
                executor.submit(self.action, i, data, total)
    pass
