# __author__ = 'Exter'


from functools import wraps
import time

def timed(f):
  @wraps(f)
  def wrapper(*args, **kwds):
    current_milli_time = lambda: int(round(time.time() * 1000))
    start = current_milli_time()
    result = f(*args, **kwds)
    elapsed = current_milli_time() - start
    print "%s took %d ms to finish" % (f.__name__, elapsed)
    return result
  return wrapper