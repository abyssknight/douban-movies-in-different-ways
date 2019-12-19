"""
使用多线程队列, 生产者 消费者模型

movies_queue    电影队列 下载的所有电影数据放入此队列
covers_queue    封面队列 从电影队列取值下载封面数据后放入此队列

共有三组任务, 分别为:
    获取电影数据放入电影队列
    从电影队列获取数据下载封面数据放入封面队列
    从封面队列获取封面数据保存本地

这三组任务并发运行
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor, wait
from queue import Queue

import requests

from douban import mkdir_if_not_exsit, pages, per_pages

# 封面保存路径
covers_dir = os.path.join(os.path.dirname(os.path.abspath(__name__)), 'covers', 'thread_queue')
mkdir_if_not_exsit(covers_dir)


def get_movies(movies_queue, page_start=0):
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
    proxies = {
        "http": "http://localhost:10800",
    }
    resp = requests.get(url, params=params, headers=headers, proxies=proxies)
    resp.raise_for_status()

    # 遍历所有条目 放入队列
    for movie in resp.json()['subjects']:
        movies_queue.put(movie)


def download_cover(movies_queue, covers_queue):
    while True:
        # 获取到 None 表示任务结束
        movie = movies_queue.get()
        if movie is None:
            break

        result = requests.get(movie['cover']).content
        covers_queue.put({'title': movie['title'], 'data': result})

        movies_queue.task_done()


def save_cover(covers_queue):
    while True:
        # 获取到 None 表示任务结束
        cover = covers_queue.get()
        if cover is None:
            break

        cover_name = os.path.join(covers_dir, '{}.jpg'.format(cover['title']))
        with open(cover_name, 'wb') as f:
            f.write(cover['data'])
        covers_queue.task_done()

        print(cover_name)


def main():
    movies_queue = Queue()
    covers_queue = Queue()

    with ThreadPoolExecutor(max_workers=pages * 3) as exector:
        # 创建三组任务
        movies_futures = [exector.submit(get_movies, movies_queue, i * per_pages) for i in range(pages)]
        _ = [exector.submit(download_cover, movies_queue, covers_queue) for _ in range(pages)]
        _ = [exector.submit(save_cover, covers_queue) for _ in range(pages)]

        # 等待所有生产者生产完成
        wait(movies_futures)
        # 等待所有消费者处理完成
        movies_queue.join()
        covers_queue.join()

        # 发送 None 通知消费者结束任务
        for _ in range(pages):
            movies_queue.put(None)
            covers_queue.put(None)


if __name__ == '__main__':
    start = time.time()
    main()
    print('done', time.time() - start)
