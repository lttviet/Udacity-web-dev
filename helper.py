import re
import string
import random
from Crypto.Hash import SHA256, HMAC
from SECRET import SECRET1, SECRET2


# Unit 1
def rot13(text):
    "Increase every letter in a text by 13 then return a new text"

    new_text = ""
    for char in text:
        if char.isalpha():
            if char.isupper():
                new_char = chr((ord(char) - ord('A') + 13) % 26 + ord('A'))
            else:
                new_char = chr((ord(char) - ord('a') + 13) % 26 + ord('a'))
            new_text += new_char
        else:
            new_text += char
    return new_text


# Unit 2
def valid_username(username):
    USER_RE = re.compile(r'^[a-zA-Z0-9_-]{3,20}$')
    return USER_RE.match(username)


def valid_password(password):
    PASSWORD_RE = re.compile(r'^.{3,20}$')
    return PASSWORD_RE.match(password)


def valid_email(email):
    EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
    return EMAIL_RE.match(email)


def signup_errors(username, password, verify, email):
    username_error = password_error = verify_error = email_error = ""
    if not valid_username(username):
        username_error = 'Please enter a valid username'

    if not valid_password(password):
        password_error = 'Please enter a valid password'

    if password != verify:
        verify_error = 'Your passwords don\'t match'

    if email and not valid_email(email):
        email_error = 'Please enter a valid email'
    return (username_error, password_error, verify_error, email_error)


# Unit 4
def make_salt():
    return ''.join([random.choice(string.ascii_letters + string.digits)
                    for i in xrange(16)])


def hash_pass(password, salt):
    h = HMAC.new(salt, password + SECRET1, SHA256)
    return h.hexdigest()


def valid_pass(input, salt, hashed_password):
    return hash_pass(input, salt) == hashed_password


def make_cookie(username):
    h = HMAC.new(SECRET2, username, SHA256)
    return "{}|{}".format(username, h.hexdigest())


def valid_cookie(cookie):
    username, hashed = cookie.split("|")
    return make_cookie(username) == cookie
