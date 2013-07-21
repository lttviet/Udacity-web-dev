import webapp2
import os
import jinja2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])


class MainPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render())


class TestHandler(webapp2.RequestHandler):
    def post(self):
        q = self.request.get("q")
        self.response.out.write(q)

        #self.response.headers['Content-Type'] = 'text/plain'
        #self.response.out.write(self.request)


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/testform', TestHandler)
], debug=True)
