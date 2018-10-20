import pymongo
import pymysql

client = pymongo.MongoClient('localhost', 27017)

novels = client['novels']

def create_database(dbname):
    '''
    创建数据库
    :param databasename:
    :return:
    '''
    databasename = client.database_names()
    if dbname in databasename:
        return databasename
    else:
        return client[dbname]


def get_list(list_name):
    '''
    判断novels数据库中list_name是否存在，
    存在返回集合对象，不存在则创建集合
    :param list_name: 集合名字
    :return: 集合
    '''
    collist = novels.list_collection_names()
    if list_name in collist:
        return novels.get_collection(list_name)
    else:
        return novels[list_name]

class SqlDB:
    def __init__(self):

        self.conn = pymysql.connect('localhost', 'flask_crawler', 'flask_crawler', 'flask_crawler')
        self.cursor = self.conn.cursor()
        self.sql_string = '''insert into ebooks(book_name, author, book_image, last_since, new_chapter, about_book, book_url) values("{0}","{1}", "{2}", "{3}", "{4}", "{5}", "{6}")'''

    def insert_data(self, data):
        '''
        插入数据
        :param data:
        :return:
        '''
        try:
            print(self.sql_string.format(data['book_name'], data['author'], data['book_image'],
                                                       data['last_since'], data['new_chapter'], data['about_book'], data['book_url']))

            self.cursor.execute(self.sql_string.format(data['book_name'], data['author'], data['book_image'],
                                                       data['last_since'], data['new_chapter'], data['about_book'], data['book_url']))
            self.conn.commit()
        except Exception as e:
            print(e.args)
            self.conn.rollback()
        finally:
            self.conn.close()

if __name__ == '__main__':
    #all_book = get_list('all_book')
    #all_book.delete_one({'book_name': '太古神王', 'book_url': 'https://www.qu.la/book/4140/'})
    print(novels.list_collection_names())
