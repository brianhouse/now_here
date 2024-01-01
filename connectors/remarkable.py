#!/Users/house/Studio/now_here/venv/bin/python

import sys, os, io, subprocess, json, PyPDF2, requests, datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util import *

# have to have it set up so "ssh remarkable" logs in with keys and no password

NOTEBOOK = "28aa63fb-517e-4695-8d69-9da712368d31"
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

log.info("Connecting...")
if not os.path.isdir(DIR):
    os.mkdir(DIR)
filename = f"{NOTEBOOK}.content"
try:
    if subprocess.run(["scp", f"root@remarkable:/home/root/.local/share/remarkable/xochitl/{filename}", DIR]).returncode:
        raise Exception("connection failed")
    log.info("--> connected")
    with open(os.path.join(DIR, filename)) as f:
        data = json.loads(f.read())
    os.remove(os.path.join(DIR, filename))
except Exception as e:
    log.error(log.exc(e))
    exit()
log.info("--> loaded notebook")

log.info("Getting tags and dates...")
tags = {}
for page in data['cPages']['pages']:
    if 'deleted' in page:
        continue
    if page['id'] not in tags:
        tags[page['id']] = []
ids = list(tags.keys())  
dates = {}      
for i, id in enumerate(ids):
    for tag in data['pageTags']:
        if tag['pageId'] == id:
            if tag['name'] == "cont":
                tags[id] = tags[ids[i-1]]
            else:
                tags[id].append(tag['name'])
    try:
        if subprocess.run(["scp", "-p", f"root@remarkable:/home/root/.local/share/remarkable/xochitl/{NOTEBOOK}/{id}.rm", DIR]).returncode:
            raise Exception("connection failed")
        path = f"{DIR}/{id}.rm"
        creation_time = os.stat(path).st_birthtime
        creation_time_dt = datetime.datetime.fromtimestamp(creation_time)
        creation_time_s = creation_time_dt.isoformat()
        if id not in dates:
            dates[id] = []
        dates[id].append(creation_time_s)
        os.remove(path)
    except Exception as e:
        log.error(log.exc(e))
        exit()
log.info("--> done")

# print(json.dumps(tags, indent=4))
# print(json.dumps(dates, indent=4))

log.info("Getting pdf content via HTTP...")
try:
    if subprocess.run(["wget", f"http://remarkable.local/download/{NOTEBOOK}/data.pdf", "-O", f"{DIR}/data.pdf"]).returncode:
        raise Exception("connection failed")
except Exception as e:
    log.error(log.exc(e))
    exit()
log.info("--> success")

with open(f"{DIR}/data.pdf", 'rb') as f:
    pdf_reader = PyPDF2.PdfReader(f)
    for n in range(len(pdf_reader.pages)):
        pdf_writer = PyPDF2.PdfWriter()
        pdf_writer.add_page(pdf_reader.pages[n])

        pdf_data = io.BytesIO()
        pdf_writer.write(pdf_data)
        pdf_data.seek(0)

        entry = {}
        entry['entry_id'] = "new"
        entry['tags'] = ','.join(tags[ids[n]] + ["_remarkable"])
        entry['content'] = ""
        entry['date'] = dates[ids[n]]
        entry['location'] = None
        print(entry)

        files = {'pdf_data': pdf_data}
        try:
            r = requests.post("http://localhost:%s/update" % config['port'], data=entry, files=files, verify=False)
        except Exception as e:
            log.error(log.exc(e))
        else:
            log.info("--> %s: %s" % (r.status_code, r.text))

os.remove(f"{DIR}/data.pdf")

## ...and then how to delete the files...

## check that emailing annotated pdfs works

# change tail back to false, and switch the port back


# it would actually be better to have the 'conts' combined
