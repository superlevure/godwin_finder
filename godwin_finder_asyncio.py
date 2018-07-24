import asyncio
from asyncio import CancelledError
from random import random
import sys
import argparse
from bs4 import BeautifulSoup
import aiohttp
import time
import urllib.parse

KEYWORDS = ("Nazi", "Hitler", "Nazie")
MAX_WORKERS = 4


parser = argparse.ArgumentParser(description="Search wikipedia for godwin point")

parser.add_argument("start_page", help="Wikipedia start page")
parser.add_argument(
    "-d", "--depth", help="Depth of the research", action="store", default=2
)
args = parser.parse_args()

depth_max = int(args.depth)


class Factory:
    """
    Factory
    """

    def __init__(self, max_workers):
        self.task_queued = 0
        self.task_completed = 0
        self.max_workers = max_workers

        self.queue = asyncio.Queue()

    def print_ident(self, string, task_id):
        print((task_id.count(".") + 1) * "    " + string)

    async def manager(self):
        print("Begin work \n")

        await self.queue.put(
            ("1", "/wiki/" + args.start_page)
        )  # We add one task to the queue to start
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

    async def worker(self, worker_id):
        """Worker
        
        Arguments:
            worker_id {int} -- 
        """
        while True:
            task_id, page = await self.queue.get()
            page_decoded = urllib.parse.unquote(page)
            print(
                "Worker #{} takes charge of page {} (task {})".format(
                    worker_id, page_decoded, task_id
                )
            )
            await self.task(task_id, page)
            self.queue.task_done()

    async def task(self, task_id, page):
        """Task
        
        Arguments:
            task_id {string} -- 
        """
        page_decoded = urllib.parse.unquote(page)
        self.print_ident("Begin task #{}".format(task_id), task_id)
        async with aiohttp.ClientSession() as session:
            html = await self.fetch(session, "https://fr.wikipedia.org" + page)
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text()

        if any(s in text for s in KEYWORDS):
            self.print_ident(
                f"Godwin point FOUND in page {page_decoded} (task {task_id})", task_id
            )
            loop = asyncio.get_running_loop()
            pending = asyncio.Task.all_tasks(loop)
            for task in pending:
                task.cancel()
        else:
            self.print_ident(f"Godwin not found", task_id)

            if task_id.count(".") < depth_max:
                links = []
                for link in soup.find(id="content").find_all("a"):
                    if (
                        str(link.get("href")).startswith("/wiki/")
                        and not str(link.get("href")).startswith("/wiki/Fichier:")
                        and not str(link.get("href")).endswith("Projet:Accueil")
                        and not str(link.get("href")).startswith("/wiki/Portail:")
                        and not str(link.get("href")).startswith(
                            "/wiki/Cat%C3%A9gorie:"
                        )
                        and not str(link.get("href")).startswith("/wiki/Aide:")
                        and not str(link.get("href")).endswith("homonymie)")
                    ):
                        links.append(link.get("href"))

                self.print_ident(
                    f'{len(links)} links found in page "{page_decoded}"', task_id
                )

                for i, link in enumerate(links, 1):
                    await self.queue.put((task_id + "." + str(i), link))
                    self.task_queued += 1

        self.task_completed += 1
        self.print_ident(
            "End task #{} ({} queued, {} completed)".format(
                task_id, self.queue.qsize(), self.task_completed
            ),
            task_id,
        )

    async def fetch(self, session, url):
        async with session.get(url) as response:
            return await response.text()


if __name__ == "__main__":
    t1 = time.time()
    loop = asyncio.get_event_loop()

    factory = Factory(max_workers=MAX_WORKERS)

    try:
        loop.run_until_complete(factory.manager())

    except KeyboardInterrupt:
        print("\nBye bye")
        sys.exit(0)

    except CancelledError:
        loop.stop()

    finally:
        print(f"Executed in {round(time.time() - t1, 1)}s")
