import os

import requests

pages = 20  # 准备抓取的页数
per_pages = 20  # 每页的条目数


def get_movies(page_start: int = 0):
    """
    请求接口 获取电影数据
    :param page_start: 开始页 从这一页开始获取数据 每次获取20条数据
    """
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
    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()

    return resp.json()['subjects']


def download_cover(movie: dict):
    """
    通过电影数据 获取电影封面数据 封装为字典
    :param movie: 电影数据
    """
    return {'title': movie['title'], 'data': requests.get(movie['cover']).content}


def save_cover(cover_name: str, cover_data: bytes):
    """
    将封面数据保存到本地
    :param cover_name: 封面文件路径名
    :param cover_data: 封面数据
    """
    with open(cover_name, 'wb') as f:
        f.write(cover_data)


def mkdir_if_not_exsit(path):
    """
    如果目录不存在就创建
    :param path: 需要创建的路径
    """
    if not os.path.exists(path):
        os.makedirs(path)
