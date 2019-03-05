#coding:utf-8
import tornado.web
import json
from utils.session import Session


class BaseHandler(tornado.web.RequestHandler):
	"""handlers 基类"""
	@property
	def db(self):
		return self.application.db

	@property
	def redis(self):
		return self.application.redis

	def prepare(self):
		self.xsrf_token
		if self.request.headers.get('Content-Type','').startswith('application/json'):
			self.json_data = json.loads(self.request.body)
		else:
			self.json_data = None

	def set_default_headers(self):
		self.set_header('Content-Type', 'application/json; charset=UTF-8')

	def initialize(self):
		pass

	def write_error(self, status_code, **kwargs):
		pass

	def on_finish(self):
		pass

	def get_current_user(self):
		self.session = Session(self)
		return self.session.data


class StaticFileHandler(tornado.web.StaticFileHandler):
	def __init__(self, *args, **kwargs):
		super(StaticFileHandler, self).__init__(*args, **kwargs)
		self.xsrf_token