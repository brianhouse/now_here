#!/Users/house/Studio/now_here/venv/bin/python

import sys, os, io, imaplib, email, mimetypes, requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util import *

def fetch_email(delete=False):
    server = imaplib.IMAP4_SSL(config['imap']['host'])
    server.login(config['imap']['username'], config['imap']['password'])
    server.select('INBOX')
    response, items = server.search(None, "(UNSEEN)")
    for mail in items[0].split():
        try:
            resp, data = server.fetch(mail, '(RFC822)')
            s = data[0][1].decode('utf-8')
            data = email.message_from_string(s)
            message = { 'to': data['to'],
                        'from': data['from'],
                        'subject': data['subject'],
                        'date': data['date'],
                        'body': None,
                        'html': None,
                        'attachments': []
                        }
            for part in data.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                filename = part.get_filename()
                if filename:
                    message['attachments'].append({'filename': filename, 'data': part.get_payload(decode=True)})
                else:
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        message['body'] = part.get_payload(decode=True).strip()
                    else:
                        ext = mimetypes.guess_extension(content_type)
                        if ext == '.ksh':
                            message['body'] = part.get_payload(decode=True).strip()
                        if ext == '.html':
                            message['html'] = part.get_payload(decode=True).strip()
            if type(message['body']) == bytes:
                message['body'] = message['body'].decode('utf-8')
            if type(message['html']) == bytes:
                message['html'] = message['html'].decode('utf-8')                
            if process_message(message):
                server.store(mail, '+FLAGS', ('\\Deleted' if delete else '\\Seen'))
            else:
                server.store(mail, '-FLAGS', ('\\Seen',))
        except Exception as e:
            log.error(log.exc(e))


def process_message(message):
    safe = False
    for address in config['addresses']:
        if address in message['from']:
            safe = True
            break
    if not safe:
        log.info("Skipping address: %s" % message['from'])
        return False
    try:
        entry = {}
        entry['entry_id'] = "new"
        entry['tags'] = ','.join(message['subject'].split(' ') + ["_email"])
        entry['content'] = message['body'] if message['body'] is not None else (strip_tags(message['html']) if message['html'] is not None else "")        
        entry['content'] = entry['content'].replace("--\r\nhttps://brianhouse.net <https://brianhouse.net/>", "")
        entry['content'] = entry['content'].replace("--\r\nhttps://brianhouse.net", "")
        entry['content'] = entry['content'].replace("--https://brianhouse.net", "")        
        entry['content'] = entry['content'].strip()
        entry['date'] = message['date']
        entry['location'] = None

        # if this is from reMarkable, need to refactor and use content for tags
        log.info("Sent from reMarkable")
        if 'reMarkable' in ''.join(entry['tags']):
            entry['tags'] = ','.join(entry['content'].strip().split("--")[0].split(' ') + ["_remarkable", "_email"])
            entry['content'] = ""
        log.info(entry)

        files = None
        for item in message['attachments']:
            ext = item['filename'].split('.')[-1].lower()
            if ext == 'txt':

                # handle attached .txt files from the highlighted app; should also work otherwise
                entry['tags'].append("_highlighted")
                txt = item['data'].decode('utf-8')
                txt = txt.replace("Created with https://highlighted.app\r\n", "")                
                txt = txt.replace("Highlights may be protected by copyright.\r\n\r\n\r\n", "")
                entry['content'] = txt if not len(entry['content']) else entry['content'] + "\n\n" + txt

            elif ext in ['jpg', 'jpeg', 'png', 'gif', 'tif', 'tiff', 'heic', 'heif', 'bmp', 'eps', 'webp']:
                files = {'image_data': io.BytesIO(message['attachments'][0]['data'])}
                log.info("--> attached image")

            elif ext == 'pdf':
                files = {'pdf_data': io.BytesIO(message['attachments'][0]['data'])}
                log.info("--> attached pdf")

    except (KeyError, IndexError):
        log.warning(log.exc(e))
    except Exception as e:
        log.error(log.exc(e))
        return False
    try:
        r = requests.post("https://localhost:%s/update" % config['port'], data=entry, files=files, verify=False)
    except Exception as e:
        log.error(log.exc(e))
        return False
    else:
        log.info("--> %s: %s" % (r.status_code, r.text))
        return True if r.status_code == 200 else False


if __name__ == "__main__":
    fetch_email()
