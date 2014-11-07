import logging
logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s %(funcName)s(%(filename)s:%(lineno)d)%(message)s",
    level=logging.DEBUG
)

import time
import threading
import signal

import tornado
import IPython

from katcp.testutils import DeviceTestServer

from katcp import resource_client


log = logging.getLogger(__name__)

ioloop = tornado.ioloop.IOLoop.current()

d = DeviceTestServer('', 0)
d.set_concurrency_options(False, False)
d.set_ioloop(ioloop)
ioloop.add_callback(d.start)

def setup_resource_client():
    global rc
    print d.bind_address
    rc = resource_client.KATCPResourceClient(dict(
        name='thething',
        address=d.bind_address,
        controlled=True
    ))
    rc.start()

ioloop.add_callback(setup_resource_client)

stop = threading.Event()

@tornado.gen.coroutine
def doreq(req, *args, **kwargs):
    print 'hi'
    try:
        rep = yield req(*args, **kwargs)
        print rep
    except Exception:
        print 'logging'
        log.exception('oops')
    finally:
        print 'blah'

def run_ipy():
    try:
        IPython.embed()
        # stop.wait(10000)
    finally:
        ioloop.stop()

t = threading.Thread(target=run_ipy)
t.start()

ioloop.set_blocking_log_threshold(0.1)
def ignore_signal(sig, frame):
    pass
# Disable sigint, since it stops the ioloop but not ipython shell ;)
signal.signal(signal.SIGINT, ignore_signal)
try:
    ioloop.start()
except KeyboardInterrupt:
    print 'Keyboard interrupt'
    stop.set()

