import datetime
from typing import Optional

import DriverManager
from context import Context
from connections import Connections
from salesforce.sfapi import SFClient
import logging

_log = logging.getLogger('main')


def setup_env(envname) -> Optional[Context]:
    mde = Connections()
    env = mde.get_db_env(envname)
    if env is None:
        _log.error(f'Configuration for {envname} not found')
        exit(1)

    sf = SFClient()
    try:
        sf.login(env.consumer_key, env.consumer_secret, env.login, env.password, env.authurl)
    except Exception as ex:
        _log.error(f'Unable to connect to {env.authurl} as {env.login}: {str(ex)}')
        return None

    dbdriver = DriverManager.Manager().get_driver('postgresql')
    if not dbdriver.connect(env):
        return None
    return Context(env, dbdriver, sf)


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial
    return str(obj)


def dict_list_to_dict(alist, keyfield):
    assert(keyfield is not None)
    assert(alist is not None)

    result = dict()
    for item in alist:
        key = item[keyfield]
        result[key] = item
    return result


def sf_timestamp(t: datetime):
    s = t.isoformat()[0:19]
    s += '+00:00'
    return s


def parse_timestamp(t):
    return datetime.datetime.strptime(t[0:19], '%Y-%m-%dT%H:%M:%S')
