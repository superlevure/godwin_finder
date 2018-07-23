import asyncio
from random import random
import sys

"""
[1]
[1.1]
[1.2]
[1.1.1]
[1.1.2]
[1.2.1]
[1.2.2]
[1.1.1.1]
[1.1.1.2]
[1.1.2.1]
[1.1.2.2]
[1.2.1.1]
[1.2.1.2]
[1.2.2.1]
[1.2.2.2]
etc
"""



class Factory:
    """
    Factory
    """

    def __init__(self, max_workers, max_tasks):
        self.task_queued = 0
        self.max_workers = max_workers
        self.max_tasks = max_tasks

        self.queue = asyncio.Queue()

    async def task(self, task_id):
        sleep_time = 0.5 + random()
        print('     Begin task #{}'.format(task_id))
        await asyncio.sleep(sleep_time)
    
        if self.task_queued < self.max_tasks:
            await self.queue.put(task_id + ".1")
            self.task_queued += 1
        if self.task_queued < self.max_tasks:
            await self.queue.put(task_id + ".2")
            self.task_queued += 1
            
        print('     End task #{} ({} item(s) in the queue)'.format(task_id, self.queue.qsize()))


    async def worker(self, worker_id):
        while True:
            task_id = await self.queue.get()
            print('Worker #{} takes charge of task {}'.format(worker_id, task_id))
            await self.task(task_id)
            self.queue.task_done()


    async def organize_work(self):
        print('Begin work \n')
        
        await self.queue.put("1") # We add one task to the queue to start
        self.task_queued += 1

        workers = [asyncio.create_task((self.worker(worker_id + 1))) for worker_id in range(self.max_workers)]

        await self.queue.join()

        print('Queue is empty, {} tasks completed'.format(self.task_queued))
        for w in workers:
            w.cancel()
        print('\nEnd work')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    factory = Factory(max_workers=3, max_tasks=50)

    try:
        loop.run_until_complete(factory.organize_work())

    except KeyboardInterrupt:
        print('\nBye bye')
        sys.exit(0)

