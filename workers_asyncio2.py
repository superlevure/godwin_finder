import asyncio
import random
import sys
from easy_timing import timer


MAX_TASKS = 100
MAX_WORKERS = 10

task_completed = 0
task_queued = 0


def print_ident(string, ident):
    print(ident.count(".") * "    " + string)


async def task(loop, task_id, lock):
    global task_completed, task_queued

    async with lock:
        print_ident(f"Begin task #{task_id}", task_id)
        await asyncio.sleep(0.5 + random.random())
        task_completed += 1
        print_ident(
            f"End task #{task_id} ({task_queued - task_completed} in queue, {task_completed} completed)",
            task_id,
        )

    if task_queued < MAX_TASKS:
        loop.create_task(task(loop, task_id + ".1", lock))
        task_queued += 1
        if task_queued < MAX_TASKS - 1:
            loop.create_task(task(loop, task_id + ".2", lock))
            task_queued += 1

    if task_completed == MAX_TASKS:
        loop.stop()


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        lock = asyncio.Semaphore(MAX_WORKERS)
        with timer(""):
            loop.create_task(task(loop, "1", lock))
            task_queued += 1
            loop.run_forever()

    except KeyboardInterrupt:
        print("\n Bye bye.")
        sys.exit(0)
