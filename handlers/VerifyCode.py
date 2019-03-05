#coding:utf-8

import logging
import constants
import random

from .BaseHandler import BaseHandler
from utils.captcha.captcha import captcha
from utils.response_code import RET
from libs.yuntongxun.SendTemplateSMS import ccp

class ImageCodeHandler(BaseHandler):
	""""""
	def get(self):
		code_id = self.get_query_argument('codeid','')
		pre_code_id = self.get_query_argument('pcodeid', '')

		if pre_code_id:
			try:
				self.redis.delete('image_code_%s'%pre_code_id)
			except Exception as e:
				logging.error(e)
		name, text, image = captcha.generate_captcha()
		try:
			self.redis.setex('image_code_%s'%code_id, constants.IMAGE_CODE_EXPIRES_SECONDS, text)
		except Exception as e:
			logging.error(e)
			self.write('')
		else:
			self.set_header('Content-Type', 'image/jpg')
			self.write(image)


class PhoneCodeHandler(BaseHandler):
	def post(self):
		"""获取验证码,判断对错,　如果对发送短信,　如果错返回错误码"""

		mobile = self.json_data.get('mobile')
		image_code_id = self.json_data.get('image_code_id')
		image_code_text = self.json_data.get('image_code_text')
		#　参数校验
		if not all((mobile, image_code_id, image_code_text)):
			return self.write(dict(errorcode=RET.PARAMERR, errormsg='参数不完整'))
		#　获取图片验证码的真实值
		try:
			real_image_code_text = self.redis.get('image_code_%s'%image_code_id)
		except Exception as e:
			logging.error(e)
			return self.write(dict(errorcode=RET.DBERR, errormsg='查询出错'))
		
		if not real_image_code_text:
			return self.write(dict(errorcode=RET.NODATA, errormsg='验证码已过期'))

		if real_image_code_text.lower() != image_code_text.lower():
			return self.write(dict(errorcode=RET.DATAERR, errormsg='验证码错误'))

		#　判断手机号是否已经注册
		sql = 'select count(*) counts from ih_user_profile where up_mobile=%s'
		try:
			ret = self.db.get(sql, mobile)
		except Exception as e:
			logging.error(e)
		else:
			if ret['counts'] != 0:
				return self.write(dict(RET.DATAEXIST, errormsg='手机号已注册'))

		#若成功: 生成随机手机验证码,并存入redis
		sms_code = '%04d'%random.randint(0, 9999)
		try:
			self.redis.setex('sms_code_%s'%mobile, constants.SMS_CODE_EXPIRES_SECONDS, sms_code)
		except Exception as e:
			logging.error(e)
			return self.write(dict(errorcode=RET.DBERR, errormsg='生成短信验证码错误'))

		#发送短信
		try:
			result = ccp.sendTemplateSMS(mobile, [sms_code, constants.SMS_CODE_EXPIRES_SECONDS//60], 1)
		except Exception as e:
			logging.error(e)
			return self.write(dict(errorcode=RET.THIRDERR, errormsg='发送失败'))
		else:
			if result:
				self.write(dict(errorcode=RET.OK, errormsg='OK'))
			else:
				self.write(dict(errorcode=RET.UNKOWNERR, errormsg='发送失败'))
		



