#!/usr/local/bin/python3

import io, imaplib, email, mimetypes, requests
from util import *

def fetch_email(delete=False):
    server = imaplib.IMAP4_SSL(config['imap']['host'])
    server.login(config['imap']['username'], config['imap']['password'])
    server.select('INBOX')
    response, items = server.search(None, "(UNSEEN)")
    messages = []
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
            messages.append(message)
            server.store(mail, '+FLAGS', ('\\Deleted' if delete else '\\Seen'))
        except Exception as e:
            log.error(log.exc(e))
    return messages        
  
def main():
    try:
        messages = fetch_email()
    except Exception as e:
        log.warning("Could not fetch mail: %s" % e)
        return
    log.info("Found %d messages" % len(messages))
    for message in messages:
        safe = False
        for address in config['addresses']:        
            if address in message['from']:
                safe = True
                break
        if not safe:
            log.info("Bad address: %s" % message['from'])
            continue
        entry = {}
        entry['entry_id'] = "new"
        entry['tags'] = ','.join(message['subject'].split(' '))
        entry['content'] = message['body']
        entry['date'] = message['date']    
        entry['location'] = default_name
        log.info(entry)
        files = None
        try:
            files = {'image_data': io.BytesIO(message['attachments'][0]['data'])}
        except KeyError:
            pass
        except Exception as e:
            log.error(log.exc(e))
        try:
            r = requests.post("http://localhost:%s/update" % config['port'], data=entry, files=files)
        except Exception as e:
            success = False
            log.error(log.exc(e))
        else:
            log.info("--> %s: %s" % (r.status_code, r.text))
                    

if __name__ == "__main__":
    main()
