# -*- coding: utf-8 -*-

from basehandler import BaseHandler

import utils


class Welcome(BaseHandler):
    def get(self):
        ck = self.request.cookies.get('user')

        if utils.check_cookie(ck):
            self.render('/templates/welcome.html',
                        username=ck.split('|')[0])
        else:
            self.redirect('/blog/signup')
