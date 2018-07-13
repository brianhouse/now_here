#!/usr/bin/env python3

import os, datetime, yaml, json
from flask import Flask, render_template, request
from mongo import db, ObjectId, DESCENDING

app = Flask(__name__)
with open(os.path.join(os.path.dirname(__file__), "places.yaml")) as f:
    y = yaml.load(f)
    hash_to_name = y['hash_to_name']
    name_to_hash = y['name_to_hash']
    default_name = y['default_name']
from entry import create_or_update, expand, apply_reverse_patch, get_datestring

@app.route("/")
def main():
    entry = {   '_id': "new",
                'tags': "",
                'content': "",
                'location': None, 
                'date': get_datestring().split('.')[0]
                }
    entries = [entry]    
    return render_template("page.html", entries=[entry], places=hash_to_name)

@app.route("/recent") 
def recent():
    entries = list(db.entries.find(None, {'_id': True, 'tags': True, 'content': True, 'location': True, 't': True}).sort([('t', DESCENDING)]).limit(100))
    expand(entries)
    return render_template("page.html", entries=entries, places=hash_to_name)

@app.route("/search/<int:page>") 
def search(page):
    q = request.args['q'] if 'q' in request.args else ''
    app.logger.debug(q)
    return "Search %s %s" % (page, q)

@app.route("/entries/<string:entry_id>") 
def entries(entry_id):
    entry = db.entries.find_one({'_id': ObjectId(entry_id)})
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