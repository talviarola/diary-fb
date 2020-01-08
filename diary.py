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
        url = "http://www.diary.ru/api/"
        params2 = params.copy()
        params2['method'] = method
        #data = urlencode(params2)
        print(params2)
        #url = url + "?" + data

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
        url = "http://www.diary.ru/api/"
        params2 = params.copy()
        params2['method'] = method
        data = urlencode(params2)
        print(params2)

        boundary = "d41d8cd98f00b204e9800998ecf8427e"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0",
            "Accept": "application/json",
            #"Content-Type": "application/x-www-form-urlencoded",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            #"Content-Type": "multipart/form-data; charset=UTF-8; boundary=" + boundary
        }

        #headers["Content-Type"] = "multipart/form-data; charset=UTF-8; boundary=d41d8cd98f00b204e9800998ecf8427e"

        http = urllib3.PoolManager()
        response = http.request("POST", url, params2, headers, encode_multipart=False, multipart_boundary=boundary)
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
        params['message'] = text.encode("utf8")
        params['close_access_mode'] = 7
        if userid is not None:
            params['juserid'] = userid
        result = self._request_large("post.create", params)
        return int(result['postid'])

    def add_comment(self, postid, text):
        params = dict()
        params['sid'] = self.sid
        params['postid'] = postid
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


login = "<login>"
password = "<password>"

api = Diary()
api.login(login, password)

import util
text = util.load("split_part1.txt")
text = "это пост в utf8"
#posts = api.get_posts(None, 0)
api.new_post(text)
#print(posts)

#
# def main():
#     login = os.getenv("DIARY_LOGIN")
#     password = os.getenv("DIARY_PASSWORD")
#     if len(sys.argv) < 2:
#         print "Usage: DIARY_LOGIN='my_login' DIARY_PASSWORD='my_password' %s <output_dir> [<user_id>]" % sys.argv[0]
#         return
#     out_dir = sys.argv[1]
#     if not os.path.isdir(out_dir):
#         os.mkdir(out_dir)
#         os.mkdir(os.path.join(out_dir, "posts"))
#         os.mkdir(os.path.join(out_dir, "comments"))
#         os.mkdir(os.path.join(out_dir, "avatars"))
#     userid = None
#     if len(sys.argv) > 2:
#         userid = int(sys.argv[2])
#
#     if (login is None) or (password is None):
#         print "You have to set DIARY_LOGIN and DIARY_PASSWORD environment variables"
#         return
#
#     posts_by_date = dict()
#     posts_with_comments = set()
#     avatars = set()
#     try:
#         api = Diary()
#         api.login(login, password)
#         print "Downloading posts..."
#         _from = 0
#         while True:
#             posts = api.get_posts(userid, _from)
#             if len(posts) == 0:
#                 break
#             for post in posts.values():
#                 id = str(post['postid'])
#                 posts_by_date[post['dateline_date']] = id
#                 if ("comments_count_data" in post) and (int(post['comments_count_data']) > 0):
#                     posts_with_comments.add(id)
#                 if "avatar_path" in post:
#                     avatars.add(post["avatar_path"])
#
#                 path = os.path.join(out_dir, "posts", "%s.json" % id)
#                 f = open(path, 'w')
#                 json.dump(post, f)
#                 f.close()
#
#             _from += len(posts)
#
#         post_ids = []
#         for date in sorted(posts_by_date.keys(), reverse=True):
#             post_ids.append(posts_by_date[date])
#         f = open(os.path.join(out_dir, "posts.json"), "w")
#         json.dump(post_ids, f)
#         f.close()
#
#         print "Downloading comments..."
#         for post_id in posts_with_comments:
#             comments = api.get_all_comments(post_id)
#             for comment in comments:
#                 if "author_avatar" in comment:
#                     avatars.add(comment["author_avatar"])
#
#             path = os.path.join(out_dir, "comments", "%s.json" % post_id)
#             f = open(path, 'w')
#             json.dump(comments, f)
#             f.close()
#
#         print "Downloading avatars..."
#         for avatar in avatars:
#             try:
#                 print "==>", avatar
#                 filename = avatar.replace('http://', '').replace('/', '_')
#                 path = os.path.join(out_dir, "avatars", filename)
#                 print path
#                 download(avatar, path)
#             except Exception as e:
#                 print e
#
#         print "Unpacking index.html..."
#         unpack_index_html(os.path.join(out_dir, "index.html"))
#     except Exception as e:
#         print "Error:", e
#
# if __name__ == "__main__":
#     main()
#
