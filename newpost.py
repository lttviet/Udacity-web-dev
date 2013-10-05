# -*- coding: utf-8 -*-

import utils

from basehandler import BaseHandler

from database import Post


class NewPost(BaseHandler):
    def render_post(self, subject='', content='', error=''):
        self.render('/templates/newpost.html',
                    subject=subject,
                    content=content,
                    error=error)

    def get(self):
        self.render_post()

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(subject=subject, content=content)
            post_id = utils.add_post(p)

            self.redirect('/blog/{}'.format(post_id))
        else:
            error = 'Please input both subject and content!'
            self.render_post(subject, content, error)
