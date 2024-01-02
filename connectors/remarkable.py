#!/Users/house/Studio/now_here/venv/bin/python

import sys, os, io, subprocess, json, PyPDF2, requests, datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util import *

# have to have it set up so "ssh remarkable" logs in with keys and no password

NOTEBOOK = config['notebook']
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
        content = json.loads(f.read())
    os.remove(os.path.join(DIR, filename))
except Exception as e:
    log.error(log.exc(e))
    exit()
log.info("--> loaded notebook")
print(json.dumps(content, indent=4))

log.info("Getting entry tags and dates...")
try:

    # get valid page ids
    entries = []
    for page in content['cPages']['pages']:
        if 'deleted' in page:
            continue
        entries.append({'id': page['id'], 'date': None, 'tags': [], 'children': []})

    # distribute tags
    for tag in content['pageTags']:
        for entry in entries:
            if tag['pageId'] == entry['id']:
                entry['tags'].append(tag['name'])

    # combine mutipage
    # (there is a race condition if run exactly two weeks between cont page creation
    # -- so make it 3am two weeks before or something)
    i = 0
    while True:
        if "cont" in entries[i]['tags']:
            entries[i-1]['children'].append(entries[i]['id'])
            del entries[i]
        else:
            i += 1
        if i == len(entries):
            break

    # pull .rm files to get creation times
    i = 0
    while True:
        entry = entries[i]
        if not subprocess.run(["scp", "-p", f"root@remarkable:/home/root/.local/share/remarkable/xochitl/{NOTEBOOK}/{entry['id']}.rm", DIR]).returncode:
            path = f"{DIR}/{entry['id']}.rm"
            entry['date'] = datetime.datetime.fromtimestamp(os.stat(path).st_birthtime).isoformat()            
            os.remove(path)
            i += 1
        else:
            # blank page (hopefully not a connection error)
            del entries[i]
        if i == len(entries):
            break
        

except Exception as e:
    log.error("Parsing error:" + log.exc(e))
    exit()        
log.info("--> done")
# print(json.dumps(entries, indent=4))


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
    p = 0
    for entry in entries:
        pdf_writer = PyPDF2.PdfWriter()
        for i in range(len(entry['children']) + 1):
            pdf_writer.add_page(pdf_reader.pages[p])
            p += 1

        pdf_data = io.BytesIO()
        pdf_writer.write(pdf_data)
        pdf_data.seek(0)

        data = {}
        data['entry_id'] = "new"
        data['tags'] = ','.join(entry['tags'] + ["_remarkable"])
        data['content'] = ""
        data['date'] = entry['date']
        data['location'] = None
        print(data)

        # files = {'pdf_data': pdf_data}
        # try:
        #     r = requests.post("http://localhost:%s/update" % config['port'], data=data, files=files, verify=False)
        # except Exception as e:
        #     log.error(log.exc(e))
        # else:
        #     log.info("--> %s: %s" % (r.status_code, r.text))

os.remove(f"{DIR}/data.pdf")

## ...and then how to delete the files...

## check that emailing annotated pdfs works

# change tail back to false, and switch the port back; relaunch

# test that mail is stripping my sig
# it would actually be better to have the 'conts' combined
