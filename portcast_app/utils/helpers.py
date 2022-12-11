import logging
import time
from datetime import datetime
from functools import wraps, reduce

logger = logging.getLogger(__name__)


def exponential_backoff(exc, retries=3, delay=3, backoff=2):
    def outer_wrapper(f):
        @wraps(f)
        def inner_wrapper(*args, **kwargs):
            retry, exp_delay = retries, delay
            while retry > 0:
                try:
                    return f(*args, **kwargs)
                except exc as e:
                    retry_msg = f'{str(e)}. Retrying in {exp_delay} seconds... Retries left: {retry}'
                    logger.warning(retry_msg)
                    time.sleep(exp_delay)
                    retry -= 1
                    exp_delay *= backoff
            return f(*args, **kwargs)
        return inner_wrapper
    return outer_wrapper


'''
Takes a tuple of functions, and processes them from left to right
Result from each function is passed on to the next
'''
def compose(*fns):
    def compose(f,g):
        return lambda x: g(f(x))    # result from f(x) is passed to g as arg
    return reduce(compose, fns, lambda x : x)


'''for logging request metadata'''
def metadata_log(status_code, g):
    return {
        'latency': f"{'%.4f' % (datetime.utcnow() - g.request_timestamp_start).total_seconds()}s",
        'status': status_code
    }
