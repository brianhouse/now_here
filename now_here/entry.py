import calendar, string, re, geohash, datetime
import diff_match_patch
from dateutil import parser
from pymongo import MongoClient
from __main__ import app, hash_to_name, name_to_hash, default_name
from mongo import db, ObjectId

def create_or_update(data):
    app.logger.debug("entry.create_or_update")
    app.logger.debug(data)
    try:
        entry_id = data['entry_id']
        tags = list(set(tag.lower().replace('.', '_') for tag in data['tags'].split()))
        content = str(data['content']).strip()
        location = data['location']
        if location is None or not len(location.strip()):
            location = default_name
        location = name_to_hash[location] if location in name_to_hash else location
        image = data['image'] if 'image' in data else None
        has_image = int(image is not None)
        t = parse_date(data['date'])
    except Exception as e:
        app.logger.error(e)
        return False, e    

    # unpack facet tags
    for i, tag in enumerate(tags):
        if ':' in tag:
            parts = tag.split(':')
            if len(parts) == 2:
                facet, value = parts[0], parts[1]
                if facet == 'date':
                    try:
                        t = parse_date(value)
                    except:
                        pass
                elif facet == 'place':
                    location = name_to_hash[value] if value in name_to_hash else value
            tags[i] = None
        else:
            tags[i] = depunctuate(tag, exclude='_')
    tags = [tag for tag in tags if tag is not None]

    app.logger.debug(entry_id)
    app.logger.debug(t)
    app.logger.debug(location)
    app.logger.debug(tags)
    app.logger.debug(content)
    app.logger.debug(has_image)

    if entry_id == "new":
        try:
            entry_id = db.entries.insert({'t': t, 'location': location, 'tags': tags, 'content': content, 'has_image': has_image})            
            app.logger.debug(entry_id)
        except Exception as e:
            app.logger.error(e)
            return False, e

    else:
        try:
            db.entries.update_one({'_id': ObjectId(entry_id)}, {'$set': {'tags': tags, 'content': content}})
        except Exception as e:
            app.logger.error(e)
            return False, e

    return entry_id, None


def expand(entries):
    for entry in entries:
        try:
            entry['date'] = datetime.datetime.fromtimestamp(entry['t'])
            if 'location' in entry and entry['location'] is not None:    
                place = hash_to_name[entry['location'][0:4]] if entry['location'][0:4] in hash_to_name else entry['location']
                lonlat = geohash.decode(entry['location'])
                entry['location'] = {'geohash': entry['location'], 'lonlat': lonlat, 'place': place}
            entry['tags'] = ' '.join(entry['tags'])        
            entry['content'] = entry['content'].replace('=\r\n', '').replace('=20=', '').replace('=20', '')
            # entry.folder = str(entry.id)[-1]
        except Exception as e:
            app.logger.error(e)
            app.logger.debug(entry)

def depunctuate(s, exclude=None, replacement=''):
    p = string.punctuation
    if exclude:
        for c in exclude:
            p = p.replace(c, '')    
    regex = re.compile('[%s]' % re.escape(p))
    return regex.sub(replacement, s) 

def parse_date(string):
    """We are purposefully ignoring timezone and storing as if everything was UTC"""
    try:
        dt = parser.parse(string)
        t = calendar.timegm(dt.timetuple())        
    except ValueError as e:
        app.logger.error(e)
        t = None
    return t

dmp = diff_match_patch.diff_match_patch()

def get_reverse_patch(original, new):
    patches = dmp.patch_make(new, original)    
    return dmp.patch_toText(patches)

def apply_reverse_patch(new, patch):
    patches = dmp.patch_fromText(patch)
    return dmp.patch_apply(patches, new)[0]