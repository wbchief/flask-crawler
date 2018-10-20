'''
保存到数据库
'''
from requests import RequestException

from app.crawlers.novelsql import get_list, create_database, novels

'''
使用协程爬取
'''

import os
import random
import re

import gevent
import requests
import time

from gevent import monkey
from pyquery import PyQuery as pq


monkey.patch_all(False)
base_url = 'https://www.qu.la'
url = 'https://www.qu.la/paihangbang/'
pattern = re.compile(u'(第?([一二三四五六七八九零十百千万亿]+|[0-9]+)?章)')
IPs = [
        {'HTTPS': 'https://115.237.16.200:8118'},
        {'HTTPS': 'https://42.49.119.10:8118'},
        {'HTTPS': 'http://60.174.74.40:8118'}
    ]
headers = {
    # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    # 'Accept-Encoding': 'gzip, deflate, br',
    # 'Accept-Language': 'zh-CN,zh;q=0.9',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
}


#novels = create_database('novels')

def get_content(url):
    '''
    获取网页html
    :return:
    '''
    ip = random.choice(IPs)
    try:
        response = requests.get(url, headers=headers, proxies=ip)
        if response.status_code == 200:
            return response.content.decode('utf-8')
    except Exception as e:
        failedwaitlist.append(url)
        time.sleep(2)
        print(e.args)

def get_all_book():
    '''
    解析书籍主页
    :return:
    '''
    try:
        all_book = get_list('all_book')
        ip = random.choice(IPs)
        response = requests.get(url, headers=headers, proxies=ip)
        if response.status_code == 200:
            html = response.content.decode('utf-8')
            doc = pq(html)
            items = doc('#main div.mbottom').items()
            count = 1
            for item in items:
                lis = item.find('div:nth-child(2) > div:nth-child(1) > ul > li').items()
                for li in lis:
                    count += 1
                    href = li.find('a').attr('href')
                    book_url = base_url + href
                    book_name = li.find('a').text().strip()
                    data = {
                        'book_name': book_name,
                        'book_url': book_url
                    }
                    all_book.insert_one(data)
                    #print(data)
                    #print(count)
                    count += 1
            print('all_book over')
    except Exception as e:
        print(e.args)



def get_chapters_url(book_url, book_name):
    '''
    解析详细资料页面
    :return:
    '''
    data = {
        'book_name': book_name,
        'book_url': book_url
    }
    try:
        ip = random.choice(IPs)
        response = requests.get(book_url, headers=headers, proxies=ip)
        if response.status_code == 200:
            html = response.content.decode('utf-8')
            doc = pq(html)
            div_info = doc('#maininfo div#info')
            #name = div_info.find('h1').text().strip()
            author = div_info.find('p:nth-child(2)').text().replace('作  者：', '').strip()
            #print(author)
            last_since = div_info.find('p:nth-child(4)').text().replace('最后更新：', '').strip()
            new_chapter = div_info.find('p:nth-child(5) > a').text().strip()
            about_book = doc('#maininfo div#intro').text().strip()
            image_url = base_url + doc('#fmimg > img').attr('src')
            # 章节
            list_name = author + '-' + book_name
            list_name_db = get_list(list_name)
            #fail_book_db
            num = 1
            for a in doc('div.box_con div#list > dl > dd:gt(11) > a').items():
                    #print(num)
                    chapter_url = base_url + a.attr('href')
                    chapter_name = a.text()
                    #print(chapter_name)
                    data1 = {
                        "_id": num,
                        "chapter_name": chapter_name,
                        "chapter_url": chapter_url
                    }
                    list_name_db.insert_one(data1)
                    num += 1
            success_book = get_list('success_book')
            success_book.insert_one(data)
            all_book = get_list('all_book')
            print(data)
            result = all_book.delete_one({'book_name': book_name,
                                          'book_url': book_url})
            print(result.deleted_count, '------------------')
            #print(book_name, '所有目录链接已近爬取完毕------------------------')
            return author
    except RequestException as e:
        #爬取book失败则将book_url放入失败列表
        print(e.args)
        fail_book_db = get_list('fail_book')
        fail_book_db.insert_one(data)
        #print(book_name, '爬取目录链接失败------------------------')

    except Exception as e:
        print(e.args)
        print(book_name, '已爬取')


def get_chapter_content(chapter_success_list, chapter_fail_list, chapter_url, id, chapter_name):
    '''
    获取章节内容
    :param name: 书名
    :param chapter_name: 章节名
    :param chapter_url: 章节地址
    :return:
    '''
    success_db = get_list(chapter_success_list)
    fail_db = get_list(chapter_fail_list)
    data = {}
    data['num'] = id
    data['chapter_url'] = chapter_url
    data['chapter_name'] = chapter_name
    try:
        ip = random.choice(IPs)
        response = requests.get(chapter_url, headers=headers, proxies=ip)
        if response.status_code == 200:
            html = response.content.decode('utf-8')
            doc = pq(html)
            content = doc('#content').text()
            data['content'] = content
            success_db.insert_one(data)
            print(id, chapter_name, '爬取完毕')
    except RequestException as e:
        print(e.args)
        fail_db.insert_one(data)
    except Exception as e:
        print(e.args)
        print(chapter_name, '爬去失败')



def save_chapter(chapter_name, content, chapter_url):
    '''
    保存成文件
    :param chapter_name:
    :param content:
    :return:
    '''
    pass

def save_image(url, name):
    '''
    下载图片到/home/chief/python/flask-crawler
    :param url: 图片地址
    :param name: 图片名称
    :return:
    '''
    content = get_content(url)
    image_address = '/home/chief/python/flask-crawler/' + 'image'
    if not os.path.exists(image_address):
        os.mkdir(image_address)
    with open(image_address + '/%s.png' % name, 'wb') as f:
        f.write(content)
    print(name, url, '保存成功')


def main():
    starttime = time.time()
    # 获取全部小说的链接
    #get_all_book()
    all_book_db = novels.get_collection('all_book')
    count = 1
    for book in all_book_db.find():
        book_name = book.get('book_name')
        book_url = book.get('book_url')
        print('开始爬取%s'% book_name, '----------------------------')
        author = get_chapters_url(book_url, book_name)
        chapter_fail_list = author + '-' + book_name + '-fail'
        chapter_success_list = author + '-' + book_name + '-success'
        for bb in novels.list_collection_names():
            if 'book' in bb:
                continue
            book_db = get_list(bb)
            for col in book_db.find():
                id = col.get('_id')
                chapter_url = col.get('chapter_url')
                chapter_name = col.get('chapter_name')
                get_chapter_content(chapter_success_list, chapter_fail_list, chapter_url, id, chapter_name)

        print(book_name, '爬取完毕--------------------')
        print('\n'*5)
        time.sleep(1)
        count += 1
    print(count)
    endtime = time.time()
    print(endtime-starttime)



if __name__ == '__main__':
    get_all_book()
    main()
    #get_chapter_content('https://www.qu.la/book/17069/6826072.html')
