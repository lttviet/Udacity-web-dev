# -*- coding: utf-8 -*-

import json

import utils

from database import Post

from basehandler import BaseHandler


class PostPage(BaseHandler):
    def get(self, post_id):
        post_key = 'POST_' + post_id

        post, age = utils.age_get(post_key)
        if not post:
            post = Post.get_by_id(long(post_id))
            if not post:
                self.response.write('This page doesn\'t exist!')
            utils.age_set(post_key, post)
            age = 0

        if True:
            self.render('/templates/permanent.html',
                        post=post,
                        age=utils.age_str(age))

        else:
            self.response.headers['Content-Type'] = ('application/json; '
                                                     'charset=UTF-8')
            p = {'content': post.content,
                 'created': post.created.strftime('%c'),
                 'subject': post.subject}
            self.response.write(json.dumps(p))
