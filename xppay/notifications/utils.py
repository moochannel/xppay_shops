import json

import requests

from .models import Webhook


def send_notify(webhook_url, content):
    headers = {
        'Content-Type': 'multipart/form-data',
    }
    payload = json.dumps({
        'content': content,
    })
    requests.post(webhook_url, data=payload, headers=headers)


def spam_notify(content):
    for webhook in Webhook.active_objects.all():
        send_notify(webhook.url, content)
