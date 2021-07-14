# cyberminer
OOAD course project su21

Requires a config.py file to read app and database config. include this file in gitignore

```
import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my-secret-key'

    db_config = {
        'host' : 'localhost',
        'port' : '', 
        'user' : 'root', 
        'passwd' : 'root'
    }
```