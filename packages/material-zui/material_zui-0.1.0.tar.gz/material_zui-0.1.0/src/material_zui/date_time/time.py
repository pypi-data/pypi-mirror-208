import threading
import time


def set_timeout(code, milliseconds):
    timer = threading.Timer(milliseconds / 1000, code)
    timer.start()
    return timer


def clear_timeout(timer):
    timer.cancel()


def my_code():
    print("Hello World!")


timer = set_timeout(my_code, 5)


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    # t = threading.Timer(sec, func_wrapper)
    t = threading.Timer(sec, func)
    t.start()
    return t


def clear_interval(t):
    print('cancel')
    t.cancel()


def print_hello():
    print("Hello!")


interval_id = set_interval(print_hello, 1)
time.sleep(5)
clear_interval(interval_id)
print('abc')
