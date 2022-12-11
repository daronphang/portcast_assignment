import pytest
import logging
from unittest.mock import patch
from portcast_app.utils import exponential_backoff, BadRequest


logger = logging.getLogger(__name__)


def network_request():
    count = 0

    def fail_or_succeed(c):
        nonlocal count
        if count < c:
            count += 1
            raise BadRequest('network request failed')
        else:
            return 'network request succeeded'
    return fail_or_succeed


@patch('time.sleep', return_value=None)
def test_exponential_backoff(patched_time_sleep):

    nr = network_request()

    # default retry is 3 times 
    # 1. network request fails on 3 tries
    with pytest.raises(BadRequest) as exc:
        exponential_backoff(BadRequest)(nr)(4)
    assert str(exc.value) == 'network request failed'

    # reset enclosing namespace
    nr = network_request()

    # network request succeed on second try
    result = exponential_backoff(BadRequest)(nr)(1)
    assert result == 'network request succeeded'

    # reset enclosing namespace
    nr = network_request()

    # network request succeed on third try
    result = exponential_backoff(BadRequest)(nr)(2)
    assert result == 'network request succeeded'


    
    
    


