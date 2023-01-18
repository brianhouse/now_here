#!venv/bin/python

from util import config
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.objectid import ObjectId
from util import config

mongo = config['mongo']
client = MongoClient(mongo['host'], mongo['port'])
db = client[mongo['database']]

def make_indexes():
  try:
      db.entries.create_index([('t', DESCENDING)])  
      db.entries.create_index('tags')
      db.entries.create_index([('content', 'text')])    
  except Exception as e:
      log.error(log.exc(e))

if __name__ == "__main__":
  make_indexes()

"""
entry_id, tags, content, location, created

image?

"""
