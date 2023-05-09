# -*- coding:utf-8 -*-
import requests
from requests.exceptions import RequestException
import os, time
import re
from lxml import etree
import threading

lock = threading.Lock()
def get_html(url):
    """
    定义一个方法，用于获取一个url页面的响应内容
    :param url: 要访问的url
    :return: 响应内容
    """
    response = requests.get(url, timeout=10)
    # print(response.status_code)
    try:
        if response.status_code == 200:

            # print(response.text)
            return response.text
        else:
             return None
    except RequestException:
        print("请求失败")
        # return None


def parse_html(html_text):
    """
    定义一个方法，用于解析页面内容，提取图片url
    :param html_text:
    :return:一个页面的图片url集合
    """
    html = etree.HTML(html_text)

    if len(html) > 0:
        img_src = html.xpath("//img[@data-src]/@data-src")  # 元素提取方法
        # print(img_src)
        return img_src

    else:
        print("解析页面元素失败")

def get_image_pages(url):
    """
    获取所查询图片结果的所有页码
    :param url: 查询图片url
    :return: 总页码数
    """

    html_text = get_html(url)  # 获取搜索url响应内容
    # print(html_text)
    if html_text is not None:
        html = etree.HTML(html_text)  # 生成XPath解析对象
        last_page = html.xpath("//div[@class='pages']//a[last()]/@href")  # 提取最后一页所在href链接
        print(last_page)
        if last_page:
            max_page = re.compile(r'(\d+)', re.S).search(last_page[0]).group()  # 使用正则表达式提取链接中的页码数字
            print(max_page)
            print(type(max_page))
            return int(max_page)  # 将字符串页码转为整数并返回
        else:
            print("暂无数据")
            return None
    else:
        print("查询结果失败")


def get_all_image_url(page_number):
    """
    获取所有图片的下载url
    :param page_number: 爬取页码
    :return: 所有图片url的集合
    """

    base_url = 'https://imgbin.com/free-png/naruto/'
    image_urls = []

    x = 1  # 定义一个标识，用于给每个图片url编号，从1递增
    for i in range(1, page_number):
        url = base_url + str(i)  # 根据页码遍历请求url
        try:
            html = get_html(url)  # 解析每个页面的内容
            if html:
                data = parse_html(html)  # 提取页面中的图片url
                # print(data)
                # time.sleep(3)
                if data:
                    for j in data:
                        image_urls.append({
                            'index': x,
                            'img_src': j
                        })
                        x += 1  # 每提取一个图片url，标识x增加1
        except RequestException as f:
            print("遇到错误：", f)
            continue
    # print(image_urls)
    return image_urls

def get_image_content(url):
    """请求图片url，返回二进制内容"""
    # print("正在下载", url)
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.content
        return None
    except RequestException:
        return None

def main(index, img_src):
    """
    主函数：实现下载图片功能
    :param index: 第几张图片
    :param img_src: 图片地址
    :return:
    """
    # semaphore.acquire()  # 加锁，限制线程数
    with semaphore:
        print('当前子线程: {}'.format(threading.current_thread().name))
        save_path = os.path.abspath('.') + '/pics/'
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        try:
            file_path = '{0}/{1}.jpg'.format(save_path, index)
            if not os.path.exists(file_path):  # 判断是否存在文件，不存在则爬取
                with open(file_path, 'wb') as f:
                    f.write(get_image_content(img_src))
                    # f.close()

                    print('第{}个文件保存成功'.format(index))

            else:
                print("第{}个文件已存在".format(index))

            # semaphore.release()  # 解锁imgbin-多线程-重写run方法.py

        except FileNotFoundError as f:
            print("第{}个文件下载时遇到错误，url为：{}：".format(index, img_src))
            print("报错：", f)
            raise

        except TypeError as e:
            print("第{}个文件下载时遇到错误，url为：{}：".format(index, img_src))
            print("报错：", e)

class MyThread(threading.Thread):
    """继承Thread类重写run方法创建新进程"""
    def __init__(self, func, args):
        """

        :param func: run方法中要调用的函数名
        :param args: func函数所需的参数
        """
        threading.Thread.__init__(self)
        self.func = func
        self.args = args

    def run(self):
        print('当前子线程: {}'.format(threading.current_thread().name))
        self.func(self.args[0], self.args[1])
        # 调用func函数
        # 因为这里的func函数其实是上述的main()函数，它需要2个参数；args传入的是个参数元组，拆解开来传入


if __name__ == '__main__':
    start = time.time()
    print('这是主线程：{}'.format(threading.current_thread().name))

    urls = get_all_image_url(2)  # 获取所有图片url列表
    thread_list = []  # 定义一个列表，向里面追加线程
    semaphore = threading.BoundedSemaphore(5) # 或使用Semaphore方法
    for t in urls:
        # print(i)

        m = MyThread(main, (t["index"], t["img_src"]))  # 调用MyThread类，得到一个实例

        thread_list.append(m)

    for m in thread_list:

        m.start()  # 调用start()方法，开始执行

    for m in thread_list:
        m.join()  # 子线程调用join()方法，使主线程等待子线程运行完毕之后才退出


    end = time.time()
    print(end-start)
    # get_image_pages("https://imgbin.com/free-png/Naruto")