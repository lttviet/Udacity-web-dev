# -*- coding: utf-8 -*-

from google.appengine.ext import ndb


class Post(ndb.Model):
    subject = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(auto_now=True)


class User(ndb.Model):
    username = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    salt = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
