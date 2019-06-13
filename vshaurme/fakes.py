import os
import random
import datetime

from PIL import Image
from faker import Faker
from flask import current_app
from sqlalchemy.exc import IntegrityError

from vshaurme.extensions import db
from vshaurme.models import User, Photo, Tag, Comment, Notification

fake = Faker("ru_RU")


def fake_admin():
    admin = User(name='Grey Li',
                 username='greyli',
                 email='admin@helloflask.com',
                 bio=fake.sentence(),
                 website='http://greyli.com',
                 confirmed=True)
    admin.set_password('helloflask')
    notification = Notification(message='Hello, welcome to Vshaurme.', receiver=admin)
    db.session.add(notification)
    db.session.add(admin)
    db.session.commit()


def fake_user(count=10):
    for user_number in range(count):
        user = User(name=fake.first_name(),
                    confirmed=True,
                    username=fake.user_name(),
                    bio = fake.job(),
                    location=fake.city(),
                    website=fake.url(),
                    email=fake.ascii_free_email())
        user.set_password('123456')
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_follow(count=30):
    for _ in range(count):
        user = User.query.get(random.randint(1, User.query.count()))
        user.follow(User.query.get(random.randint(1, User.query.count())))
    db.session.commit()


def fake_tag(count=20):
    for tag_number in range(count):
        tag = Tag(name=fake.color_name())
        db.session.add(tag)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_photo(count=30, period=None):
    # photos
    upload_path = current_app.config['VSHAURME_UPLOAD_PATH']
    for photo_number in range(count):
        random_color = tuple([random.randint(0, 255) for i in range(0,3)])
        img = Image.new("RGB", (100, 100), random_color)
        filename = 'random_%d.jpg' % photo_number
        img.save('{0}/{1}'.format(upload_path, filename))
        if period:
            timestamp = fake.date_between(start_date=f"-{period}d", end_date="today")
        else:
            timestamp = fake.date_time_this_year()
        print(timestamp)
        photo = Photo(
            description=fake.text(),
            filename=filename,
            filename_m=filename,
            filename_s=filename,
            author=User.query.get(random.randint(1, User.query.count())),
            timestamp=timestamp
        )
        print('Photo created')
        # tags
        for j in range(random.randint(1, 5)):
            tag = Tag.query.get(random.randint(1, Tag.query.count()))
            if tag not in photo.tags:
                photo.tags.append(tag)

        db.session.add(photo)

    db.session.commit()


def fake_collect(count=50, period=None):
    if period:
        date = datetime.datetime.now() - datetime.timedelta(days=period)
        photo_query = Photo.query.filter(Photo.timestamp >= date)
    else:
        photo_query = Photo.query
    if not photo_query.count():
        pass

    for i in range(count):
        user = User.query.get(random.randint(1, User.query.count()))
        user.collect(photo_query[random.randint(0, photo_query.count()-1)])
    db.session.commit()


def fake_comment(count=100, period=None):
    if period:
        date = datetime.datetime.now() - datetime.timedelta(days=period)
        photo_query = Photo.query.filter(Photo.timestamp > date)
    else:
        photo_query = Photo.query
    if not photo_query.count():
        pass

    for i in range(count):
        comment = Comment(
            author=User.query.get(random.randint(1, User.query.count())),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            photo=photo_query[random.randint(0, photo_query.count()-1)]
        )
        db.session.add(comment)
    db.session.commit()
