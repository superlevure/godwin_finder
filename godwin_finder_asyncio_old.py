import aiohttp
import argparse
import sys
import socket
from bs4 import BeautifulSoup
import asyncio

SIMULTANEOUS_FETCH = 200
KEYWORDS = ("Nazi", "Hitler")

parser = argparse.ArgumentParser(description="Search wikipedia for godwin point")

parser.add_argument("start_page", help="Wikipedia start page")
parser.add_argument("-d", "--depth", help="Depth of the research", action="store", default=5)
args = parser.parse_args()

depth_max = int(args.depth)
soup = {}
links = {}


def print_ident(string, ident):
    print(ident * "    " + string)


def check_for_godwin(page, content, current_depth):
    """check a page for godwin point
    
    Arguments:
        page {string} -- page to check
    
    Returns:
        result -- 
        links -- list of all links to other wiki pages present in the page
    """

    soup = BeautifulSoup(content, "html.parser")
    text = soup.get_text()

    links = []

    if any(s in text for s in KEYWORDS):
        print_ident(f'Godwin point FOUND in "{page}" (depth {current_depth})', current_depth)
        result = True
    else:
        result = False
        for link in soup.find(id="content").find_all("a"):
            if (
                str(link.get("href")).startswith("/wiki/")
                and not str(link.get("href")).startswith("/wiki/Fichier:")
                and not str(link.get("href")).startswith("/wiki/Portail:")
                and not str(link.get("href")).startswith("/wiki/Cat%C3%A9gorie:")
                and not str(link.get("href")).startswith("/wiki/Aide:")
            ):
                links.append(link.get("href"))

    return result, links


async def fetch(loop, page, semaphore, current_depth=0):
    async with semaphore:
        try:
            # if page == "maison":
            #     asyncio.get_event_loop().create_task(fetch(loop, "ah_bon", semaphore))

            print(f"begin fetching {page}")
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
                try:
                    async with session.get("https://fr.wikipedia.org/wiki/" + page) as response:
                        html = await response.text()
                except socket.gaierror:
                    print("No internet connection")
                    sys.exit(0)
            result, links = check_for_godwin(page, html, current_depth)
            if result:
                print("Cancelling other tasks")
                pending = asyncio.Task.all_tasks(loop)
                for task in pending:
                    # print(task)
                    task.cancel()
                    # Maybe, cancel gather instead (it will propagate to the children)

            print(f"end fetching {page}")
        except asyncio.CancelledError:
            print("Task cancelled")


async def main(loop):
    semaphore = asyncio.BoundedSemaphore(SIMULTANEOUS_FETCH)

    wiki_list = ["maison", "avion", "guerre", "test", "bar", "foo"]

    for page in wiki_list:
        await loop.create_task(fetch(loop, page, semaphore))
        # await fetch(loop, page, semaphore)


if __name__ == "__main__":
    """
    
    Boucle principale, un tour par depth  
        Depth 0:
            add 1 task (fetch(start_page)) -> return page 
            chained coroutine: check_for_godwin(start page)
            if not success: 
                chained coroutine: get_all_links(start page) -> return x depth(1)
            if sucess: 
                stop all tasks 
                exit
        Depth 1: 
            add x task (fetch(each link)) -> return pages
            chained coroutine: check_for_godwin(each page)
            if not success: 
                chained coroutine: get_all_links(each page) -> return x depth(2)
            if sucess: 
                stop all tasks 
                exit
        Depth 2:
            add x task (fetch(each link)) -> return pages
            chained coroutine: check_for_godwin(each page)
            if not success: 
                chained coroutine: get_all_links(each page) -> return x depth(3)
            if sucess: 
                stop all tasks 
                exit


    Inconvenients: aucune task de depth n+1 n'est schedulé avant que toutes les task
    depth n ne soient finis 
    Sauf si, 
    


    """

    try:
        loop = asyncio.get_event_loop()

        loop.run_until_complete(main(loop))

    except KeyboardInterrupt:
        print("Bye bye")
        sys.exit(0)

    except asyncio.CancelledError:
        pass

