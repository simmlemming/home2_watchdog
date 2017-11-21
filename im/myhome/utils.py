import os


def validate_device(token):
    return ('device_token' in token) & ('device_name' in token)


def rm(file):
    try:
        os.remove(file)
    except FileNotFoundError:
        pass
