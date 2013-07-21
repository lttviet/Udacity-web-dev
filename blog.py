import webapp2
import os
import jinja2
from helper import rot13

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])


class MainPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render())


class Rot13Handler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('ps2/rot13.html')
        self.response.write(template.render(texts=""))

    def post(self):
        texts = self.request.get('text')
        texts = rot13(texts)

        template_values = {
            'texts': texts
        }

        template = JINJA_ENVIRONMENT.get_template('ps2/rot13.html')
        self.response.write(template.render(template_values))

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/rot13', Rot13Handler)
], debug=True)
