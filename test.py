import asyncio

# Gather

# async def task(id):
#     print("Begin task #{}".format(id))
#     await asyncio.sleep(1)
#     print("End task #{}".format(id))


# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     tasks = [task(id) for id in range(10)]
#     loop.run_until_complete(asyncio.gather(*tasks))

# Main

DEPTH = 2
CHILDREN = 2


async def task(id):
    print("Begin task #{}".format(id))
    await asyncio.sleep(id / 10)
    print("End task #{}".format(id))
    return CHILDREN


async def main(loop):
    """
    Tasks execution order: 
    [0]
    [1]     chained to [0]
    [2]     chained to [0]
    [1.1]   chained to [1]
    [1.2]   chained to [1]
    [2.1]   chained to [2]
    [2.2]   chained to [2]
    [1.1.1] chained to [1.1]
    [1.1.2] chained to [1.1]
    [1.2.1] chained to [1.2]
    [1.2.2] chained to [1.2]
    [2.1.1] chained to [2.1]
    [2.1.2] chained to [2.1]
    [2.2.1] chained to [2.2]
    [2.2.2] chained to [2.2]
    etc

    
    Main loop shall: 
    x = 0
    for d in range(depth):
        for i in range(x):
            create task[i] and wait for it to return x 

    for f in as_completed(fs):
        result = await f  # The 'await' may raise
    """

    print("begin main")
    for d in range(DEPTH):

        future = [task(0), task(1)]
        for f in asyncio.as_completed(future):
            result = await f  # The 'await' may raise

    print("end main")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    loop.run_until_complete(main(loop))

