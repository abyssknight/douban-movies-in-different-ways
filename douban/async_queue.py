"""
使用协程队列 原理同多线程队列
"""

import asyncio
import os
import time

import aiofiles
import aiohttp

from douban import mkdir_if_not_exsit, pages, per_pages

# 封面保存路径
covers_dir = os.path.join(os.path.dirname(os.path.abspath(__name__)), 'covers', 'async_queue')
mkdir_if_not_exsit(covers_dir)


async def get_movies(session, movies_queue, page_start):
    url = 'https://movie.douban.com/j/search_subjects'
    params = {
        'type': 'movie',
        'tag': '热门',
        'sort': 'recommend',
        'page_limit': 20,
        'page_start': page_start
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
    }

    async with session.get(url, params=params, headers=headers) as rv:
        result = await rv.json()
        for movie in result['subjects']:
            await movies_queue.put(movie)


async def download_cover(session, movies_queue, covers_queue):
    while True:
        movie = await movies_queue.get()

        async with session.get(movie['cover']) as rv:
            result = await rv.read()
            await covers_queue.put({'title': movie['title'], 'data': result})
        movies_queue.task_done()


async def save_cover(covers_queue):
    while True:
        cover = await covers_queue.get()

        cover_name = os.path.join(covers_dir, '{}.jpg'.format(cover['title']))
        async with aiofiles.open(cover_name, 'wb') as f:
            await f.write(cover['data'])
        covers_queue.task_done()

        print(cover_name)


async def main():
    movies_queue = asyncio.Queue()
    covers_queue = asyncio.Queue()

    async with aiohttp.ClientSession() as session:
        movies_tasks = [asyncio.create_task(download_cover(session, movies_queue, covers_queue)) for _ in range(pages)]
        covers_tasks = [asyncio.create_task(save_cover(covers_queue)) for _ in range(pages)]

        await asyncio.gather(*[get_movies(session, movies_queue, i * per_pages) for i in range(pages)])

        await movies_queue.join()
        await covers_queue.join()

        for task in movies_tasks:
            task.cancel()

        for task in covers_tasks:
            task.cancel()


if __name__ == '__main__':
    start = time.time()
    asyncio.run(main())
    print('done', time.time() - start)
