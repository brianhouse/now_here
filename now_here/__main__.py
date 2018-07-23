#!/usr/bin/env python3

import os, datetime, yaml, json
from flask import Flask, render_template, request
from mongo import db, ObjectId, DESCENDING
app = Flask(__name__)
from entry import *


@app.route("/")
def main():
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
    q = request.args['q']
    app.logger.debug("q=[%s]" % q)
    if not len(q):  
        app.logger.debug("RECENT")
        entries = list(db.entries.find(None, {'_id': True, 'tags': True, 'content': True, 'location': True, 't': True}).sort([('t', DESCENDING)]).limit(100))
        expand(entries)
        return render_template("page.html", entries=entries, places=hash_to_name)
    else:
        app.logger.debug("SEARCH")
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
            match.append({"$text": {"$search": full_text}})     
        if not len(match):
            pass
        query = {'$and': match}
        app.logger.debug(query)
        entries = list(db.entries.find(query, {'_id': True, 'tags': True, 'content': True, 'location': True, 't': True}).sort([('t', DESCENDING)]).limit(100))
        expand(entries)    
        search_string = " ".join(tags) + (" -" + " -".join(anti_tags) if len(anti_tags) else "") + (' "' + full_text + '"' if full_text else "")
        return render_template("page.html", entries=entries, places=hash_to_name, search_string=search_string.strip())

@app.route("/<string:entry_id>") 
def entries(entry_id):
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
    expand(entries)    
    return render_template("page.html", entries=entries, places=hash_to_name)

@app.route("/update", methods=['POST']) 
def update():
    success, e = create_or_update({key: value[0] for (key, value) in dict(request.form).items()})
    if not success:
        app.logger.error(e)
        return e, 400
    app.logger.debug("Success")
    return "Success"

@app.route("/delete", methods=['POST']) 
def delete():
    try:
        db.entries.delete_one({'_id': ObjectId(request.form['entry_id'])})
    except Exception as e:
        app.logger.error(e)
        return e, 400
    return "Success"
    

application = app
if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)