# -*- coding: utf-8 -*-

import webapp2

# Importing handlers
from mainpage import MainPage
from rot13 import Rot13
from blogfront import BlogFront
from signup import Signup
from welcome import Welcome
from login import Login
from logout import Logout
from newpost import NewPost
from postpage import PostPage
from flushcache import FlushCache


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/rot13', Rot13),
    ('/blog', BlogFront),
    ('/blog/signup', Signup),
    ('/blog/welcome', Welcome),
    ('/blog/newpost', NewPost),
    ('/blog/([0-9]+)', PostPage),
    ('/blog/login', Login),
    ('/blog/logout', Logout),
    ('/blog/flush', FlushCache)
], debug=True)
