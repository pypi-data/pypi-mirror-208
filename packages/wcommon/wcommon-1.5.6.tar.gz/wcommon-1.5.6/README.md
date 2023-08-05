# This is my common Python tool classes.


### /data/apps/public/conf.ini content like:
```
[mysql]
host=example.com
port=3306
user=username
passwd=password
database=test
charset=utf8mb4
```

### Find the localhost internal network ip:
```python
from wcommon import *
ip = getLocalIp()
hostname = getLocalHostname()
```

### Decode unusual json string:
```python
from wcommon import *
line = """
{
    name:'java',
    system:'linux'
}
"""
result = dejson(line)
# output result
{"name":"java","system":"linux"}
```

```python
# check the reuquirement list
check_requirement(['requests','flask'])
```

### Operate mysql data:
```python
mysql = Mysql(configuraion_file="/data/apps/public/conf.ini", section="mysql")
```
```python
# query
rows = mysql.query("select * from example_table where status = %s order by id desc limit %s",(1,10))
for row in rows:
    print(row)
```

```python
# bulk_insert
mysql.bulk_insert("test.person",["name","age"],[["mahuateng",40],["liyanhong",39]])
```

```python
# bulk_insert
mysql.bulk_insert2("test.person",[{"name":"ma2","age":40},{"name":"liyanhong2","age":39},{"name":"ren"}] )
```


## Feature
### 1.3.5
Mysql insert语句执行的时候，忽略值为None的字段。

### 1.3.8
可以通过check_requirement方法检测依赖包是否已经安装，如果没有安装，则提示安装。