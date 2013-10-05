# -*- coding: utf-8 -*-

from basehandler import BaseHandler

from google.appengine.api import memcache


class FlushCache(BaseHandler):
    def get(self):
        memcache.flush_all()
        self.redirect('/blog')
