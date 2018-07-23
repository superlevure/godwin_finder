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

MAX_WORKERS = 3
MAX_TASKS = 10

task_queued = 0

async def task(queue, id="1"):
    global task_queued
    sleep_time = 0.5 + random()
    print('     Begin task #{}'.format(id))
    await asyncio.sleep(sleep_time)
    if task_queued < MAX_TASKS:
        await queue.put(id + ".1")
        task_queued += 1
    if task_queued < MAX_TASKS:
        await queue.put(id + ".2")
        task_queued += 1
    print('     End task #{} ({} item(s) in the queue)'.format(id, queue.qsize()))




async def worker(worker_id, queue):
    while True:
        task_id = await queue.get()
        print('Worker #{} takes charge of task {}'.format(worker_id, task_id))
        await task(queue, task_id)
        queue.task_done()


async def main():
    global task_queued
    print('Begin main \n')
    queue = asyncio.Queue()
    await queue.put("1") # We add one task to the queue
    task_queued += 1

    workers = [asyncio.create_task((worker(worker_id + 1, queue))) for worker_id in range(MAX_WORKERS)]

    await queue.join()

    print('Queue is empty, {} tasks completed'.format(task_queued))
    for w in workers:
        w.cancel()
    print('\n End main')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print('\nBye bye')
        sys.exit(0)

