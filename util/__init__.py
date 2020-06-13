import os, calendar, string, re, geohash, datetime, diff_match_patch, yaml, shutil
from dateutil import parser
from .log_config import log, config

with open(os.path.join(os.path.dirname(__file__), "..", "places.yaml")) as f:
    y = yaml.safe_load(f)
    hash_to_name = y['hash_to_name']
    name_to_hash = y['name_to_hash']

dmp = diff_match_patch.diff_match_patch()

def get_reverse_patch(original, new):
    patches = dmp.patch_make(new, original)
    return dmp.patch_toText(patches)

def apply_reverse_patch(new, patch):
    patches = dmp.patch_fromText(patch)
    return dmp.patch_apply(patches, new)[0]

def depunctuate(s, exclude=None, replacement=''):
    p = string.punctuation
    if exclude:
        for c in exclude:
            p = p.replace(c, '')
    regex = re.compile('[%s]' % re.escape(p))
    return regex.sub(replacement, s)

def parse_datestring(string):
    """We are purposefully ignoring timezone and storing as if everything was UTC"""
    try:
        dt = parser.parse(string)
        t = calendar.timegm(dt.timetuple())
    except ValueError as e:
        app.logger.error(e)
        t = None
    return t

def get_t(dt=None):
    if not dt:
        dt = datetime.datetime.now()
    return calendar.timegm(dt.timetuple())

def get_datestring(t=None):
    if not t:
        t = get_t()
    return str(datetime.datetime.utcfromtimestamp(t))

def linkify(string):
    regex = r"(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    links = re.findall(regex, string)
    for link in links:
        string = string.replace(link[0], f'<a href="{link[0]}">{link[0]}</a>')
    return string
