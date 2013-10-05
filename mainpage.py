# -*- coding: utf-8 -*-

from basehandler import BaseHandler


class MainPage(BaseHandler):
    def get(self):
        self.render('/templates/mainpage.html')
