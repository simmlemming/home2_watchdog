import sqlite3
from sqlite3 import OperationalError
from im.myhome.utils import file_for_picture, file_for_picture_with_filename, dir_for_pictures
import datetime
import os
from im.myhome.utils import DATE_FORMAT

DATABASE_FILE_NAME = 'db.sqlite'
LAST_UPDATE_FILE_NAME = 'last_update.json'


def get_db():
    db = sqlite3.connect(DATABASE_FILE_NAME)
    db.execute('create table if not exists devices (name text primary key, token text)')
    return db


def get_all_devices():
    db = get_db()

    cursor = db.execute('select name, token from devices')

    devices = cursor.fetchall()
    db.close()

    return devices


def add_device(device):
    db = get_db()

    cursor = db.execute('insert or replace into devices values (?,?)', (device['name'], device['token']))
    added = cursor.rowcount == 1

    db.commit()
    db.close()

    if not added:
        raise OperationalError


def save_picture(camera_index, picture):
    file_with_picture = file_for_picture(camera_index)

    with open(file_with_picture, 'wb') as f:
        f.write(picture)

    return file_with_picture


def get_picture_by_name(file_name):
    with open(file_for_picture_with_filename(file_name), 'rb') as f:
        picture = f.read()

    return picture


def get_picture_by_timestamp(camera_index, timestamp):
    requested_timestamp = datetime.datetime.strptime(timestamp, DATE_FORMAT)
    picture_files = [f for f in os.listdir(dir_for_pictures()) if f.split('.')[0] == camera_index]
    picture_files.sort(key=__timestamp)

    requested_file = None

    for picture_file in picture_files:
        timestamp_of_file = __timestamp(picture_file)

        if requested_timestamp > timestamp_of_file:
            requested_file = picture_file
            continue

        break

    if requested_file:
        return get_picture_by_name(requested_file)

    return None


def __timestamp(file_name):
    timestamp_str = file_name.split('.')[1]
    return datetime.datetime.strptime(timestamp_str, DATE_FORMAT)
