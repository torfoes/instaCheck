import datetime
import hashlib
import random
import string
import time

from threading import Thread

from instagram_web_api import Client, ClientError, ClientLoginError


class MyClient(Client):

    @staticmethod
    def _extract_rhx_gis(html):
        options = string.ascii_lowercase + string.digits
        text = ''.join([random.choice(options) for _ in range(8)])
        return hashlib.md5(text.encode()).hexdigest()

    def login(self):
        """Login to the web site."""
        if not self.username or not self.password:
            raise ClientError('username/password is blank')

        time = str(int(datetime.datetime.now().timestamp()))
        enc_password = "#PWD_INSTAGRAM_BROWSER:0:{time}:{self.password}"

        params = {'username': self.username, 'enc_password': enc_password, 'queryParams': '{}', 'optIntoOneTap': False}
        self._init_rollout_hash()
        login_res = self._make_request('https://www.instagram.com/accounts/login/ajax/', params=params)
        if not login_res.get('status', '') == 'ok' or not login_res.get('authenticated'):
            raise ClientLoginError('Unable to login')

        if self.on_login:
            on_login_callback = self.on_login
            on_login_callback(self)
        return login_res


class user_base:
    def __init__(self):
        self.user_dict = {}
        self.web_api = MyClient()
        self.tracked_posts = []

    def query_user(self, user_id):
        user_feed_info = self.web_api.user_feed(user_id)
        return user_feed_info

    def add_user(self, user_id):
        user_feed_info = self.query_user(user_id)
        self.user_dict[user_id] = user_feed_info
        return user_feed_info

    def all_posts(self):
        for user in self.user_dict:
            print("User: " + user)
            for post in self.user_dict[user]:
                print(post['node'])

    def all_users(self):
        for user in self.user_dict:
            print("User: " + user)

    def display_user_posts(self, user_id):
        for index, post in enumerate(self.user_dict[user_id]):
            print(index, post)

    def num_change_check(self, user_id):
        saved_user = self.user_dict[user_id]
        current_user = self.add_user(user_id)

        saved_user_posts = []
        current_user_posts = []

        print("Saved Posts:")
        for post in self.user_dict[user_id]:
            saved_user_posts.append(post)
            print(post)

        print("New Query:")
        for post in current_user:
            current_user_posts.append(post)
            print(post)

        if len(saved_user_posts) != len(current_user_posts):
            print("There has been a change in the number of posts.")

    def add_tracked_post(self, user_id):
        print("Which post would you like to track?")
        self.display_user_posts(user_id)

        # if user_id in self.user_dict:
        #     self.add_user(user_id)

        posts = self.user_dict[user_id]
        # print(posts)

        post_index = int(input("Enter post number: "))

        tracked_post = posts[post_index]
        # print("Tracking post ", tracked_post)

        id_and_post = [user_id, tracked_post]
        self.tracked_posts.append(id_and_post)

    def foo(self):
        while True:
            for user in self.tracked_posts:
                user_id = user[0]
                tracked_post = user[1]

                tracked_post_id = tracked_post['node']['id']

                print("Checking user:", user_id, "post:", tracked_post_id)

                curr_user_info = self.query_user(user_id)
                # print(curr_user_info)

                post_exists = False

                for post in curr_user_info:
                    current_post_id = post['node']['id']
                    print("Checking: ", current_post_id)
                    if current_post_id == tracked_post_id:
                        post_exists = True

                if not post_exists:
                    print("Post", tracked_post_id, "was deleted.")

                    # user_info = self.user_dict[user_id]
                    #
                    # print(user_info)
                    #
                    # post_exists = True

                    # for post in user_info['node']:
                    #     if post['id'] == post_info[1]:
                    #         print("Post no longer exists.")
                    #         post_exists = False

            time.sleep(30)


if __name__ == '__main__':
    # user_name = input("Enter username: ")
    # url = 'https://www.instagram.com/%s/?__a=1' % user_name
    # print(url)

    # response = requests.get(url)

    # try:
    #     response.raise_for_status()  # raises exception when not a 2xx response
    # except:
    #     print("Error in getting JSON shit from page, using Response")

    # print(response.json())


    # test_id = '10448683263'

    # users.query_user('10448683263')
    #
    # users.query_user('1234177284')
    #
    #
    users = user_base()


    test_user = '1234177284'

    users.add_user(test_user)

    users.add_tracked_post(test_user)
    Thread(target=users.foo).start()
    time.sleep(10)
    users.add_user('199414232')
    users.add_tracked_post('199414232')
    users.add_user('10448683263')
    users.add_tracked_post('10448683263')