#!/Users/house/Studio/now_here/venv/bin/python

import sys, os, io, subprocess, json, PyPDF2, requests
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
    log.info("Getting tags...")        
    with open(os.path.join(DIR, filename)) as f:
        data = json.loads(f.read())
    os.remove(os.path.join(DIR, filename))
except Exception as e:
    log.error(log.exc(e))
    exit()
pages = {}
for page in data['cPages']['pages']:
    if 'deleted' in page:
        continue
    if page['id'] not in pages:
        pages[page['id']] = []
ids = list(pages.keys())        
for i, id in enumerate(ids):
    for tag in data['pageTags']:
        if tag['pageId'] == id:
            if tag['name'] == "cont":
                pages[id] = pages[ids[i-1]]
            else:
                pages[id].append(tag['name'])
log.info("--> done")

print(json.dumps(pages, indent=4))


log.info("Getting pages via HTTP...")
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
        # output_file_path = f"{DIR}/{ids[n]}.pdf"

        pdf_data = io.BytesIO()
        pdf_writer.write(pdf_data)
        pdf_data.seek(0)

        # with open(output_file_path, 'wb') as output_file:
        #     pdf_writer.write(output_file)

        # with open(output_file_path, "rb") as fh:
        #     pdf_data = io.BytesIO(fh.read())            


        entry = {}
        entry['entry_id'] = "new"
        entry['tags'] = ','.join(pages[ids[n]] + ["_remarkable"])
        entry['content'] = ""
        entry['date'] = None
        entry['location'] = None
        print(entry)

        files = {'pdf_data': pdf_data}
        try:
            r = requests.post("http://localhost:%s/update" % config['port'], data=entry, files=files, verify=False)
        except Exception as e:
            log.error(log.exc(e))
        else:
            log.info("--> %s: %s" % (r.status_code, r.text))

        break

os.remove(f"{DIR}/data.pdf")

## dammit, forgot creation times
## ...and then how to delete the files...

## annotated pdfs can just be emailed -- fix to accept my@remarkable.com, and make sure that it handles pdf attachments






# change tail back to false