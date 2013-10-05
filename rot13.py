# -*- coding: utf-8 -*-

import utils

from basehandler import BaseHandler


class Rot13(BaseHandler):
    def get(self):
        self.render('/templates/rot13.html')

    def post(self):
        t = self.request.get('text')
        self.render('/templates/rot13.html',
                    texts=utils.rot13(t))
