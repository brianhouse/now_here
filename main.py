#!/usr/bin/env python3

import os, datetime, yaml, json, math, io
from flask import Flask, render_template, request
from mongo import db, ObjectId, DESCENDING
from PIL import Image
app = Flask(__name__)
from util import *


@app.route("/")
def main():
    app.logger.debug("/")        

    # new entry
    if not 'q' in request.args:
        app.logger.debug("NEW")
        entry = {   '_id': "new",
                    'tags': "",
                    'content': "",
                    'location': None, 
                    'date': get_datestring().split('.')[0]
                    }
        entries = [entry]    
        return render_template("page.html", entries=[entry], places=hash_to_name)

    # get request
    q = request.args['q']
    try:
        page = int(request.args['p']) if 'p' in request.args else 0
    except ValueError:
        page = 0

    # recent entries
    if not len(q):  
        app.logger.debug("RECENT page=%s" % (page,))
        entries = list(db.entries.find(None, {'_id': True, 'tags': True, 'content': True, 'location': True, 't': True, 'image': True}).sort([('t', DESCENDING)]).skip(page * 10).limit(100))
        search_string = ""

    # search
    else:
        app.logger.debug("SEARCH q=[%s] page=%s" % (q, page))
        tokens = q.split(',')
        tags = [tag for tag in tokens if len(tag) and tag[0] not in '-"' and len(tag)]
        anti_tags = [tag[1:] for tag in tokens if len(tag) and tag[0] == '-' and len(tag)]
        full_text = [tag.strip('"') for tag in tokens if len(tag) and tag[0] == '"' and len(tag) > 2]
        full_text = full_text[0] if len(full_text) else None
        match = []
        if len(tags):
            match.append({'tags': {'$all': tags}})
        if len(anti_tags):
            match.append({'tags': {'$nin': anti_tags}})
        if full_text:
            match.append({"$text": {"$search": '\"%s\"' % full_text}})     
        if not len(match):
            pass
        query = {'$and': match}
        app.logger.debug(query)
        entries = list(db.entries.find(query, {'_id': True, 'tags': True, 'content': True, 'location': True, 't': True, 'image': True}).sort([('t', DESCENDING)]).skip(page * 10).limit(100))
        search_string = " ".join(tags) + (" -" + " -".join(anti_tags) if len(anti_tags) else "") + (' "' + full_text + '"' if full_text else "")

    app.logger.debug("Found %d results" % len(entries))    

    # full response
    if page == 0:

        # create tag cloud
        cloud = []
        for entry in entries:            
            cloud.extend(entry['tags'])
        cloud = dict((s, cloud.count(s)) for s in set(cloud))    
        if len(cloud):                            
            min_count = min(cloud.values())
            max_count = max(max(cloud.values()), min_count + 1)
            for tag, count in cloud.items():
                cloud[tag] = int(math.ceil(((count - min_count) / (max_count - min_count)) * 5))
            cloud = list(cloud.items())
            cloud.sort(key=lambda c: c[0])
        else:
            cloud = None

        return render_template("page.html", entries=unpack(entries[:10]), places=hash_to_name, search_string=search_string.strip(), cloud=cloud)

    # partial response
    else:
        return render_template("content.html", entries=unpack(entries[:10]))


@app.route("/<string:entry_id>") 
def entry(entry_id):
    app.logger.debug("/(entry)")    
    if 'q' in request.args or 'p' in request.args:
        return ""
    entry = None
    try:
        entry = db.entries.find_one({'_id': ObjectId(entry_id)})
    except Exception as e:
        app.logger.warning(e)
    if entry is None:
        return "404 NOT FOUND", 404
    content = entry['content']
    patches = entry['patches']
    patches.sort(key=lambda x: x[0], reverse=True)
    for p, patch in enumerate(patches):
        entry['patches'][p] = [patch[0], apply_reverse_patch(content, patch[1])]
        content = entry['patches'][p][1]
    entries = [entry]
    return render_template("page.html", entries=unpack(entries), places=hash_to_name)


@app.route("/update", methods=['POST']) 
def update():

    # parse data
    app.logger.debug("/update")
    data = {key: value[0] for (key, value) in dict(request.form).items()}
    app.logger.debug(data)
    try:
        entry_id = data['entry_id']
        content = str(data['content']).strip()        
        t = parse_datestring(data['date']) if 'date' in data else get_t()
        tags = list(set(tag.lower().replace('.', '_') for tag in data['tags'].split(','))) if 'tags' in data else []
        location = data['location'] if 'location' in data else None
        if location is None or not len(location.strip()):
            location = default_name
        location = name_to_hash[location] if location in name_to_hash else location
        image = data['image'] if 'image' in data else None
        image_data = None
        if 'image_data' in request.files:        
            image_data = Image.open(request.files['image_data'].stream)
    except Exception as e:
        app.logger.error(e)
        return "Parsing failed", 400

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
            tags[i] = depunctuate(tag, exclude='_').lower()
    tags = [tag for tag in tags if tag is not None]

    # create new
    if entry_id == "new":
        try:
            entry_id = db.entries.insert({'t': t, 'location': location, 'tags': tags, 'content': content, 'patches': []})
            entry_id = str(entry_id)
            app.logger.debug("New entry: %s" % entry_id)
        except Exception as e:
            app.logger.error(e)
            return "Insert failed", 400
        if image_data:
            if not image:
                image = entry_id
            image_path = os.path.join(os.path.dirname(__file__), "static", "data", "images", str(image)[-1], "%s.png" % str(image))
            app.logger.debug("image_path: %s" % image_path)
            image_data.save(image_path)
            db.entries.update_one({'_id': ObjectId(entry_id)}, {'$set': {'image': image}})            

    # update
    else:
        update = {'$set': {'t': t, 'tags': tags, 'content': content}}     # if migrating, dont add t (and dont replace it below)
        original_content = db.entries.find_one({'_id': ObjectId(entry_id)})['content']
        if content != original_content:
            t = get_t()
            patch = (t, get_reverse_patch(original_content, content))
            update['$push'] = {'patches': patch}
        try:
            db.entries.update_one({'_id': ObjectId(entry_id)}, update)
        except Exception as e:
            app.logger.error(e)
            return "Update failed", 400

    return entry_id


@app.route("/delete", methods=['POST']) 
def delete():
    app.logger.debug("/delete")        
    try:
        db.entries.delete_one({'_id': ObjectId(request.form['entry_id'])})
    except Exception as e:
        app.logger.error(e)
        return "Delete failed", 400
    return "Success"
    

def unpack(entries):
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
            entry['folder'] = str(entry['image'])[-1]
        except Exception as e:
            app.logger.error(e)
            app.logger.debug(entry)
    return entries


application = app
if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)