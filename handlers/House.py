#coding:utf-8

import logging
import json
import constants

from .BaseHandler import BaseHandler
from utils.response_code import RET
from utils.commons import required_login

class AreaInfoHandler(BaseHandler):
	"""区域信息"""
	def get(self):
		#　先从缓存中取出信息
		try:
			ret = self.redis.get('area_info')
		except Exception as e:
			logging.error(e)
			ret = None

		if ret:
			logging.info('hit redis:area_info')
			resp = '{"errorcode":"0","errormsg":"OK", "data":%s}'%ret
			return self.write(resp)
		#　如果缓存中没有在从数据库中查找信息
		try:
			ret = self.db.query('select ai_area_id, ai_name from ih_area_info;')
		except Exception as e:
			logging.error(e)
			return self.write(dict(errorcode=RET.DBERR, errormsg='get area data failed'))
		if not ret:
			return self.write(dict(errorcode=RET.NODATA, errormsg='no area data'))

		areas = []
		for l in ret:
			area = {
				'area_id':l['ai_area_id'],
				'name':l['ai_name']
			}
			areas.append(area)
		#　将查找到的信息缓存到redis中
		json_data = json.dumps(areas)
		try:
			self.redis.setex('area_info', constants.REDIS_AREA_INFO_EXPIRES_SECONDES, json_data)
		except Exception as e:
			logging.error(e)

		self.write({'errorcode':RET.OK, 'errormsg':'OK', 'data':areas})


class MyHousesHandler(BaseHandler):
	""""""
	@required_login
	def get(self):
		user_id = self.session.data['user_id']
		sql = 'select a.hi_house_id, a.hi_title, a.hi_price, a.hi_index_image_url, a.hi_ctime, b.ai_name from ih_house_info a left join ih_area_info b on a.hi_area_id=b.ai_area_id where a.hi_user_id = %s'
		try:
			ret = self.db.query(sql, user_id)
		except Exception as e:
			logging.error(e)
			return self.write(dict(errorcode=RET.DBERR, errormsg='查询数据库出错'))

		houses = []
		if ret:
			for row in ret:
				house = {
					'house_id':row['hi_house_id'],
					'title':row['hi_title'],
					'price':row['hi_price'],
					'ctime':row['hi_ctime'].strftime('%Y-%m-%d'),
					'area_name':row['ai_name'],
					'img_url':constants.QINIU_URL_PREFIX + row['ih_index_image_url'] if row['ih_index_image_url'] else ''
				}
				houses.append(house)
		self.write({'errorcode':RET.OK, 'errormsg':'OK', 'houses':houses})


class HouseInfoHandler(BaseHandler):
	"""发布新房源"""
	@required_login
	def post(self):
		user_id = self.session.data['user_id']
		title = self.json_data.get('title')
		price = self.json_data.get('price')
		area_id = self.json_data.get('area_id')
		address = self.json_data.get('address')
		room_count = self.json_data.get('room_count')
		acreage = self.json_data.get('acreage')
		unit = self.json_data.get('unit')
		capacity = self.json_data.get('capacity')
		beds = self.json_data.get('beds')
		deposit = self.json_data.get('deposit')
		min_days = self.json_data.get('min_days')
		max_days = self.json_data.get('max_days')
		facility = self.json_data.get('facility')

		if not all([title, price, address, area_id, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
			return self.write({'errorcode':RET.PARAMERR, 'errormsg':'缺少参数'})

		try:
			price = int(price) * 100
			deposit = int(deposit) * 100
		except Exception as e:
			logging.error(e)
			return self.write({'errorcode':RET.PARAMERR, 'errormsg':'参数错误'})

		#　添加数据到mysql数据库
		try:
			sql = 'insert into ih_house_info(hi_user_id,hi_title, hi_price, hi_area_id, hi_address, hi_room_count, hi_capacity, hi_beds, hi_deposit, hi_min_days, hi_max_days) values(%(user_id)s,%(title)s, %(area_id)s, %(address)s, %(room_count)s, %(capacity)s, %(beds)s, %(deposit)s, %(min_days)s, %(max_days)s)'
			house_id = self.db.execute(sql,user_id = user_id, title=title,aread_id=aread_id, address=address, room_count=room_count, capacity=capacity, beds=beds, deposit=deposit, min_days=min_days, max_days=max_days)
		except Exception as e:
			logging.error(e)
			return self.write({'errorcode':RET.DBERR, 'errormsg':'insert　failed'})

		#　给房间添加设施
		try:
			sql = 'insert into ih_house_facility(hf_house_id, hf_facility_id) values'

			sql_val = []
			vals = []
			for facility_id in facility:
				sql_val.append('(%s,%s)')
				vals.append(house_id, facility_id)

			sql += ','.join(sql_val)
			vals = tuple(vals)
			logging.debug(sql)
			logging.debug(vals)
			self.db.execute(sql, *vals)
		except Exception as e:
			logging.error(e)
			try:
				self.db.execute('delete from ih_house_info where hi_house_id=%s', house_id)
			except Exception as e:
				logging.error(e)
				return self.write({'errorcode':RET.DBERR, 'errormsg':'delete failed'})
			else:
				return self.write({'errorcode':RET.DBERR, 'errormsg':'no data save'})
		self.write({'errorcode':RET.OK, 'errormsg':'OK', 'house_id':house_id})





