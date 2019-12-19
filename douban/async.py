"""
协程请求
"""

import asyncio
import os
import time

import aiofiles
import aiohttp

from douban import mkdir_if_not_exsit, pages, per_pages

# 封面保存路径
covers_dir = os.path.join(os.path.dirname(os.path.abspath(__name__)), 'covers', 'async')
mkdir_if_not_exsit(covers_dir)


async def get_movies(session, page_start):
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
        return result['subjects']


async def download_cover(session, movie: dict):
    async with session.get(movie['cover']) as rv:
        result = await rv.read()
        return {'title': movie['title'], 'data': result}


async def save_cover(cover_name, cover_data):
    async with aiofiles.open(cover_name, 'wb') as f:
        await f.write(cover_data)


async def main():
    async with aiohttp.ClientSession() as session:
        all_movies = await asyncio.gather(*[get_movies(session, i * per_pages) for i in range(pages)])
        all_movies = [movie for movies in all_movies for movie in movies]
        for cover in await asyncio.gather(*[download_cover(session, movie) for movie in all_movies]):
            cover_name = os.path.join(covers_dir, '{}.jpg'.format(cover['title']))
            cover_data = cover['data']
            await save_cover(cover_name, cover_data)
            print(cover_name)


if __name__ == '__main__':
    start = time.time()
    asyncio.run(main())
    print('done', time.time() - start)
