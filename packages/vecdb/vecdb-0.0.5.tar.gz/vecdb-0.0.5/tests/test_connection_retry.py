import time
import vecdb

from vecdb.api.api import retry


@retry(num_of_retries=2, timeout=1)
def fail_function(test_client: vecdb.Client):
    raise ConnectionResetError(104, "Connection reset by peer")


def test_retry_error(test_client):
    t1 = time.time()
    try:
        fail_function(test_client)
    except Exception as e:
        print(e)
        pass
    t2 = time.time()
    assert (t2 - t1) > 1
