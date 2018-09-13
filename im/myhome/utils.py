import os
import datetime

DATE_FORMAT = '%Y-%m-%d-%H-%M-%S'


def validate_device(token):
    return ('device_token' in token) & ('device_name' in token)


def rm(file):
    try:
        os.remove(file)
    except FileNotFoundError:
        pass


def file_for_picture_with_filename(file_name):
    return os.path.abspath('./p/' + file_name)


def dir_for_pictures():
    return os.path.abspath('./p')


def file_for_picture(camera_index):
    timestamp = datetime.datetime.today().strftime(DATE_FORMAT)
    file_with_picture = './p/' + camera_index + '.' + timestamp + '.jpg'

    dir_with_pictures = os.path.dirname(file_with_picture)
    if not os.path.exists(dir_with_pictures):
        os.makedirs(dir_with_pictures)

    return os.path.abspath(file_with_picture)
