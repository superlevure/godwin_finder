import trio
import random
import sys
from easy_timing import timer


MAX_TASKS = 100
MAX_WORKERS = 10

task_completed = 0
task_queued = 0


def print_ident(string, ident):
    print(ident.count(".") * "    " + string)


async def task(nursery, task_id, lock, task_status=trio.TASK_STATUS_IGNORED):
    global task_completed, task_queued

    task_status.started()
    async with lock:
        print_ident(f"Begin task #{task_id}", task_id)
        await trio.sleep(0.5 + random.random())
        task_completed += 1
        print_ident(
            f"End task #{task_id} ({task_queued - task_completed} in queue, {task_completed} completed)",
            task_id,
        )

    if task_queued < MAX_TASKS:
        await nursery.start(task, nursery, task_id + ".1", lock)
        task_queued += 1
        if task_queued < MAX_TASKS - 1:
            await nursery.start(task, nursery, task_id + ".2", lock)
            task_queued += 1
            if task_queued < MAX_TASKS - 2:
                await nursery.start(task, nursery, task_id + ".3", lock)
                task_queued += 1


async def main():
    global task_queued
    print("Begin parent")
    with trio.move_on_after(20):
        async with trio.open_nursery() as nursery:
            lock = trio.CapacityLimiter(MAX_WORKERS)
            print("Begin nursery")
            await nursery.start(task, nursery, "1", lock)
            task_queued += 1
            print("Waiting for children")

    print("End parent")


if __name__ == "__main__":
    try:
        with timer(""):
            trio.run(main)

    except KeyboardInterrupt:
        print("\n Bye bye.")
        sys.exit(0)
