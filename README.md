# flask-crawler
爬虫与flask相结合实现自己的微网站

# 爬取小说
爬取站点: 
笔趣阁 : https://www.qu.la/paihangbang/
选书网 : http://www.xuanshu.com

# 数据库模型
ebooks
id : 使用站点+书 形成主键
书名 : book_name
作者 : author
书封面 : book_image
最后更新时间 : last_since
最新更新时间 : new_since
简介 : about_book
存储地址 : address