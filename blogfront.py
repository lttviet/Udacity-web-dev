# -*- coding: utf-8 -*-

import json

import utils

from database import Post

from basehandler import BaseHandler


class BlogFront(BaseHandler):
    def get(self):
        posts, age = utils.get_posts()
        self.render('/templates/blogfront.html',
                    posts=posts,
                    age=utils.age_str(age))

        if False:
            self.response.headers['Content-Type'] = ('application/json; '
                                                     'charset=UTF-8')
            allPosts = [{'content': p.content,
                         'created': p.created.strftime('%c'),
                         'subject': p.subject}
                        for p in Post.query()]
            self.response.write(json.dumps(allPosts))
