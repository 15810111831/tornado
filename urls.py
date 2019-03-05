#coding:utf-8
import os
from tornado.web import StaticFileHandler
from handlers import Passport, VerifyCode, Profile, House
from handlers.BaseHandler import StaticFileHandler

handlers = [
	(r'/', Passport.IndexHandler),
	(r'/api/imagecode', VerifyCode.ImageCodeHandler),
	(r'/api/phonecode', VerifyCode.PhoneCodeHandler),
	(r'/api/register', Passport.RegisterHandler),
	(r'/api/login', Passport.LoginHandler),
	(r'/api/logout', Passport.LogoutHandler),
	(r'/api/check_login', Passport.CheckLoginHandler),
	(r'/api/profile', Profile.ProfileHandler),
	(r'/api/profile/avatar', Profile.AvatarHandler),
	(r'/api/profile/auth', Profile.AuthHandler),
	(r'/api/profile/name', Profile.NameHandler),
	(r'/api/house/area', House.AreaInfoHandler),
	(r'/api/house/my', House.MyHousesHandler),
	(r'/(.*)', StaticFileHandler, {'path':os.path.join(os.path.dirname(__file__), 'template'), 'default_filename':'index.html'})
]