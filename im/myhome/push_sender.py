from im.myhome.config import PUSH_API_KEY
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
    headers = {'Authorization': 'key=' + PUSH_API_KEY, 'Content-Type': 'application/json'}
    body = dict(to=token, data=dict(message=message))

    request = http.Request('https://gcm-http.googleapis.com/gcm/send',
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
    t = "dN94xGA5m0Y:APA91bFvqn8y758yfyX8ugqQShee_RVHCb8cMFkvijeDZNXTyrBnzTdVpApNTu6uvp81gv039YUN4RB-He9Tsby2uZqFbK_WPk8IJChQgFYEk_S5BmiwB82izKE8K_tbM99sIAgMimbf"
    m = dict(data=dict(message_id="qwe"))

    send_to_all([('d1', t)], json.dumps(m))
    # __send_to_one("name", t, json.dumps(m))
