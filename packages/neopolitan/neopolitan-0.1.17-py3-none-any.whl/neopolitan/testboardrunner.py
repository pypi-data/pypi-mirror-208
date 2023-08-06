import time
from threading import Thread
from queue import Queue

from neopolitan.neop import main, initialize_logger

# todo: doesn't this also need to listen tho??

def add_to_queue(q, e, t):
    time.sleep(t)
    q.put(e)

def runner():
    initialize_logger()

    events = Queue()
    t = Thread(target=main, args=(events,))
    t.start()

    Thread(target=add_to_queue, args=(events, 'speed fast', 1,)).start()
    Thread(target=add_to_queue, args=(events, 'speed 1.0', 2,)).start()
    Thread(target=add_to_queue, args=(events, 'speed banana', 3,)).start()
    Thread(target=add_to_queue, args=(events, 'say hello again', 5,)).start()
    # todo: test below
    Thread(target=add_to_queue, args=(events, 'wrap False', 10,)).start()
    Thread(target=add_to_queue, args=(events, 'wrap 1', 15,)).start()
    Thread(target=add_to_queue, args=(events, 'exit', 20,)).start()

    t.join() # no difference

runner()
