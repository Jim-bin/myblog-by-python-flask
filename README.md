MyBlog
========

###Myblog by python flask

1. 实现了数据库的增删改查
2. 增加了代码高亮的功能
3. 使用七牛云作为图床

###Dependencies:

```
pip install flask

pip install flask-sqlalchemy
```

###Setup database:
```python
from app import db
db.create_all()
```

###Run:

python app.py

http://127.0.0.1:5000/

USERNAME: admin

PASSWORD: admin

###Demo

部署在了heroku上面了

[Demo](https://fendushu.herokuapp.com/)

![image](http://omahxqu4k.bkt.clouddn.com/2017-03-05_112750.jpg)

