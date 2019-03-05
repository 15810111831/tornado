# coding:utf-8

import uuid
import json
import logging

from constants import SESSION_EXPIRES_SECONDS


class Session(object):
    """"""
    def __init__(self, request_handler_obj):
        self._request_handler = request_handler_obj
        self.session_id = self._request_handler.get_secure_cookie('session_id')
        
        if not self.session_id:
            self.session_id = uuid.uuid4().get_hex()
            self.data = {}
        #　如果存在session_id就从redis中获取
        else:
            try:
                data = self._request_handler.redis.get('sess_%s'%self.session_id)
            except Exception as e:
                logging.error(e)
                self.data = {}

            if not data:
                self.data = {}
            else:
                self.data = json.loads(data)

    def save(self):
        data = json.dumps(self.data)
        print data
        try:
            self._request_handler.redis.setex('sess_%s'%self.session_id, SESSION_EXPIRES_SECONDS, data)
        except Exception as e:
            logging.error(e)
            raise e
        else:
            self._request_handler.set_secure_cookie('session_id', self.session_id)

    def clear(self):
        self._request_handler.clear_cookie('session_id')
        try:
            self.redis.delete('sess_%s'%self.session_id)
        except Exception as e:
            logging.error(e)








"""
class xxxxhandler(RequestHandler):
    def post(self):

        session = Session(self)
        session.session_id
        session.data["username"] = "abc"
        session.data["mobile"] = "abc"
        session.save()

    def get(self):
        session = Session(self)
        session.data["username"] = "def"
        session.save()



    def get(self):
        session = Session(self)
        session.clear()

        session.clear()

redis中的数据：
key:    session_id
value:  data
"""
