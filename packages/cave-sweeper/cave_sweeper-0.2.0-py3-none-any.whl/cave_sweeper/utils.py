import os

def count_digits(n):
    count=0

    while n > 0:
        count=count+1
        n = n // 10

    return count


def set_env_var(env_var, value):
    os.environ[env_var] = value