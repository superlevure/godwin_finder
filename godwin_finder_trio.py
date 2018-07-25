import trio
from random import random
import sys
from easy_timing import timer
import argparse
from bs4 import BeautifulSoup
import asks
import time
import urllib.parse

KEYWORDS = ("Nazi", "Hitler", "Nazie")
# KEYWORDS = ("defzdeazefdezfzedezzf", "ezerzrerfez")

MAX_WORKERS = 4


parser = argparse.ArgumentParser(description="Search wikipedia for godwin point")

parser.add_argument("start_page", help="Wikipedia start page")
parser.add_argument(
    "-d", "--depth", help="Depth of the research", action="store", default=2
)
args = parser.parse_args()

depth_max = int(args.depth)


MAX_TASKS = 100
MAX_WORKERS = 10

task_completed = 0
task_queued = 0


def print_ident(string, ident):
    print(ident.count(".") * "    " + string)


async def task(nursery, lock, task_id, page):
    """Task
    
    Arguments:
        task_id {string} -- 
    """

    global task_completed, task_queued
    async with lock:
        page_decoded = urllib.parse.unquote(page)
        print_ident(
            f"Task #{task_id:10} - Begin                              - Page {page_decoded}",
            task_id,
        )
        html = await asks.get("https://fr.wikipedia.org" + page)

    soup = BeautifulSoup(html.content, "html.parser")
    text = soup.get_text()

    if any(s in text for s in KEYWORDS):
        print_ident(
            f"Task #{task_id:10} - Godwin point FOUND  - Page {page_decoded}", task_id
        )
        # To do: cancellation
        nursery.cancel_scope.cancel()
    else:
        print_ident(
            f"Task #{task_id:10} - Godwin not found                   - Page {page_decoded:30} ",
            task_id,
        )

        if task_id.count(".") < depth_max:
            links = []
            for link in soup.find(id="content").find_all("a"):
                if (
                    str(link.get("href")).startswith("/wiki/")
                    and not str(link.get("href")).startswith("/wiki/Fichier:")
                    and not str(link.get("href")).endswith("Projet:Accueil")
                    and not str(link.get("href")).startswith("/wiki/Portail:")
                    and not str(link.get("href")).startswith("/wiki/Cat%C3%A9gorie:")
                    and not str(link.get("href")).startswith("/wiki/Aide:")
                    and not str(link.get("href")).endswith("homonymie)")
                ):
                    links.append(link.get("href"))

            print_ident(
                f"Task #{task_id:10} - {len(links)} links found                      - Page {page_decoded:30} ",
                task_id,
            )

            for i, link in enumerate(links, 1):
                nursery.start_soon(task, nursery, lock, task_id + "." + str(i), link)
                task_queued += 1

        task_completed += 1
        print_ident(
            f"Task #{task_id:10} - End task ({task_queued - task_completed} in queue, {task_completed} completed) - Page {page_decoded}",
            task_id,
        )


async def main():
    global task_queued
    print("Begin parent")
    with trio.move_on_after(20):
        async with trio.open_nursery() as nursery:
            lock = trio.CapacityLimiter(MAX_WORKERS)
            print("Begin nursery")
            await task(nursery, lock, "1", "/wiki/" + args.start_page)
            task_queued += 1
            print("Waiting for children")

    print("End parent")


if __name__ == "__main__":
    try:
        asks.init("trio")
        with timer(""):
            trio.run(main)

    except KeyboardInterrupt:
        print("\n Bye bye.")
        sys.exit(0)
