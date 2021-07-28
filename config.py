import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my-secret-key'

    db_config = {
        'host' : 'localhost',
        'port' : '8889', 
        'user' : 'root', 
        'passwd' : 'root'
    }
