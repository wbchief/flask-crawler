# flask-crawler
爬虫与flask相结合实现自己的微网站

# 爬取小说
爬取站点: 
笔趣阁 : https://www.qu.la/paihangbang/
选书网 : http://www.xuanshu.com

# 数据库模型
ebooks
id : 
书名 : book_name
作者 : author
书封面 : book_image
最后更新时间 : last_since
最新更新 : new_chapter
简介 : about_book
书链接 : book_url
章节，与chapters关联 : chapter



chapters:
id 
chapter_name:章节名
chapter_url: 章节url
content: 内容
book_id : ebook外键

contents:
id 
content: 内容
chapter_id : 外键