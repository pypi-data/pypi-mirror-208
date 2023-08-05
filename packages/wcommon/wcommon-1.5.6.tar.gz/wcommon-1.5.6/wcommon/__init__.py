# coding=utf-8
from __future__ import division
import time as timetool
import datetime as datetime_tool
import requests
import json
import subprocess
import socket
import traceback
import os
import sys
import pymysql
import re
import configparser
from loguru import logger
import hashlib
import platform
import warnings

# from Crypto.Cipher import AES
# from binascii import b2a_hex

# reload(sys)
# sys.setdefaultencoding('utf8')
# logger.info("WARN:please configuration the configuraion_file variable")

configuration_file = "/data/apps/public/conf.ini"
configuration_path_prefix = "/data"
system = platform.system()
if system == "Darwin":
    configuration_path_prefix = os.path.expanduser("~")
configuration_file = "{}/apps/public/conf.ini".format(configuration_path_prefix)


def getConfig(config_file=None):
    warnings.warn("此方法已废弃，不推荐使用，请使用 get_config 替换。", DeprecationWarning)
    return get_config(config_file)


def execute_command(cmd):
    warnings.warn("此方法已废弃，不推荐使用，请使用 command 替换。", DeprecationWarning)
    return command(cmd)


def get_config(config_file=None):
    if config_file is None:
        config_file = configuration_file
    logger.info(configuration_file)
    import configparser
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


# for python2
# def execute_command2(cmd):
#     status,output = commands.getstatusoutput(cmd)
#     if status == 0:
#         status = True
#     else:
#         status = False
#
#     tempLines = output.split("\n")
#
#     lines = []
#
#     for e in tempLines:
#         t = e.strip()
#         if len(t) >0 :
#             lines.append(t)
#
#     return (status, output, lines)


# for python3
def execute_command3(cmd):
    warnings.warn("此方法已废弃，不推荐使用，请使用 command 替换。", DeprecationWarning)
    status, output = subprocess.getstatusoutput(cmd)
    if status == 0:
        status = True
    else:
        status = False

    temp_lines = output.split("\n")

    lines = []

    for e in temp_lines:
        t = e.strip()
        if len(t) > 0:
            lines.append(t)

    return status, output, lines


def command(cmd):
    """执行shell命令,并返回结果

    :param cmd:
    :return:
    """
    major = sys.version_info[0]
    if major == 2:
        proc = subprocess.Popen([cmd, ], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        return out
    else:
        status, output = subprocess.getstatusoutput(cmd)
        if status == 0:
            status = True
        else:
            status = False

        return status, output


# 将datetime转为timestamp
def timestamp(dt):
    return int(timetool.mktime(dt.timetuple()))


def set_logger_level(level):
    """设置loguru的日志级别

    Args:
        level: logger level,DEBUG,INFO,WARNING,ERROR....

    Returns:
        handler_id.
    """
    # 删去import logger之后自动产生的handler，不删除的话会出现重复输出的现象
    logger.remove()
    # 添加一个可以修改控制的handler
    handler_id = logger.add(sys.stderr, level=level)
    return handler_id


def parseCommandArguments(args):
    arg_dict = {}
    for argument in args:
        logger.debug("argument:" + argument)
        if argument.startswith("-D"):
            arg = argument[2:]

            idx = arg.find("=")

            k = arg[0:idx]
            v = arg[idx + 1:]
            arg_dict[k] = v
    return arg_dict


def wait_until(future_timestamp):
    logger.debug("futureTimestamp %s " % future_timestamp)

    now = datetime_tool.datetime.now()
    now_timestamp = timestamp(now)

    logger.debug("nowTimestamp %s " % now_timestamp)

    if now_timestamp < future_timestamp:
        d = future_timestamp - now_timestamp
        timetool.sleep(d)


# 获取redisCluster的对象
# def getRedisCluster(redisClusterStr):
#     from rediscluster import StrictRedisCluster
#     logger.debug(redisClusterStr)
#     redisCluster = []
#     for nodePort in redisClusterStr.split(","):
#         kv = nodePort.split(":")
#         node = {"host": kv[0], "port": kv[1]}
#         redisCluster.append(node)
#
#     logger.debug(redisCluster)
#     rc = StrictRedisCluster(startup_nodes=redisCluster, decode_responses=True)
#     return rc

# mysql some operations
def getDatabase(section="mysql"):
    try:
        import configparser
        import pymysql
        config = configparser.ConfigParser()
        config.read(configuration_file)
        host = config.get(section, "host")
        port = int(config.get(section, "port"))
        user = config.get(section, "user")
        password = config.get(section, "passwd")
        database = config.get(section, "database")
        charset = config.get(section, "charset")

        db = pymysql.connect(host=host, port=port, user=user, passwd=password, db=database, charset=charset,
                             autocommit=True,
                             cursorclass=pymysql.cursors.DictCursor)
        return db
    except ImportError:
        logger.error("Error: configparser or pymysql module not exists")
    except Exception as e:
        logger.error(e)
        traceback.print_exc()

    return None


def query(database, sql, argumentTuple=(), timestamp2str=True):
    import pymysql
    cursor = database.cursor()
    logger.debug("query sql:\t%s, arguments: %s" % (sql, argumentTuple))
    if len(argumentTuple) == 0:
        cursor.execute(sql)
    else:
        cursor.execute(sql, argumentTuple)
    rows = []

    if timestamp2str:
        timestamp_field_array = []
        date_field_array = []
        for tp in cursor.description:
            if tp[1] == pymysql.constants.FIELD_TYPE.TIMESTAMP or tp[1] == pymysql.constants.FIELD_TYPE.DATETIME:
                timestamp_field_array.append(tp[0])
            elif tp[1] == pymysql.constants.FIELD_TYPE.DATE:
                date_field_array.append(tp[0])

        for row in cursor:
            for field in timestamp_field_array:
                if row[field] is not None:
                    tmp_value = row[field].strftime("%Y-%m-%d %H:%M:%S")
                    row[field] = tmp_value

            for field in date_field_array:
                if row[field] is not None:
                    tmp_value = row[field].strftime("%Y-%m-%d")
                    row[field] = tmp_value
            rows.append(row)
    else:
        for row in cursor:
            rows.append(row)
    return rows


def insert(database, tableName, dic, commit=True):
    cursor = database.cursor()
    cols = []
    vals = []
    placeholders = []
    doc_id = ""
    for key in dic.keys():
        val = dic[key]
        if val is not None:
            cols.append(key)
            placeholders.append("%s")
            vals.append(val)
    insert_sql = "INSERT INTO " + tableName + " ( %s ) VALUES ( %s )" % (",".join(cols), ",".join(placeholders))
    logger.debug(insert_sql)

    if commit:
        logger.info(tuple(vals))
        cursor.execute(insert_sql, tuple(vals))
        doc_id = cursor.lastrowid
    if commit:
        database.commit()

    return doc_id


def updateById(database, tableName, id, dic, idFieldName="id", commit=True):
    cursor = database.cursor()
    vals = []
    placeholders = []
    for key in dic.keys():
        val = dic[key]
        if val is not None:
            placeholders.append("{} = %s ".format(key))
            vals.append(val)
    setting = " , ".join(placeholders)
    vals.append(id)
    update_sql = "update {0} set {1} where {2} = %s ".format(tableName, setting, idFieldName)
    logger.debug(update_sql)

    if commit:
        logger.debug(tuple(vals))
        cursor.execute(update_sql, tuple(vals))
    if commit:
        database.commit()


def execute(database, sql, argumentTuple=()):
    cursor = database.cursor()
    logger.debug("query sql:\t%s, arguments: %s" % (sql, argumentTuple))
    if len(argumentTuple) == 0:
        cursor.execute(sql)
    else:
        cursor.execute(sql, argumentTuple)


def delete(database, sql, commit=True):
    cursor = database.cursor()
    logger.debug("delete sql:\t" + sql)
    if commit:
        cursor.execute(sql)
        database.commit()


def mysql_execute(database, sql, argumentTuple, commit=True):
    cursor = database.cursor()
    if argumentTuple:
        cursor.execute(sql, argumentTuple)
    else:
        cursor.execute(sql)
    if commit:
        database.commit()


# 获取文件的创建时间
def getFileCreateTime(filePath):
    # filePath = unicode(filePath,'utf8')
    t = os.path.getctime(filePath)
    return datetime_tool.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


# 获取文件的访问时间
def getFileAccessTime(filePath):
    # filePath = unicode(filePath,'utf8')
    t = os.path.getatime(filePath)
    return datetime_tool.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


# 获取文件的修改时间
def getFileModifyTime(filePath):
    # filePath = unicode(filePath,'utf8')
    t = os.path.getmtime(filePath)
    return datetime_tool.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


def getHost(url):
    begin_index = url.find("//")
    end_index = url.find("/", begin_index + 2)
    host = url[begin_index + 2:end_index]
    return host


def getHostname(url):
    begin_index = url.find("//")
    end_index = url.find(":", begin_index + 2)
    if end_index < 0:
        end_index = url.find("/", begin_index + 2)
    hostname = url[begin_index + 2:end_index]
    return hostname


def getFileSize(filePath):
    fsize = os.path.getsize(filePath)
    return fsize


def getFilePrefix(path):
    return os.path.splitext(path)[0]


def getFilePostfix(path):
    return os.path.splitext(path)[1][1:]


def getLocalHostname():
    hostname = ""
    try:
        hostname = socket.gethostname()
    except Exception as e:
        logger.debug(e)
        traceback.print_exc()
    return hostname


def getLocalIp():
    ip = ""
    try:
        # ip=socket.gethostbyname(socket.gethostname())
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        logger.debug(e)
        traceback.print_exc()
    return ip


def get_external_ip():
    # 这里的-s参数目的是在进行网络请求的时候禁止在控制台输出进度
    proc = subprocess.Popen(["curl -s https://api.hohode.com/ip"], stdout=subprocess.PIPE, shell=True)
    (outer_ip, err) = proc.communicate()
    if isinstance(outer_ip, bytes):
        outer_ip = outer_ip.decode("utf8")
    return outer_ip


def ding_send_text(message, token=None, mobiles=[], is_at_all=False):
    logger.warning("Sorry, this method is deprecated !")


def eweixin_send_text(message, token=None, mobiles=[], is_at_all=False):
    weixin_send_text(message, token, mobiles, is_at_all)


def weixin_send_text(message, token=None, mobiles=[], is_at_all=False):
    if not token:
        config = get_config()
        token = config.get("eweixin", "token")
    content = "{}[{}]\n{}".format(getLocalHostname(), getLocalIp(), message)
    data = json.dumps({"msgtype": "text", "text": {"content": content, "mentioned_mobile_list": mobiles}})
    requests.post("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=" + token, data,
                  auth=('Content-Type', 'application/json'))


def get_md5_code(arg, is_file=False):
    return md5(arg, is_file=is_file)


def md5(arg, is_file=False):
    """
    :param arg: 原始字符串，或者文件路径
    :param is_file: 如果为True，就对文件做md5处理
    :return : 对原始字符串进行MD5加密的字符串
    """
    content = arg
    m = hashlib.md5()
    temp_file = None
    if is_file:
        temp_file = open(arg, 'rb')
        content = temp_file.read()
    elif type(arg) is str:
        content = arg.encode(encoding='utf-8')
    m.update(content)
    if temp_file is not None:
        temp_file.close()
    return m.hexdigest()


# def aes(text,apiSecret):
#     """
#     AES加密
#     :param text:text
#     :param apiSecret:apiSecret
#     :return: AES加密后的字符串
#     """
#     key = apiSecret[:16].encode('gbk')# 密匙，apiSecret的前十六位
#     iv = apiSecret[16:].encode('gbk')# 偏移量，apiSecret的后十六位
#     mycipher = AES.new(key, AES.MODE_CBC, iv)
#     # 加密的明文长度必须为16的倍数，如果长度不为16的倍数，则需要补足为16的倍数
#     # 将iv（密钥向量）加到加密的密文开头，一起传输
#     ciphertext = iv + mycipher.encrypt(text.encode())
#     e = b2a_hex(ciphertext)[32:].decode() # 加密后
#     return e  # 加密

def dejson(content):
    """
    :param content: 非标准Json字符串，像JavaScript的类Json字符串那样
    :return: 标准的Json字符串
    """
    tmp_content = re.sub("\\s+", "", content)
    tmp_content = re.sub(":'", r':"', tmp_content)
    tmp_content = re.sub("':", r'":', tmp_content)
    tmp_content = re.sub("',", r'",', tmp_content)
    tmp_content = re.sub(",'", r',"', tmp_content)
    tmp_content = re.sub("[{]'([a-zA-Z]{2,})", r'{"\1', tmp_content)

    tmp_content = re.sub("\\['", r'["', tmp_content)
    tmp_content = re.sub("'}", r'"}', tmp_content)
    tmp_content = re.sub("']", r'"]', tmp_content)

    # tmp_content = re.sub("[{]([a-zA-Z])", r'{"\1', tmp_content)
    tmp_content = re.sub("""[{]([a-zA-Z])""", r'{"\1', tmp_content)
    tmp_content = re.sub("\\b([a-zA-Z])(\\w+):", r'\1\2":', tmp_content)
    tmp_content = re.sub(",([a-zA-Z])", r',"\1', tmp_content)
    return tmp_content


def check_requirement(requirement_list):
    """检查依赖包是否已经安装，如果还未安装，则提示安装。

    Args:
        requirement_list: 依赖包list
    """
    for package in requirement_list:
        try:
            exec("import {0}".format(package))
            logger.info("Requirement {} already!".format(package))
        except ModuleNotFoundError:
            inquiry = input("This script requires {0}. Do you want to install {0}? [y/n]".format(package))
            while (inquiry != "y") and (inquiry != "n"):
                inquiry = input("This script requires {0}. Do you want to install {0}? [y/n]".format(package))
            if inquiry == "y":
                import os
                logger.info("Execute command: pip3 install {0}".format(package))
                os.system("pip3 install {0}".format(package))
            else:
                logger.info("{0} is missing, so the program exits!".format(package))
                exit(-1)


# reconnecting mysql , 参考 https://www.kingname.info/2017/04/17/decorate-for-method/
def pingmysql(original_function):
    def wrapper(self, *args, **kwargs):
        try:
            self.database.ping()
            if self.columns_dict is None:
                cursor = self.database.cursor()
                self.columns_dict = {}
                sql = "select TABLE_SCHEMA,TABLE_NAME,COLUMN_NAME,DATA_TYPE from information_schema.columns where 1 =1 and TABLE_SCHEMA not in ('information_schema','performance_schema','mysql','sys') "
                cursor.execute(sql)
                for row in cursor:
                    table_schema = row.get("TABLE_SCHEMA")
                    table_name = row.get("TABLE_NAME")
                    column_name = row.get("COLUMN_NAME")
                    k = '{}.{}.{}'.format(table_schema, table_name, column_name)
                    self.columns_dict[k] = row
            result = original_function(self, *args, **kwargs)
            return result
        except Exception as e:
            traceback.print_exc()
            return 'an Exception raised.'

    return wrapper


class Mysql():

    def __init__(self, configuraion_file=configuration_file, section="mysql"):
        self.default_database_name = ''
        self.database = None
        self.columns_dict = None
        try:
            config = configparser.ConfigParser()
            config.read(configuraion_file)
            host = config.get(section, "host")
            port = int(config.get(section, "port"))
            user = config.get(section, "user")
            password = config.get(section, "passwd")
            self.default_database_name = config.get(section, "database")
            charset = config.get(section, "charset")

            self.database = pymysql.connect(host=host, port=port, user=user, passwd=password,
                                            db=self.default_database_name,
                                            charset=charset, autocommit=True,
                                            cursorclass=pymysql.cursors.DictCursor)

        except ImportError:
            logger.error("Error: configparser or pymysql module not exists")
        except Exception as e:
            logger.error(e)
            traceback.print_exc()

    def is_legal_value(self, table_name, column_name, val):
        if val is None:
            return True
        if "." not in table_name:
            table_name = "{}.{}".format(self.default_database_name, table_name)
        col_name = "{}.{}".format(table_name, column_name)
        if self.columns_dict is None:
            return True
        row = self.columns_dict.get(col_name)
        data_type = row.get("DATA_TYPE")
        if data_type in ['int', 'tinyint', 'bigint']:
            str_val = str(val)
            if len(str_val) == 0:
                logger.warning("{} {} is not a valid {}".format(column_name, val, data_type))
                return False
            elif str_val.startswith("-") or str_val.startswith("+"):
                unsigned_number = str_val[1:]
                if not unsigned_number.isnumeric():
                    raise Exception("{} {} is not a wrong {}".format(column_name, val, data_type))
                    return False
            elif not str(val).isnumeric():
                logger.error("{} {} is not a wrong {}".format(column_name, val, data_type))
                raise Exception("{} {} is not a wrong {}".format(column_name, val, data_type))
                return False
        return True

    @pingmysql
    def query(self, sql, argumentTuple=(), timestamp2str=True):
        cursor = self.database.cursor()
        logger.debug("query sql:\t%s, arguments: %s" % (sql, argumentTuple))
        if len(argumentTuple) == 0:
            cursor.execute(sql)
        else:
            cursor.execute(sql, argumentTuple)
        rows = []

        if timestamp2str:
            timestamp_field_array = []
            date_field_array = []
            for tp in cursor.description:
                if tp[1] == pymysql.constants.FIELD_TYPE.TIMESTAMP or tp[1] == pymysql.constants.FIELD_TYPE.DATETIME:
                    timestamp_field_array.append(tp[0])
                elif tp[1] == pymysql.constants.FIELD_TYPE.DATE:
                    date_field_array.append(tp[0])

            for row in cursor:
                for field in timestamp_field_array:
                    if row[field] is not None:
                        tmp_value = row[field].strftime("%Y-%m-%d %H:%M:%S")
                        row[field] = tmp_value

                for field in date_field_array:
                    if row[field] is not None:
                        tmp_value = row[field].strftime("%Y-%m-%d")
                        row[field] = tmp_value
                rows.append(row)
        else:
            for row in cursor:
                rows.append(row)
        return rows

    @pingmysql
    def insert(self, tableName, dic, commit=True):
        cursor = self.database.cursor()
        cols = []
        vals = []
        placeholders = []
        id = ""
        for key in dic.keys():
            val = dic[key]
            if val is not None and self.is_legal_value(tableName, key, val):
                cols.append(key)
                placeholders.append("%s")
                vals.append(val)
        insert_sql = "INSERT INTO " + tableName + " ( %s ) VALUES ( %s )" % (",".join(cols), ",".join(placeholders))
        logger.debug(insert_sql)

        if commit:
            logger.debug(tuple(vals))
            cursor.execute(insert_sql, tuple(vals))
            id = cursor.lastrowid
        if commit:
            self.database.commit()

        return id

    @pingmysql
    def update_by_id(self, tableName, id, dic, idFieldName="id", commit=True):
        """
        if want to change one field value to NULL, you should put {'fieldname':None} to dic.

        :param tableName:
        :param id:
        :param dic:
        :param idFieldName:
        :param commit:
        :return:
        """
        cursor = self.database.cursor()
        vals = []
        placeholders = []
        for key in dic.keys():
            val = dic[key]
            if val is None:
                placeholders.append("{} = null ".format(key))
            elif self.is_legal_value(tableName, key, val):
                placeholders.append("{} = %s ".format(key))
                vals.append(val)
        setting = " , ".join(placeholders)
        vals.append(id)
        update_sql = "update {0} set {1} where {2} = %s ".format(tableName, setting, idFieldName)
        logger.debug(update_sql)

        result = None
        if commit:
            logger.debug(tuple(vals))
            result = cursor.execute(update_sql, tuple(vals))
        if commit:
            self.database.commit()
        return result

    @pingmysql
    def execute(self, sql, argumentTuple=(), commit=True):
        cursor = self.database.cursor()
        logger.debug("query sql:\t%s, arguments: %s" % (sql, argumentTuple))
        if len(argumentTuple) == 0:
            cursor.execute(sql)
        else:
            cursor.execute(sql, argumentTuple)
        if commit:
            self.database.commit()

    @pingmysql
    def delete(self, sql, commit=True):
        cursor = self.database.cursor()
        logger.debug("delete sql:\t" + sql)
        if commit:
            cursor.execute(sql)
            self.database.commit()

    # Bulk Insert
    @pingmysql
    def bulk_insert(self, table_name, field_array, values_array, batch_size=100):
        field_line = ",".join(field_array)
        placeholder = ",".join(list(map(lambda x: "%s", field_array)))
        logger.info("insert bulk data ")
        ql = "INSERT INTO {} ({}) values ({})".format(table_name, field_line, placeholder)
        logger.debug(ql)
        cursor = self.database.cursor()
        for start in range(0, len(values_array), batch_size):
            logger.debug(values_array[start:start + batch_size])
            cursor.executemany(ql, values_array[start:start + batch_size])
            self.database.commit()

    # Bulk Insert
    @pingmysql
    def bulk_insert2(self, table_name, data, batch_size=100):
        """
        insert the object array to the table use mysql batch insert commit api

        :param table_name: table name
        :param data:  object array
        :param batch_size: size of batch to commit
        :return: no return value
        """
        field_array = data[0].keys()
        field_line = ",".join(field_array)
        placeholder = ",".join(list(map(lambda x: "%s", field_array)))
        logger.info("insert bulk data ")
        ql = "INSERT INTO {} ({}) values ({})".format(table_name, field_line, placeholder)
        logger.debug(ql)

        values_array = []
        for row in data:
            tmp_ar = []
            for i in field_array:
                val = row.get(i)
                tmp_ar.append(val)
            values_array.append(tmp_ar)
        logger.debug(values_array)
        cursor = self.database.cursor()
        for start in range(0, len(values_array), batch_size):
            logger.debug(values_array[start:start + batch_size])
            cursor.executemany(ql, values_array[start:start + batch_size])
            self.database.commit()


class ElasticSearch():
    """
    通过requests来访问ElasticSearch
    """

    def __init__(self, host, port=9200, username=None, password=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.urlPrefix = "http://{}:{}".format(host, port)

    headers = {
        'content-type': 'application/json'
    }

    def _transfer_data(self, data=None):
        if data is not None:
            if type(data) == str:
                return data
            elif type(data) == dict:
                return json.dumps(data)
        return None

    def search(self, action, data=None):
        data1 = self._transfer_data(data)
        return requests.get(url="{}{}".format(self.urlPrefix, action), auth=(self.username, self.password),
                            headers=self.headers, data=data1).json()

    def delete_by_query(self, index, data):
        """
        :param action: /sym/_delete_by_query
        :return:
        """
        data1 = self._transfer_data(data)
        return requests.post(url="{}/{}/_delete_by_query".format(self.urlPrefix, index),
                             auth=(self.username, self.password), headers=self.headers, data=data1)

    def delete(self, index, doc_id):
        return requests.delete(url="{}/{}/_doc/{}".format(self.urlPrefix, index, doc_id),
                               auth=(self.username, self.password))

    def put(self, action, data=None):
        """

        :param action:
        :param data:
        :return:
        """
        return self.post(action, data)

    def post(self, action, data=None):
        data1 = self._transfer_data(data)
        return requests.post(url="{}{}".format(self.urlPrefix, action), auth=(self.username, self.password),
                             headers=self.headers, data=data1)
