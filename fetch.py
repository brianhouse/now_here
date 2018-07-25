#!/usr/bin/env python3

import io, imaplib, email, mimetypes, requests
from util import config, default_name

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
            print(e)
    return messages        
  
def main():
    for message in fetch_email():
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
            r = requests.post("http://localhost:5000/update", data=entry, files=files)
        except Exception as e:
            success = False
            log.error(log.exc(e))
        else:
            log.info("--> %s: %s" % (r.status_code, r.text))
                    

if __name__ == "__main__":

    import os, logging, sys, logging.handlers

    name = "fetch"
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    log.propagate = False
    logdir = os.path.abspath(os.path.join(os.path.dirname(__file__), "logs"))
    if not os.path.isdir(logdir):
        os.makedirs(logdir)
    logfile = os.path.join(logdir, "%s.log" % name)
    logfile = logging.handlers.TimedRotatingFileHandler(logfile, 'midnight')    
    logfile.setLevel(logging.DEBUG)
    log.addHandler(logfile)
    formatter = logging.Formatter("%(asctime)s |%(levelname)s| %(message)s <%(filename)s:%(lineno)d>")            
    logfile.setFormatter(formatter)

    def exc(e):
        return "%s <%s:%s> %s" % (sys.exc_info()[0].__name__, os.path.split(sys.exc_info()[2].tb_frame.f_code.co_filename)[1], sys.exc_info()[2].tb_lineno, e)

    log.exc = exc   

    main()
