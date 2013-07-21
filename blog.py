import webapp2
import os
import jinja2
import helper

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])


def render_str(template, **kw):
    t = JINJA_ENVIRONMENT.get_template(template)
    return t.render(kw)


class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.write(render_str(template, **kw))


class MainPage(BaseHandler):
    def get(self):
        self.render('index.html')


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

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/unit2/rot13', Rot13Handler),
    ('/unit2/signup', SignupHandler),
    ('/unit2/welcome', WelcomeHandler)
], debug=True)
