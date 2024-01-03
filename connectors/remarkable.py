#!/Users/house/Studio/now_here/venv/bin/python

import sys, os, paramiko, subprocess, json, PyPDF2, requests, datetime, io
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util import *


entries = []
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    log.info("Connecting...")    
    ssh.connect("remarkable.local", username="root", password=config['remarkable'])
    log.info("--> connected")

    log.info("Reading metadata...")
    command = 'grep -l "Quick sheets" /home/root/.local/share/remarkable/xochitl/*.metadata | xargs grep -L "trash"'
    log.info(command)
    stdin, stdout, stderr = ssh.exec_command(command)
    uuid = stdout.read().decode("utf-8").split(":")[0].split("/")[-1].split(".")[0].strip()
    if not len(uuid):
        log.error("Notebook not found")
        exit()
    else:
        log.info(f"UUID is {uuid}")

    command = f'cat /home/root/.local/share/remarkable/xochitl/{uuid}.content'
    stdin, stdout, stderr = ssh.exec_command(command)
    content = json.loads(stdout.read().decode("utf-8"))

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
        command = f"stat /home/root/.local/share/remarkable/xochitl/{uuid}/{entry['id']}.rm"
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode("utf-8")
        date = output.strip().split("\n")[-1].replace("Change: ", "").strip()
        if not len(date):
            # blank page
            del entries[i]
        else:
            entry['date'] = date
            i += 1
        if i == len(entries):
            break

    log.info("--> done")
    # print(json.dumps(entries, indent=4))


    log.info("Getting pdf content via HTTP...")
    try:
        if subprocess.run(["wget", f"http://remarkable.local/download/{uuid}/data.pdf", "-O", f"{DIR}/data.pdf"]).returncode:
            raise Exception("connection failed")
    except Exception as e:
        log.error(log.exc(e))
        exit()
    log.info("--> success")

    log.info("Compiling and posting...")
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
            log.info(json.dumps(data, indent=4))

            files = {'pdf_data': pdf_data}
            try:
                r = requests.post("https://localhost:%s/update" % config['port'], data=data, files=files, verify=False)
            except Exception as e:
                log.error(log.exc(e))
                exit()
            else:
                log.info("--> %s: %s" % (r.status_code, r.text))
                if r.status_code != 200:
                    exit()

    os.remove(f"{DIR}/data.pdf")        
    log.info("--> done")

    # # doesn't work. have to be manual for now.
    # log.info("Deleting old notebook...")
    # command = f"cat /home/root/.local/share/remarkable/xochitl/{uuid}.metadata | sed 's/\"visibleName\": \"Quick sheets\"/\"visibleName\": \"prev sheets\"/g' > temp && mv temp /home/root/.local/share/remarkable/xochitl/{uuid}.metadata"
    # print(command)
    # stdin, stdout, stderr = ssh.exec_command(command)    
    # command = f"cat /home/root/.local/share/remarkable/xochitl/{uuid}.metadata | sed 's/\"parent\": \"\"/\"parent\": \"trash\"/g' > temp && mv temp /home/root/.local/share/remarkable/xochitl/{uuid}.metadata"
    # print(command)
    # stdin, stdout, stderr = ssh.exec_command(command)    
    # log.info("--> done")

except Exception as e:
    log.error(log.exc(e))
    exit()
finally:
    stdin.close()
    ssh.close()

