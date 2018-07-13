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
        t = parse_datestring(data['date'])
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
                        t = parse_datestring(value)
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
            entry_id = db.entries.insert({'t': t, 'location': location, 'tags': tags, 'content': content, 'has_image': has_image, 'patches': []})            
            app.logger.debug(entry_id)
        except Exception as e:
            app.logger.error(e)
            return False, e

    else:
        update = {'$set': {'t': t, 'tags': tags, 'content': content}}
        original_content = db.entries.find_one({'_id': ObjectId(entry_id)})['content']
        if content != original_content:
            t = get_t()
            patch = (t, get_reverse_patch(original_content, content))
            update['$push'] = {'patches': patch}
        try:
            db.entries.update_one({'_id': ObjectId(entry_id)}, update)
        except Exception as e:
            app.logger.error(e)
            return False, e

    return entry_id, None


def expand(entries):
    for entry in entries:
        try:
            entry['date'] = get_datestring(entry['t'])
            if 'patches' in entry:
                for patch in entry['patches']:
                    patch[0] = str(get_datestring(patch[0])).split(" ")[0]
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

##            

def depunctuate(s, exclude=None, replacement=''):
    p = string.punctuation
    if exclude:
        for c in exclude:
            p = p.replace(c, '')    
    regex = re.compile('[%s]' % re.escape(p))
    return regex.sub(replacement, s) 

##

def parse_datestring(string):
    """We are purposefully ignoring timezone and storing as if everything was UTC"""
    try:
        dt = parser.parse(string)
        t = calendar.timegm(dt.timetuple())
    except ValueError as e:
        app.logger.error(e)
        t = None
    return t

def get_t(dt=None):
    if not dt:
        dt = datetime.datetime.now()
    return calendar.timegm(dt.timetuple())

def get_datestring(t=None):
    if not t:
        t = get_t()
    return str(datetime.datetime.utcfromtimestamp(t))

##    

dmp = diff_match_patch.diff_match_patch()

def get_reverse_patch(original, new):
    patches = dmp.patch_make(new, original)    
    return dmp.patch_toText(patches)

def apply_reverse_patch(new, patch):
    patches = dmp.patch_fromText(patch)
    return dmp.patch_apply(patches, new)[0]