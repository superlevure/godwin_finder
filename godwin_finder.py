import requests
import argparse
import sys
import socket
from bs4 import BeautifulSoup


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


def check_page(page, current_depth=0):
    print_ident(f'Looking for Godwin point at "{page}" (depth={current_depth})', current_depth)
    try:
        r = requests.get("https://fr.wikipedia.org" + page)
        soup[page] = BeautifulSoup(r.text, "html.parser")
        text = soup[page].get_text()

    except socket.gaierror:
        print("No internet connection")
        sys.exit(0)

    if any(s in text for s in KEYWORDS):
        print_ident("Godwin point FOUND", current_depth)
        return True
    else:
        if current_depth == depth_max:
            return False
        else:
            print_ident(f"Not found in depth {current_depth}. Looking deeper..", current_depth)
            current_depth += 1
            links[page] = []
            for link in soup[page].find(id="content").find_all("a"):
                if (
                    str(link.get("href")).startswith("/wiki/")
                    and not str(link.get("href")).startswith("/wiki/Fichier:")
                    and not str(link.get("href")).startswith("/wiki/Portail:")
                    and not str(link.get("href")).startswith("/wiki/Cat%C3%A9gorie:")
                    and not str(link.get("href")).startswith("/wiki/Aide:")
                ):
                    links[page].append(link.get("href"))
                    # print(link.get('href'))

            print_ident(f'{len(links[page])} links found in page "{page}"', current_depth)

            for link in links[page]:
                check_page(link, current_depth)


if __name__ == "__main__":
    try:
        check_page("/wiki/" + args.start_page)
    except KeyboardInterrupt:
        print("Bye bye")
        sys.exit(0)

