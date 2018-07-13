#!/usr/bin/env python3

from util import config
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.objectid import ObjectId
from util.config import config

mongo = config['mongo']
client = MongoClient(mongo['host'], mongo['port'])
db = client[mongo['database']]

def make_indexes():
  try:
      db.entries.create_index("entry_id")
      db.features.create_index([("t_utc", DESCENDING)])      
  except Exception as e:
      log.error(log.exc(e))

if __name__ == "__main__":
  make_indexes()

"""
entry_id, tags, content, location, created

image?

"""

"""
DROP TABLE IF EXISTS entries;
CREATE TABLE entries (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    tags VARCHAR(255) DEFAULT NULL,
    content TEXT,   
    has_image BOOL DEFAULT 0,
    location CHAR(12) DEFAULT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    KEY(location),
    FULLTEXT(tags, content),
    FULLTEXT(tags)
) ENGINE=MyISAM;

DROP TABLE IF EXISTS versions;
CREATE TABLE versions (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    entry_id INTEGER NOT NULL,
    content TEXT,   
    location CHAR(12) DEFAULT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    KEY(entry_id)
) ENGINE=MyISAM;
"""


"""

design question:

do I actually need history? the idea was that it would be a diff history, and that it would be useful for static things, like the "now"

it would be cool ... but risky

and is it a separate table? so that's my question, how to nest

and how does that affect full text search?

so maybe store the complete content, and then a change history
so like append to an array, thats how to nest
https://docs.mongodb.com/manual/reference/operator/update/push/

so... what's the format for storing diffs? that isnt lossy at all?

diff = difflib.ndiff(t1.splitlines(True), t2.splitlines(True))
then apply  result = difflib.restore(diff, 1) sequentially to restore earlier versions

ok, but the diffs have to be indexed or something so theyre not the same size (or bigger) as the original
I mean, could gzip them. 

diff-match-patch

ok, this is working!

only thing is, according to this, I'm storing the original, and then applying these. I have to go in reverse.
got it. great.


tags, content, has_image, location, date

"""