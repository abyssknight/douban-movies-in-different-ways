"""
多线程请求
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor

from douban import download_cover, get_movies, mkdir_if_not_exsit, pages, per_pages, save_cover

# 封面保存路径
covers_dir = os.path.join(os.path.dirname(os.path.abspath(__name__)), 'covers', 'thread')
mkdir_if_not_exsit(covers_dir)


def save(cover):
    cover_name = os.path.join(covers_dir, '{}.jpg'.format(cover['title']))
    cover_data = cover['data']
    save_cover(cover_name, cover_data)
    print(cover_name)


def main():
    with ThreadPoolExecutor(max_workers=pages * 3) as exector:
        all_movies = exector.map(get_movies, [i * per_pages for i in range(pages)])

        results = []
        for movies in all_movies:
            results.append(exector.map(download_cover, movies))

        for covers in results:
            exector.map(save, covers)


if __name__ == '__main__':
    start = time.time()
    main()
    print('done', time.time() - start)
