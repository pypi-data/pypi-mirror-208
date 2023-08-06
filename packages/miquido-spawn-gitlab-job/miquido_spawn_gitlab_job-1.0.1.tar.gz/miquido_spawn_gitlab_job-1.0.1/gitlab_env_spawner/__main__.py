import sys
from . import spawner


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


if __name__ == '__main__':
    print('wlaczony')
    spawner.spawn()
