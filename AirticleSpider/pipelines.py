# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import MySQLdb
import MySQLdb.cursors
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi

class AirticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item

class JSONWithEncodingPipeline(object):
    #自定义json导出
    def __init__(self):
        self.file = codecs.open('article.json','w',encoding='utf-8')
    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item
    def spider_closed(self, spider):
        self.file.close()

class JSONExporterPipeline(object):
    #调用scrapy提供的json exporter导出json文件
    def __init__(self):
        self.file = open('airticleexpoter.json','wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

class MysqlPipeline(object):
    #同步写入MySQL
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1', 'root' , 'srl' , 'article_spider' , charset="utf8" , use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_article(title,create_date,url,fav_nums)
            VALUES (%s,%s,%s,%s)
        """
        self.cursor.execute(insert_sql,(item["title"],item["create_date"],item["url"],item["fav_nums"]))
        self.conn.commit()

class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWORD"],
            charset = 'utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode = True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        #使用twisted将MySQL插入变为异步
        query = self.dbpool.runInteraction(self.do_insert,item)
        query.addErrback(self.handle_error)

    def handle_error(self,failure):
        #处理异步插入的异常
        print(failure)

    def do_insert(self,cursor,item):
        #执行具体插入
        insert_sql = """
                    insert into jobbole_article(title,create_date,url,url_object_id)
                    VALUES (%s,%s,%s,%s)
                """
        cursor.execute(insert_sql, (item["title"], item["create_date"], item["url"], item["url_object_id"]))



class AirticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            for ok,value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path
        return item