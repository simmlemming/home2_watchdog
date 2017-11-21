import im.myhome.push_sender as push_sender
import im.myhome.storage as storage


def notify(message):
    push_sender.send_to_all(storage.get_all_devices(), message)
