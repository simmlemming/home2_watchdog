import sqlite3
from sqlite3 import OperationalError
from im.myhome.utils import file_for_picture


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
