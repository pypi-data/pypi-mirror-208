'''
并行执行任务
'''
from concurrent.futures import ThreadPoolExecutor, as_completed

class ConcurrentJobs(object):
    def __init__(self, max_workers=10):
        self._executor = ThreadPoolExecutor(max_workers)


    def do(self, tasks, callback, each=None, finish=None):
        jobs = [self._executor.submit(callback, arg) for arg in tasks]
        results = []
        # for job in jobs:
        for job in as_completed(jobs):
            result = job.result()
            if callable(each):
                each(result)
            results.append(result)

        if callable(finish):
            finish(results)




import random
import time

# 参数times用来模拟网络请求的时间
def get_html(times):
    time.sleep(random.random())
    return times, times*2

def finish(results):
    print(len(results))

if __name__ == '__main__':
    jobs = ConcurrentJobs(100)
    while True:
        aaa = time.time()
        tasks = range(500)
        jobs.do(tasks, get_html, each=None, finish=finish)
        bbb = time.time()
        print(bbb-aaa)
