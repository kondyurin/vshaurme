import os
import requests

from flask import current_app
from flask_babel import lazy_gettext as _l

from wtforms import ValidationError

from transliterate import translit


def get_word_swear_level(word, lang):
    payload = {
            'txt': '{}'.format(word),
            'lang': lang
    }
    url = "https://tt-api.tech/1.0/profanity"
    headers = {'authorization': 'Token {}'.format(current_app.config['TT_API_TOKEN'])}
    response = requests.get(url, params=payload, headers=headers)
    data = response.json()
    swear_level = data['result']['level']
    return swear_level


def is_bad_username(self, field):
    langs = ['rus', 'eng']
    path = current_app.config['SWEAR_WORDS']
    if os.path.getsize(path) > 0:
        with open(path, 'r') as f:
            for word in f:
                if word.strip() in field.data:
                    raise ValidationError(_l("Please don't use swear words in username"))
    translit_word = translit(field.data, 'ru')
    for lang in langs:
        if get_word_swear_level(translit_word, lang) > 0:
            raise ValidationError(_l("Please don't use swear words in username"))