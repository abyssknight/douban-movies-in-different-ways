# douban-movies-in-different-ways

豆瓣电影封面抓取示例 分别使用同步、多线程、多线程队列、协程、协程队列来不断提高抓取速度

* [同步请求](./douban/sync.py)
* [多线程请求](./douban/thread.py)
* [多线程队列请求](./douban/thread_queue.py)
* [协程请求](./douban/async.py)
* [协程队列请求](./douban/async_queue.py)
* [Go 语言协程实现](https://github.com/Abyssknight/douban-movies-in-different-ways-go)