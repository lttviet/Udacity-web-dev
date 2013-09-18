import webapp2
import os
import jinja2
import json
import helper
from google.appengine.ext import db


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
class Rot13Handler(BaseHandler):
    def get(self):
        self.render('unit2/rot13.html')

    def post(self):
        texts = self.request.get('text')
        self.render('unit2/rot13.html', texts=helper.rot13(texts))


class SignupHandler(BaseHandler):
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


class WelcomeHandler(BaseHandler):
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


CACHE = {}


def update_blog():
    key = "top"
    if key not in CACHE:
        posts = db.GqlQuery("SELECT * FROM Posts "
                            "ORDER BY created DESC "
                            "LIMIT 10")
        posts = list(posts)
        CACHE[key] = posts
    return CACHE[key]


class BlogHandler(BaseHandler):
    def get(self):
        posts = update_blog()
        self.render("unit3/index.html",
                    posts=posts)


class NewPostHandler(BaseHandler):
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
            p.put()
            CACHE.clear()

            i = p.key().id()
            self.redirect("/blog/{}".format(i))
        else:
            error = "Please input both subject and content!"
            self.render_post(subject, content, error)


class PermanentPost(BaseHandler):
    def get(self, blog_id):
        post = Posts.get_by_id(long(blog_id))
        if post:
            self.render("unit3/permanent.html",
                        post=post)
        else:
            self.response.write("This page doesn't exist!")


# Unit 4
class User(db.Model):
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    salt = db.StringProperty(required=True)
    email = db.StringProperty()


class LoginHandler(BaseHandler):
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
class BlogJson(BaseHandler):
    def get(self):
        self.response.headers['Content-Type'] = ('application/json; '
                                                 'charset=UTF-8')
        allPosts = [{"content": p.content,
                     "created": p.created.strftime('%c'),
                     "subject": p.subject}
                    for p in Posts.all()]
        self.response.write(json.dumps(allPosts))


class PermanentJson(BaseHandler):
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

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/rot13', Rot13Handler),
    ('/blog/signup', SignupHandler),
    ('/blog/welcome', WelcomeHandler),
    ('/blog', BlogHandler),
    ('/blog/.json', BlogJson),
    ('/blog/newpost', NewPostHandler),
    ('/blog/([0-9]+)', PermanentPost),
    ('/blog/([0-9]+).json', PermanentJson),
    ('/blog/login', LoginHandler),
    ('/blog/logout', Logout)
], debug=True)
