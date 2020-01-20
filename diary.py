#!/usr/bin/env python3

from urllib.parse import urlencode
import urllib3
import json
from hashlib import md5


# From https://github.com/capgelka/hapidry/blob/master/app/Main.hs
appkey = "5ab793910e36584cd81622e5eb77d3d1"
appsecret = "8543db8deccb4b0fcb753291c53f8f4f"


class Diary:
    def __init__(self):
        self.sid = None

    @staticmethod
    def _request(method, params):
        url = "https://www.diary.ru/api/"
        params2 = params.copy()
        params2['method'] = method
        print(params2)

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0",
            "Accept": "application/json",
        }

        http = urllib3.PoolManager()
        response = http.request("POST", url, params2, headers)
        response = response.data.decode("utf8")
        print(response)
        result = json.loads(response)
        print(result)
        if result['result'] != "0":
            raise Exception(result['error'])
        return result

    @staticmethod
    def _request_large(method, params):
        url = "https://www.diary.ru/api/"
        params2 = params.copy()
        params2['method'] = method
        print(params2)

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0",
            "Accept": "application/json",
        }

        http = urllib3.PoolManager()
        response = http.request("POST", url, params2, headers)
        response = response.data.decode("utf8")
        print(response)
        result = json.loads(response)
        print(result)
        if result['result'] != "0":
            raise Exception(result['error'])
        return result

    def login(self, username, password):
        s = appsecret + password
        m = md5(s.encode("utf8"))
        password = m.hexdigest()

        params = dict()
        params['username'] = username.encode("cp1251")
        params['password'] = password
        params['appkey'] = appkey
        result = self._request("user.auth", params)
        self.sid = str(result['sid'])

    def new_post(self, text, userid=None):
        params = dict()
        params['sid'] = self.sid
        params['message'] = text.encode("cp1251")
        #params['close_access_mode'] = 7
        if userid is not None:
            params['juserid'] = userid
        result = self._request_large("post.create", params)
        return int(result['postid'])

    def add_comment(self, postid, text):
        params = dict()
        params['sid'] = self.sid
        params['postid'] = str(postid)
        params['message'] = text
        self._request_large("comment.create", params)

    def get_posts(self, userid=None, skip_first=None):
        params = dict()
        params['sid'] = self.sid
        params['type'] = 'diary'
        if userid is not None:
            params['juserid'] = userid
        if skip_first is not None:
            params['from'] = skip_first
        result = self._request("post.get", params)
        return result['posts']
    
    def get_all_comments(self, post_id):
        comments = {}

        _from = 0
        last_comments_size = 0
        while True:
            params = dict()
            params['sid'] = self.sid
            params['postid'] = post_id
            if _from is not None:
                params['from'] = _from
            result = self._request("comment.get", params)
            comment_hash = result['comments']
            for id in sorted(comment_hash.keys()):
                comments[id] = comment_hash[id]
            if len(comments) == last_comments_size:
                break
            last_comments_size = len(comments)
            _from += len(comment_hash)

        comment_list = []
        for id in sorted(comments.keys()):
            comment_list.append(comments[id])
        return comment_list
