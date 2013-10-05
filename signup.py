# -*- coding: utf-8 -*-

import utils

from basehandler import BaseHandler


class Signup(BaseHandler):
    def get(self):
        self.render('/templates/signup.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        errors = utils.signup_errors(username, password, verify, email)

        if any(errors):
            self.render('templates/signup.html',
                        username=username,
                        email=email,
                        username_error=errors[0],
                        password_error=errors[1],
                        verify_error=errors[2],
                        email_error=errors[3])
        else:
            utils.create_user(username, password, email)
            self.set_cookie(username)
            self.redirect('/blog/welcome')
