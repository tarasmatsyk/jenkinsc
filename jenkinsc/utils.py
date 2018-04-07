import json
from logging import getLogger
from time import sleep

from requests import ConnectTimeout, ConnectionError, HTTPError
from requests.packages.urllib3.exceptions import ReadTimeoutError

logger = getLogger('jenkinsc.utils')


def transform_jenkins_params(params):
    result_params = []
    for name, value in params.items():
        result_params.append({'name': name, 'value': value})
    if len(result_params) == 1:
        result_params = result_params[0]
    return {'json': json.dumps({'parameter': result_params})}


def lost_connection_wrapper(func):
    def wrapper(*args, **kwargs):
        for n in range(5):
            try:
                return func(*args, **kwargs)
            except (ConnectTimeout, ReadTimeoutError, ConnectionError):
                if n == 4:
                    raise
                logger.info('connection dropped, retrying in 15 sec')
                sleep(15)
            except HTTPError as err:
                if n == 4 or err.response.status_code != 504:
                    raise
                logger.exception('jenkins failed with gateway timeout')
                sleep(60)
    return wrapper