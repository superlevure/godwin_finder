import requests
import argparse
import sys
import socket
from bs4 import BeautifulSoup



KEYWORDS = ('Nazi', 'Hitler')

parser = argparse.ArgumentParser(description="Search wikipedia for godwin point")

parser.add_argument("start_page", help="Wikipedia start page")
parser.add_argument("-d", "--depth", help="Depth of the research", action="store", default=5)
args = parser.parse_args()

depth_max = int(args.depth)
soup = {}
links = {}



# current_depth = 0
# current_page = args.start_page


# while current_depth <= args.depth:
#     if current_depth == 0:
#         print(f'Looking for Godwin point from "{args.start_page}" wikipedia page')
#         r = requests.get('https://fr.wikipedia.org/wiki/' + args.start_page)

#         soup[args.start_page] = BeautifulSoup(r.text, 'html.parser')
#         # print(soup[args.start_page].find(id="content"))   
#         links[args.start_page] = []

#         for link in soup[args.start_page].find(id="content").find_all('a'):
#             if str(link.get('href')).startswith('/wiki/') and not str(link.get('href')).startswith('/wiki/Fichier:') and not str(link.get('href')).startswith('/wiki/Portail:') and not str(link.get('href')).startswith('/wiki/Cat%C3%A9gorie:') and not str(link.get('href')).startswith('/wiki/Aide:'):
#                 links[args.start_page].append(link.get('href')[6:])
#                 print(link.get('href')[6:])
        
#         print(f'{len(links[args.start_page])} links found in page "{args.start_page}')
#     else:
    
#         print(f'Looking for Godwin at "d" wikipedia page')
#         r = requests.get('https://fr.wikipedia.org/wiki/' + args.start_page)

#     if any(s in r.text for s in KEYWORDS):
#         print(f'Godwin found ! (depth {current_depth}, page "{current_page}")')
#         break
#     else:
#         print(f'Not found in depth {current_depth}. Looking deeper..')
#         current_depth += 1


def check_page(page, current_depth=0):
    print(f'Looking for Godwin point at "{page}" wikipedia page (depth={current_depth})')
    try:
        r = requests.get('https://fr.wikipedia.org/wiki/' + page)
    except socket.gaierror:
        print('No internet connection')
        sys.exit(0)

    
    if any(s in r.text for s in KEYWORDS):
        print('Godwin point FOUND')
        return True
    else:
        if current_depth == depth_max:
            return False
        else:
            print(f'Not found in depth {current_depth}. Looking deeper..')
            current_depth += 1

            soup[page] = BeautifulSoup(r.text, 'html.parser') 
            links[page] = []
            for link in soup[page].find(id="content").find_all('a'):
                if str(link.get('href')).startswith('/wiki/') and not str(link.get('href')).startswith('/wiki/Fichier:') and not str(link.get('href')).startswith('/wiki/Portail:') and not str(link.get('href')).startswith('/wiki/Cat%C3%A9gorie:') and not str(link.get('href')).startswith('/wiki/Aide:'):
                    links[page].append(link.get('href'))
                    # print(link.get('href'))
            
            print(f'{len(links[page])} links found in page "{page}"')
            
            for link in links[page]:
                check_page(link, current_depth)


if __name__ == "__main__":
    print(f'Depth max = {depth_max}')
    check_page(args.start_page)




