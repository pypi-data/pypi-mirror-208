'''
通过协程异步执行批量工作

给定数组，作为重复任务的执行参数
并行执行，
统一返回结果
'''
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor


class AsyncJobs(object):
    def __init__(self, concurrent_num=10):
        self._work = None
        self._loop = asyncio.get_event_loop()
        self._loop.set_default_executor(ThreadPoolExecutor(concurrent_num))  # 并行数量
        pass

    async def _do_work(self, arg):
        result = await self._loop.run_in_executor(None, self._work, arg)
        return result

    def do(self, tasks, work, finish):
        self._work = work
        works = [self._do_work(arg) for arg in tasks]
        jobs = asyncio.gather(*works)
        self._loop.run_until_complete(jobs)
        results = jobs.result()
        if callable(finish):
            finish(results)

    def __del__(self):
        self._work = None


def test():
    def hard_work(arg):
        time.sleep(1)
        return arg, arg*2

    def finish(results):
        print('%s'%results)
        pass

    jobs = AsyncJobs(20)
    while True:
        aaa = time.time()
        tasks = list(range(100))
        jobs.do(tasks, hard_work, finish)
        bbb = time.time()
        print('%s' % (bbb - aaa))


if __name__ == '__main__':
    test()

# 41.3
