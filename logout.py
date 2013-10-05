# -*- coding: utf-8 -*-

from basehandler import BaseHandler


class Logout(BaseHandler):
    def get(self):
        self.logout()
        self.redirect('/blog')