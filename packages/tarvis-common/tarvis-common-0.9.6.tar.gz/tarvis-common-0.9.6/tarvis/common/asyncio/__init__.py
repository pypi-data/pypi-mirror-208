import asyncio


async def wait_first(*tasks):
    result = None
    exceptions = []

    while True:
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            exception = task.exception()
            if exception is None:
                result = task.result()
                if result:
                    break
            else:
                exceptions.append(exception)

        if result:
            cancelling = asyncio.gather(*pending, return_exceptions=True)
            cancelling.cancel()
            try:
                await cancelling
            except asyncio.CancelledError:
                pass
            break
        elif pending:
            tasks = pending
        else:
            break

    return result, exceptions
