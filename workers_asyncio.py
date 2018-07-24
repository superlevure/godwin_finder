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
        self.task_completed = 0
        self.max_workers = max_workers
        self.max_tasks = max_tasks

        self.queue = asyncio.Queue()


    def print_ident(self, string, task_id):
        print((task_id.count(".") + 1) * "    " + string)

    async def task(self, task_id):
        """Task
        
        Arguments:
            task_id {string} -- 
        """

        sleep_time = 0.5 + random()
        self.print_ident("Begin task #{}".format(task_id), task_id)
        await asyncio.sleep(sleep_time)

        if self.task_queued < self.max_tasks:
            await self.queue.put(task_id + ".1")
            self.task_queued += 1
        if self.task_queued < self.max_tasks:
            await self.queue.put(task_id + ".2")
            self.task_queued += 1

        self.task_completed += 1
        self.print_ident(
            "End task #{} ({} queued, {} completed)".format(
                task_id, self.queue.qsize(), self.task_completed
            ),
            task_id,
        )

    async def worker(self, worker_id):
        """Worker
        
        Arguments:
            worker_id {int} -- 
        """

        while True:
            task_id = await self.queue.get()
            print("Worker #{} takes charge of task {}".format(worker_id, task_id))
            await self.task(task_id)
            self.queue.task_done()

    async def organize_work(self):
        print("Begin work \n")

        await self.queue.put("1")  # We add one task to the queue to start
        self.task_queued += 1

        workers = [
            asyncio.create_task((self.worker(worker_id + 1)))
            for worker_id in range(self.max_workers)
        ]

        await self.queue.join()

        print("Queue is empty, {} tasks completed".format(self.task_queued))
        for w in workers:
            w.cancel()
        print("\nEnd work")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    factory = Factory(max_workers=100, max_tasks=1000)

    try:
        loop.run_until_complete(factory.organize_work())

    except KeyboardInterrupt:
        print("\nBye bye")
        sys.exit(0)

