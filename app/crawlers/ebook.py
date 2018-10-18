import os
import re
from datetime import datetime

import requests
import time

from gevent import monkey
from pyquery import PyQuery as pq

from app import sheet_words
from tools.chinesetoarab import chinese_to_digits

monkey.patch_all(False)

base_url = 'https://www.qu.la'
url = 'https://www.qu.la/paihangbang/'
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
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.content
    except:
        time.wait(2)
        get_content(url)

def parse_book():
    '''
    解析书籍主页
    :return:
    '''
    html = get_content(url).decode('utf-8')
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
    time1 = datetime.now()
    html = get_content('https://www.qu.la/book/4140/').decode('utf-8')
    doc = pq(html)
    div_info = doc('#maininfo div#info')
    name = div_info.find('h1').text().strip()
    author = div_info.find('p:nth-child(2)').text().split('：')[1].strip()
    last_since = div_info.find('p:nth-child(4)').text().split('：')[1].strip()
    new_chapter = div_info.find('p:nth-child(5) > a').text().strip()
    about_book = doc('#maininfo div#intro').text().strip()
    image_url = base_url + doc('#fmimg > img').attr('src')
    #save_image(image_url, name+'-'+author)
    # 章节
    dds = doc('div.box_con div#list > dl > dd:gt(11)').items()
    for dd in dds:
        chapter_url = base_url + dd.find('a').attr('href')
        sheet_words.insert_one({'chapter_url': chapter_url})
        chapter_name = dd.find('a').text().strip()
        content = get_chapter_content(chapter_url)
        #print(chapter_name, chapter_url)
        #save_ebook(name, chapter_name, content)
        print(chapter_name, chapter_url, '保存成功')
        time.sleep(0.01)
    time2 = datetime.now()
    print(name, '保存成功', time2-time1)

def get_chapter_content(chapter_url):
    '''
    获取章节内容
    :param name: 书名
    :param chapter_name: 章节名
    :param chapter_url: 章节地址
    :return:
    '''
    html = get_content(chapter_url).decode('utf-8')
    doc = pq(html)
    chapter_name = doc('div.bookname > h1').text().strip()
    pattern = re.compile(u'(第?([一二三四五六七八九零十百千万亿]+|[0-9]+)?章)')
    chapter_num = pattern.search(chapter_name).group()
    print(pattern.search(chapter_name).group(2))
    #chapter_num = chinese_to_digits(chapter_num)
    print(chapter_num)
    content = doc('#content').text().strip().replace('&nbsp', ' ')
    return content

def save_ebook(name, chapter_name, content):
    '''
    保存成文件
    :param chapter_name:
    :param content:
    :return:
    '''
    ebook_address = '/home/chief/python/flask-crawler/ebooks'
    if not os.path.exists(ebook_address):
        os.mkdir(ebook_address)
    with open('/%s.txt'%name, 'a') as f:
        f.write(chapter_name + '\n' + content)


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




if __name__ == '__main__':
    #parse_book()
    parse_detals()
    #get_chapter_content('https://www.qu.la/book/4140/10570088.html')
