# -*- coding: utf-8 -*-

import os

import webapp2
import jinja2

import utils


JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape=True)


class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        t = JINJA_ENV.get_template(template)
        self.response.write(t.render(kw))

    def set_cookie(self, user):
        cookie = utils.make_cookie(user)
        self.response.headers.add_header(
            'Set-Cookie',
            'user={}; Path=/'.format(cookie))

    def logout(self):
        self.response.headers.add_header('Set-Cookie',
                                         'user=; Path=/')

    def get_username(self):
        cookie = self.request.cookies.get('user')
        if cookie and utils.valid_cookie(cookie):
            username = cookie.split('|')[0]
            return username

    def json(self):
        self.response.headers['Content-Type'] = ('application/json; '
                                                 'charset=UTF-8')
        allPosts = [{'content': p.content,
                     'created': p.created.strftime('%c'),
                     'subject': p.subject}
                     for p in Posts.all()]
        self.response.write(json.dumps(allPosts))
