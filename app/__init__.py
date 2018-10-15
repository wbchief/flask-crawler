from flask_sqlalchemy import SQLAlchemy
from flask import Flask

from config import config_map

db = SQLAlchemy()

def create_app(config_name):
    '''
    创建app实例
    :param config_name:
    :return:
    '''
    app = Flask(__name__)
    config_class = config_map.get(config_name)
    app.config.from_object(config_class)
    # 初始化
    db.init_app(app)

    return app
