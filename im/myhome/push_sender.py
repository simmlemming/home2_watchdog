from im.myhome.config import push_server_key
import im.myhome.log as log
import urllib.request as http
import urllib.error
import json


def send_to_all(devices, message):
    if len(devices) == 0:
        log.i('No devices registered for push notifications')

    for name, token in devices:
        log.i('Sending to %s:' % name)
        log.i(message)
        status_code, error = send_to_one(token, message)

        if status_code == 200 and not error:
            log.i('\tSent')
        else:
            log.e('\tNot sent:')
            log.e('\t%s %s' % (status_code, error))


def process_response(status_code, response_body):
    if status_code != 200:
        return status_code, None

    success = response_body['success']

    if success == 1:
        return 200, None

    error = response_body['results'][0]['error']
    return status_code, error


def send_to_one(token, message):
    headers = {
        'Authorization': 'key=' + push_server_key,
        'Content-Type': 'application/json; UTF-8',
    }

    body = dict(to=token, data=dict(message=message))
    request = http.Request('https://fcm.googleapis.com/fcm/send',
                           json.dumps(body).encode('utf-8'), headers=headers)
    try:
        response = http.urlopen(request)

        response_body = response.read().decode('utf-8')  # str
        response_body = json.loads(response_body)  # dict

        return process_response(response.getcode(), response_body)
    except urllib.error.HTTPError as e:
        error_message = e.read().decode('utf-8')
        return e.getcode(), error_message


if __name__ == "__main__":
    log.init()
    t = "eJnbKeoRV4o:APA91bGZ7H0E9PUFI-rD96VAL4jMnpUn7_1wfgt8ofXT0noHGxihR9FsAKfCCypleg5VsSaTT37bAaSvHUoj3DL-0YIEm9Eep25r45vHov0A0eRBUTicfbNLBgM_wl3b1QXIJhJsVJpe"
    m = dict(data=dict(message_id="qwe"))

    send_to_all([('d1', t)], json.dumps(m))
    # __send_to_one("name", t, json.dumps(m))
