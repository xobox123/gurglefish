from datetime import datetime

import decimal


def id(rec, name, fieldlen):
    if name in rec and rec[name] != None:
        if len(rec[name]) > 15:
            return rec[name][0:15]
        return rec[name]
    return None

def inte(rec, name, fieldlen):
    if name in rec and rec[name] != None:
        return rec[name]
    return None

def bl(rec, name, fieldlen):
    if name in rec and rec[name] is not None:
        return rec[name]
    return None

def dt(rec, name, fieldlen):
    if name in rec and rec[name] != None:
        return pyDate(rec[name])
    return None

def ts(rec, name, fieldlen):
    if name in rec and rec[name] != None:
        return pyTimestamp(rec[name])
    return None

def db(rec, name, fieldlen):
    if name in rec and rec[name] is not None:
        d = decimal.Decimal(rec[name])
        s = str(d)
        if fieldlen > 0 and len(s) > fieldlen:
            # truncate
            return float(s[0:fieldlen])
        return rec[name]
    return None

def st(rec, name, subname = None, fieldlen = 0):
    if name in rec and rec[name] != None:
        node = rec[name]
        if subname is not None:
            if subname in node:
                val = node[subname][0:fieldlen]
                return scrub(val)
            return None
        return scrub(node[0:fieldlen])
    return None


def pyTimestamp(t):
    return datetime.strptime(t[0:19], '%Y-%m-%dT%H:%M:%S')

def pyDate(d):
    return datetime.strptime(d, '%Y-%m-%d').date()

def scrub(s):
    s = s.replace('\\t',' ')
    if '\0' in s:
        s = ''.join([c for c in s if c != '\0'])
    return s