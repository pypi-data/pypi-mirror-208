import sys
from gitlab_env_spawner import spawner


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


if __name__ == '__main__':
    spawner.spawn()
