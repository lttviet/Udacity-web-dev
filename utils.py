# -*- coding: utf-8 -*-

import re
import string
import random

from database import Post, User

from Crypto.Hash import SHA256, HMAC
from datetime import datetime

from google.appengine.api import memcache

# To be changed in production
SECRET1 = ''
SECRET2 = ''


def rot13(text):
    "Increase every letter in a text by 13 then return a new text"

    new_text = ''
    for char in text:
        if char.isalpha():
            if char.isupper():
                new_text += chr((ord(char) - ord('A') + 13) % 26 + ord('A'))
            else:
                new_text += chr((ord(char) - ord('a') + 13) % 26 + ord('a'))
        else:
            new_text += char
    return new_text


def check_username(username):
    USER_RE = re.compile(r'^[a-zA-Z0-9_-]{3,20}$')
    return USER_RE.match(username)


def used_username(username):
    q = User.query(User.username == username)
    return q.get()


def check_password(password):
    PASSWORD_RE = re.compile(r'^.{3,20}$')
    return PASSWORD_RE.match(password)


def check_verify(password, verify):
    return password == verify


def check_email(email):
    EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
    return EMAIL_RE.match(email)


def signup_errors(username, password, verify, email):
    username_error = password_error = verify_error = email_error = ''

    if check_username(username) is None:
        username_error = 'Please enter a valid username'
    elif used_username(username):
        username_error = 'This username is already in use'

    if check_password(password) is None:
        password_error = 'Please enter a valid password'

    if not check_verify(username, verify):
        verify_error = 'Your passwords don\'t match'

    if email and check_email(email) is None:
        email_error = 'Please enter a valid email'
    return username_error, password_error, verify_error, email_error


def make_salt():
    return ''.join([random.choice(string.ascii_letters + string.digits)
                    for i in xrange(16)])


def hash_password(password, salt):
    h = HMAC.new(salt, password + SECRET1, SHA256)
    return h.hexdigest()


def make_cookie(username):
    h = HMAC.new(SECRET2, username, SHA256)
    return "{}|{}".format(username, h.hexdigest())


def check_cookie(cookie):
    username, hashed = cookie.split("|")
    return make_cookie(username) == cookie


def create_user(username, password, email):
    salt = make_salt()
    hashed = hash_password(password, salt)
    u = User(username=username,
             email=email,
             salt=salt,
             password=hashed)
    u.put()


def valid_password(input_password, salt, hashed):
    salt = salt.encode('ascii')
    hashed = hashed.encode('ascii')
    return hash_password(input_password, salt) == hashed


def login(username, password):
    u = User.query(User.username == username).get(use_cache=False)

    if u and valid_password(password, u.salt, u.password):
        error = ''
    else:
        error = 'Invalid login!'
    return error


def age_set(key, val):
    save_time = datetime.utcnow()
    memcache.set(key, (val, save_time))


def age_get(key):
    r = memcache.get(key)
    if r:
        val, save_time = r
        age = (datetime.utcnow() - save_time).total_seconds()
    else:
        val, age = None, 0
    return val, age


def add_post(post):
    post.put()
    get_posts(update=True)
    return str(post.key.id())


def get_posts(update=False):
    q = Post.query().order(-Post.created)
    q = q.fetch(10, use_cache=False, use_memcache=False)
    mc_key = 'BLOGS'

    posts, age = age_get(mc_key)
    if update or posts is None:
        posts = list(q)
        age_set(mc_key, posts)

    return posts, age


def age_str(age):
    s = 'Queried {}s seconds ago.'
    age = int(age)
    if age == 1:
        s = s.replace('seconds', 'second')
    return s.format(age)
