import webapp2
import jinja2

import os
import json
import helper
from datetime import datetime

from google.appengine.ext import db
from google.appengine.api import memcache


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape=True,
    extensions=['jinja2.ext.autoescape'])


def render_str(template, **kw):
    t = JINJA_ENVIRONMENT.get_template(template)
    return t.render(kw)


class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.write(render_str(template, **kw))

    def set_cookie(self, user):
        cookie = helper.make_cookie(user)
        self.response.headers.add_header(
            "Set-Cookie",
            "user={}; Path=/".format(cookie))

    def logout(self):
        self.response.headers.add_header("Set-Cookie", "user=; Path=/")


# Unit 1
class MainPage(BaseHandler):
    def get(self):
        self.render('index.html')


# Unit 2
class Rot13(BaseHandler):
    def get(self):
        self.render('unit2/rot13.html')

    def post(self):
        texts = self.request.get('text')
        self.render('unit2/rot13.html', texts=helper.rot13(texts))


class Signup(BaseHandler):
    def get(self):
        self.render('unit2/signup.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        errors = helper.signup_errors(username, password, verify, email)

        u = db.GqlQuery("SELECT * from User "
                        "WHERE username =:1", username)
        used_name = "This username has already been used." if u.get() else ""

        if any(errors) or used_name:
            self.render('unit2/signup.html',
                        username=username,
                        email=email,
                        username_error=errors[0] or used_name,
                        password_error=errors[1],
                        verify_error=errors[2],
                        email_error=errors[3])
        else:
            salt = helper.make_salt()
            hashed_pass = helper.hash_pass(password, salt)
            user = User(username=username, password=hashed_pass,
                        salt=salt, email=email)
            user.put()

            self.set_cookie(username)
            self.redirect('/blog/welcome')


class Welcome(BaseHandler):
    def get(self):
        ck = self.request.cookies.get("user")

        if helper.valid_cookie(ck):
            self.render("/unit2/welcome.html", username=ck.split("|")[0])
        else:
            self.redirect("/blog/signup")


# Unit 3
class Posts(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateProperty(auto_now_add=True)


def age_set(key, val):
    save_time = datetime.utcnow()
    memcache.set(key, (val, save_time))


def age_get(key):
    r = memcache.get(key)
    if r:
        val, save_time = r
        age = (datetime.utcnow() - save_time).total_seconds()
    else:
        val, age = None, 0
    return val, age


def add_post(post):
    post.put()
    get_posts(update=True)
    return str(post.key().id())


def get_posts(update=False):
    q = db.GqlQuery("SELECT * FROM Posts "
                    "ORDER BY created DESC "
                    "LIMIT 10")
    mc_key = "BLOGS"

    posts, age = age_get(mc_key)
    if update or posts is None:
        posts = list(q)
        age_set(mc_key, posts)

    return posts, age


def age_str(age):
    s = 'Queried {}s seconds ago.'
    age = int(age)
    if age == 1:
        s = s.replace('seconds', 'second')
    return s.format(age)


class BlogFront(BaseHandler):
    def get(self):
        posts, age = get_posts()
        self.render("unit3/index.html",
                    posts=posts,
                    age=age_str(age))


class NewPost(BaseHandler):
    def render_post(self, subject="", content="", error=""):
        self.render("unit3/newpost.html",
                    subject=subject,
                    content=content,
                    error=error)

    def get(self):
        self.render_post()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            p = Posts(subject=subject, content=content)
            post_id = add_post(p)

            self.redirect("/blog/{}".format(post_id))
        else:
            error = "Please input both subject and content!"
            self.render_post(subject, content, error)


class PostPage(BaseHandler):
    def get(self, post_id):
        post_key = 'POST_' + post_id

        post, age = age_get(post_key)
        if not post:
            post = Posts.get_by_id(long(post_id))
            if not post:
                self.response.write("This page doesn't exist!")

            age_set(post_key, post)
            age = 0

        self.render("unit3/permanent.html",
                    post=post,
                    age=age_str(age))


# Unit 4
class User(db.Model):
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    salt = db.StringProperty(required=True)
    email = db.StringProperty()


class Login(BaseHandler):
    def get(self):
        self.render("/unit4/login.html")

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        user = db.GqlQuery("SELECT * from User "
                           "WHERE username =:1", username).get()

        if user:
            salt = user.salt.encode("ascii")
            hashed_pwd = user.password.encode("ascii")
            if helper.valid_pass(password, salt, hashed_pwd):
                self.set_cookie(username)
                self.redirect("/blog/welcome")

        self.render("/unit4/login.html", error="Invalid login!")


class Logout(BaseHandler):
    def get(self):
        self.logout()
        self.redirect("/blog/signup")


# Unit 5
class BlogFrontJson(BaseHandler):
    def get(self):
        self.response.headers['Content-Type'] = ('application/json; '
                                                 'charset=UTF-8')
        allPosts = [{"content": p.content,
                     "created": p.created.strftime('%c'),
                     "subject": p.subject}
                    for p in Posts.all()]
        self.response.write(json.dumps(allPosts))


class PostPageJson(BaseHandler):
    def get(self, blog_id):
        blog_id = blog_id.split(',')[0]
        post = Posts.get_by_id(long(blog_id))
        if post:
            self.response.headers['Content-Type'] = ('application/json; '
                                                     'charset=UTF-8')
            p = {"content": post.content,
                 "created": post.created.strftime('%c'),
                 "subject": post.subject}
            self.response.write(json.dumps(p))

        else:
            self.response.write("This page doesn't exist!")


# Unit 6
class FlushMemcache(BaseHandler):
    def get(self):
        memcache.flush_all()
        self.redirect('/blog')


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/rot13', Rot13),
    ('/blog', BlogFront),
    ('/blog/signup', Signup),
    ('/blog/welcome', Welcome),
    ('/blog/.json', BlogFrontJson),
    ('/blog/newpost', NewPost),
    ('/blog/([0-9]+)', PostPage),
    ('/blog/([0-9]+).json', PostPageJson),
    ('/blog/login', Login),
    ('/blog/logout', Logout),
    ('/blog/flush', FlushMemcache)
], debug=True)
