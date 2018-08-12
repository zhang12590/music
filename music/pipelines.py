# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import pymongo
import pymongo.collection

class MusicPipeline(object):
    def process_item(self, item, spider):
        # with open('music.txt', 'ab') as f:
        #     text = json.dumps(dict(item), ensure_ascii=False) + '\n'
        #     f.write(text.encode('utf-8'))
        client = pymongo.MongoClient()
        db = client['music']
        # print(type(item.get('count')), type(item.get('name')))
        db['music163'].update({'id': item.get('id')}, {'$set': dict(item)}, True)
        return item
