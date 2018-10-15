from app import db


class Ebooks(db.Model):
    '''
    ebook表
    '''
    __tablename__ = 'ebooks'
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(64), index=True)#书名
    author = db.Column(db.String(64), index=True)#作者
    book_image = db.Column(db.Binary)# 书封面
    last_since = db.Column(db.DateTime)# 最后更新时间
    new_chapter = db.Column(db.String(128)) # 最新章节
    about_book = db.Column(db.Text) #  简介
    book_url = db.Column(db.String(128)) #书链接
    chapter = db.relationship('Chapter', backref='ebook', lazy='dynamic')


class Chapter(db.Model):
    '''
    章节表
    '''
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key=True)
    chapter_name = db.Column(db.String(128))# 章节名
    chapter_url = db.Column(db.String(128))#章节url
    # 外键
    book_id = db.Column(db.Integer, db.ForeignKey('ebooks.id'))
    chapter_content = db.relationship('Content', backref='chapter', lazy='dynamic')


class Content(db.Model):
    '''
    章节内容
    '''
    __tablename__ = 'contents'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'))

