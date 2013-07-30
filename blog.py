import webapp2
import os
import jinja2
import helper
import string
import random
from google.appengine.ext import db

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape=True,
    extensions=['jinja2.ext.autoescape'])


class Posts(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateProperty(auto_now_add=True)


def render_str(template, **kw):
    t = JINJA_ENVIRONMENT.get_template(template)
    return t.render(kw)


class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.write(render_str(template, **kw))


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
        texts = helper.rot13(texts)

        self.render('unit2/rot13.html', texts=texts)


class SignupHandler(BaseHandler):
    def get(self):
        self.render('unit2/signup.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        errors = helper.signup_errors(username, password, verify, email)

        if not any(errors):
            self.redirect('/unit2/welcome?username={}'.format(username))
        else:
            self.render('unit2/signup.html',
                        username=username,
                        email=email,
                        username_error=errors[0],
                        password_error=errors[1],
                        verify_error=errors[2],
                        email_error=errors[3])


class WelcomeHandler(BaseHandler):
    def get(self):
        username = self.request.get('username')
        self.render('unit2/welcome.html', username=username)


# Unit 3
class BlogHandler(BaseHandler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Posts "
                            "ORDER BY created DESC "
                            "LIMIT 10")
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

            i = p.key().id()
            self.redirect("/unit3/{}".format(i))
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


class RegistrationHandler(BaseHandler):
    def get(self):
        self.render("unit4/signup.html")

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        errors = helper.signup_errors(username, password, verify, email)

        u = db.GqlQuery("SELECT * from User "
                        "WHERE username =:1", username)
        user_error = ""
        if u.get():
            user_error = "This username has already been used."

        if any(errors) or user_error:
            self.render("unit4/signup.html",
                        username=username,
                        email=email,
                        username_error=errors[0] or user_error,
                        password_error=errors[1],
                        verify_error=errors[2],
                        email_error=errors[3])
        else:
            salt = ''.join([random.choice(string.ascii_letters + string.digits)
                            for i in xrange(16)])
            hashed_pass = helper.hash_pass(password, salt)
            user = User(username=username, password=hashed_pass,
                        salt=salt, email=email)
            user.put()

            cookie = helper.make_cookie(username)
            self.response.headers.add_header("Set-Cookie",
                                             "user={}; Path=/".format(cookie))
            self.redirect("/unit4/welcome")


class WelcomeCookie(BaseHandler):
    def get(self):
        ck = self.request.cookies.get("user")

        if helper.valid_cookie(ck):
            self.render("/unit4/welcome.html", username=ck.split("|")[0])
        else:
            self.redirect("/unit4/signup")


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
            hashed_pass = user.password.encode("ascii")
            if helper.hash_pass(password, salt) == hashed_pass:
                cookie = helper.make_cookie(username)
                self.response.headers.add_header("Set-Cookie",
                                                 "user={}; ".format(cookie) +
                                                 "Path=/")
                self.redirect("/unit4/welcome")
        error = "Invalid login!"
        self.render("/unit4/login.html", error=error)


class Logout(BaseHandler):
    def get(self):
        self.response.headers.add_header("Set-Cookie",
                                         "user=; Path=/")
        self.redirect("/unit4/signup")

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/unit2/rot13', Rot13Handler),
    ('/unit2/signup', SignupHandler),
    ('/unit2/welcome', WelcomeHandler),
    ('/unit3', BlogHandler),
    ('/unit3/newpost', NewPostHandler),
    ('/unit3/([0-9]+)', PermanentPost),
    ('/unit4/signup', RegistrationHandler),
    ('/unit4/welcome', WelcomeCookie),
    ('/unit4/login', LoginHandler),
    ('/unit4/logout', Logout)
], debug=True)
