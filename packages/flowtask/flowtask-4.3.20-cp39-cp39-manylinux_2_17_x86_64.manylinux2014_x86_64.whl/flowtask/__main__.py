"""Data Integration Executor."""
import os
import logging
import asyncio
import uvloop
from flowtask.runner import TaskRunner
from flowtask.utils import cPrint

os.environ['PYTHONASYNCIODEBUG'] = '1'
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
uvloop.install()

async def task(loop):
    runner = None
    try:
        runner = TaskRunner(loop=loop)
        async with runner as job:
            if await job.start():
                await job.run()
    except Exception as e:  # pylint: disable=W0718
        logging.exception(e, stack_info=True)
    finally:
        return runner

def main():
    loop = asyncio.get_event_loop()
    try:
        result = loop.run_until_complete(
            task(loop)
        )
        if result:
            cPrint(' === RESULT === ', level="DEBUG")
            print(result.result)
            cPrint('== Task stats === ', level="INFO")
            print(result.stats)
    finally:
        loop.close()

if __name__ == '__main__':
    main()
