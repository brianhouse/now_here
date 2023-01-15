#!/Users/house/Studio/now_here/venv/bin/python

import io, imaplib, email, mimetypes, requests
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
        log.info("Bad address: %s" % message['from'])
        return False
    entry = {}
    entry['entry_id'] = "new"
    entry['tags'] = ','.join(message['subject'].split(' ') + ["_email"])
    entry['content'] = message['body']
    entry['date'] = message['date']
    entry['location'] = None
    log.info(entry)
    files = None
    try:
        for item in message['attachments']:
            if '.txt' in item['filename']:
                txt = item['data'].decode('utf-8')
                txt = txt.replace("Created with https://highlighted.app\r\n", "")                
                txt = txt.replace("Highlights may be protected by copyright.\r\n\r\n\r\n", "")
                entry['content'] = txt if not entry['content'] else entry['content'] + "\n\n" + txt
            else:
                files = {'image_data': io.BytesIO(message['attachments'][0]['data'])}
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
