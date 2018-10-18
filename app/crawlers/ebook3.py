'''
保存到数据库
'''
from app.crawlers.novelsql import make_book_name, fail_list, success_list, all_list

'''
使用协程爬取
'''

import os
import random
import re
from datetime import datetime

import gevent
import requests
import time

from gevent import monkey
from pyquery import PyQuery as pq

from tools.chinesetoarab import chinese_to_digits

monkey.patch_all(False)
failedwaitlist = []
base_url = 'https://www.qu.la'
url = 'https://www.qu.la/paihangbang/'
pattern = re.compile(u'(第?([一二三四五六七八九零十百千万亿]+|[0-9]+)?章)')
def get_content(url):
    '''
    获取网页html
    :return:
    '''
    headers = {
        # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        # 'Accept-Encoding': 'gzip, deflate, br',
        # 'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }
    IPs = [
        {'HTTPS': 'https://115.237.16.200:8118'},
        {'HTTPS': 'https://42.49.119.10:8118'},
        {'HTTPS': 'http://60.174.74.40:8118'}
    ]
    ip = random.choice(IPs)
    try:
        response = requests.get(url, headers=headers, proxies=ip)
        if response.status_code == 200:
            return response.content.decode('utf-8')
    except Exception as e:
        failedwaitlist.append(url)
        time.sleep(2)
        print(e.args)

def parse_book():
    '''
    解析书籍主页
    :return:
    '''
    html = get_content(url)
    doc = pq(html)
    items = doc('#main div.mbottom').items()
    count = 0
    for item in items:
        lis = item.find('div:nth-child(2) > div:nth-child(1) > ul > li').items()
        for li in lis:
            count += 1
            href = li.find('a').attr('href')
            book_url = base_url + href
            book_name = li.find('a').text().strip()
            print(book_name, book_url)
            print('------------------------')
        print('+++++++++++++++++++++++++')
    print(count)

def parse_detals():
    '''
    解析详细资料页面
    :return:
    '''
    starttime = time.time()
    html = get_content('https://www.qu.la/book/4140/')
    doc = pq(html)
    div_info = doc('#maininfo div#info')
    name = div_info.find('h1').text().strip()
    print(div_info.find('p:nth-child(2)').text())
    author = div_info.find('p:nth-child(2)').text().replace('作  者：', '').strip()
    print(author)
    last_since = div_info.find('p:nth-child(4)').text().replace('最后更新：', '').strip()
    new_chapter = div_info.find('p:nth-child(5) > a').text().strip()
    about_book = doc('#maininfo div#intro').text().strip()
    image_url = base_url + doc('#fmimg > img').attr('src')
    # 章节
    list_name = author + '-' + name
    list_name = make_book_name(list_name)
    if not list_name:
        return
    for a in doc('div.box_con div#list > dl > dd:gt(11) > a').items():
        try:
            chapter_url = base_url + a.attr('href')
            chapter_name = a.text()
            chapter_num = pattern.search(chapter_name)
            if chapter_num is None:
                continue
            else:
                chapter_num = chapter_num.group(2)
                print(chapter_num)
                chapter_num = chinese_to_digits(chapter_num)
        except Exception as e:
            chapter_num = int(chapter_num)
            print(chapter_num)
        data = {
            "_id": chapter_num,
            "chapter_name": chapter_name,
            "chapter_url": chapter_url
        }
        try:
            list_name.insert_one(data)
        except Exception as e:
            print(e.args)
            fail_list.insert_one({"chapter_name": chapter_url})
    endtime = time.time()
    print(endtime-starttime)


def get_chapter_content(chapter_url):
    '''
    获取章节内容
    :param name: 书名
    :param chapter_name: 章节名
    :param chapter_url: 章节地址
    :return:
    '''
    html = get_content(chapter_url)
    if chapter_url in failedwaitlist:
        failedwaitlist.remove(chapter_url)
    doc = pq(html)
    chapter_name = doc('div.bookname > h1').text().replace(u'\xa0', u'')
    print(chapter_name)
    content = doc('#content').text().replace(u'\xa0', u' ')
    #content = content.replace('<br>', '')
    save_chapter(chapter_name, content, chapter_url)
    return content

def save_chapter(chapter_name, content, chapter_url):
    '''
    保存成文件
    :param chapter_name:
    :param content:
    :return:
    '''
    pattern = re.compile(u'(第?([一二三四五六七八九零十百千万亿]+|[0-9]+)?章)')
    #print(pattern.findall(chapter_name))
    try:
        chapter_num = pattern.search(chapter_name).group(2)
        print(chapter_num)
        chapter_num = chinese_to_digits(chapter_num)
        ebook_address = '/home/chief/python/flask-crawler/ebooks/'
        if not os.path.exists(ebook_address):
            os.mkdir(ebook_address)
        with open(ebook_address + '%s.txt' % chapter_num, 'w') as f:
            f.write(chapter_name + '\n  ' + content)
        print(ebook_address + '%s.txt' % chapter_num + '保存成功', chapter_name)
    except Exception as e:
        failedwaitlist.append(chapter_url)

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
    chapter_url, name = parse_detals()
    length = len(chapter_url)
    length = 100
    step = 100
    count = 0

    while count < length:
        print(count)
        waitlisted = [gevent.spawn(get_chapter_content, chapter_url[count + i]) for i in range(step) if count + i < length]
        gevent.joinall(waitlisted)
        count += step
    count = 0
    print('---------------------------------------------')
    print(failedwaitlist)
    while count < len(failedwaitlist):
        print(count)
        waited = [gevent.spawn(get_chapter_content, failedwaitlist[count + i]) for i in range(step) if count + i <len(failedwaitlist)]
        gevent.joinall(waited)
        count += step
    endtime = time.time()
    print(endtime-starttime)

def save_book():
    '''

    :return:
    '''
    name = '太古神王'
    chapterfile = list(
        filter(lambda x: x[:x.index('.')].isdigit(), os.listdir('/home/chief/python/flask-crawler/ebooks')))
    chapterfile.sort(key=lambda x: int(re.match('\d+', x).group()))
    for i in range(len(chapterfile)):
        with open('/home/chief/python/flask-crawler/ebooks/%d.txt' % (i + 1)) as f:
            string = f.read()
            if i == 0:
                with open('/home/chief/python/flask-crawler/ebooks/%s.txt' % name, 'w') as f:
                    f.write(string + '\n\n\n\n\n')
            else:
                with open('/home/chief/python/flask-crawler/ebooks/%s.txt' % name, 'a') as f:
                    f.write(string + '\n')
            os.remove('/home/chief/python/flask-crawler/ebooks/%d.txt' % (i + 1))


if __name__ == '__main__':
    #parse_book()
    parse_detals()
    #get_chapter_content('https://www.qu.la/book/4140/10570088.html')
    #main()
    #save_book()

