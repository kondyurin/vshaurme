import os
import uuid
import requests
from lxml import etree
from transliterate import translit

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

import PIL
from PIL import Image
from flask import current_app, request, url_for, redirect, flash
from flask_babel import lazy_gettext as _l
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from vshaurme.extensions import db
from vshaurme.models import User
from vshaurme.settings import Operations


def generate_token(user, operation, expire_in=None, **kwargs):
    s = Serializer(current_app.config['SECRET_KEY'], expire_in)

    data = {'id': user.id, 'operation': operation}
    data.update(**kwargs)
    return s.dumps(data)


def validate_token(user, token, operation, new_password=None):
    s = Serializer(current_app.config['SECRET_KEY'])

    try:
        data = s.loads(token)
    except (SignatureExpired, BadSignature):
        return False

    if operation != data.get('operation') or user.id != data.get('id'):
        return False

    if operation == Operations.CONFIRM:
        user.confirmed = True
    elif operation == Operations.RESET_PASSWORD:
        user.set_password(new_password)
    elif operation == Operations.CHANGE_EMAIL:
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if User.query.filter_by(email=new_email).first() is not None:
            return False
        user.email = new_email
    else:
        return False

    db.session.commit()
    return True


def rename_image(old_filename):
    ext = os.path.splitext(old_filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


def resize_image(image, filename, base_width):
    filename, ext = os.path.splitext(filename)
    img = Image.open(image)
    if img.size[0] <= base_width:
        return filename + ext
    w_percent = (base_width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)

    filename += current_app.config['VSHAURME_PHOTO_SUFFIX'][base_width] + ext
    img.save(os.path.join(current_app.config['VSHAURME_UPLOAD_PATH'], filename), optimize=True, quality=85)
    return filename


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def redirect_back(default='main.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(_l(u"Error in the %s field - %s") % (
                getattr(form, field).label.text,
                error
            ))


def get_eng_swear_words():
    url = 'https://www.noswearing.com/dictionary/'
    alphabet = list('abcdefghijklmnopqrstuvwxyz')
    result = []
    for letter in alphabet:
        try:
            response = requests.get('{}{}'.format(url, letter))
        except request.exeptions.HTTPError:
            return None
        dom = etree.HTML(response.text)
        swear_words = dom.xpath('//a/@name')
        for swear_word in swear_words:
            if not swear_word is 'top':
                result.append(swear_word.replace("\\'", ''))  # TODO regex symbols
    return result


def get_rus_swear_words(word):
    translit_word = translit(word, 'ru')
    payload = {
        'txt': '{}'.format(translit_word),
        'lang': 'rus'
    }
    url = "https://tt-api.tech/1.0/profanity"
    headers = {'authorization': 'Token {}'.format(current_app.config['TT_API_KEY'])}
    response = requests.get(url, params=payload, headers=headers)
    data = response.json()
    swear_level = data['result']['level']
    return swear_level


def write_swear_words():
    path = current_app.config['SWEAR_WORDS']
    with open(path, 'w') as f:
        for line in get_eng_swear_words():
            f.write('{}\n'.format(line))