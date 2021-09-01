import datetime
import hashlib
import random
import string
import time

from threading import Thread

from instagram_web_api import Client, ClientError, ClientLoginError


# raise queryError:
#     print("Error getting a response froom instagram.")

QUERY_TIME = 30

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




class userBase:
    def __init__(self):
        self.user_dict = {}
        self.web_api = MyClient()

    def display(self):
        for user in self.user_dict:
            print("User: " + user)
            for post in self.user_dict[user]:
                print(post['node'])

    def all_users(self):
        for user in self.user_dict:
            print("User: " + user)

    def add_user(self, user_name):
        new_user = user(user_name)

        if new_user is None:
            print("None returned from query........")
            exit()
            return
        else:
            self.user_dict[user_name] = new_user
            return new_user

    def add_tracked_post(self, user_name):
        tracked_user = self.add_user(user_name)

        print("Which post would you like to track?")
        tracked_user.display_posts()
        post_index = int(input("Enter post number: "))

        tracked_user.track(post_index)

    def foo(self):
        while True:
            for user_key in self.user_dict:
                current_user = self.user_dict[user_key]
                tracked_post_number = current_user.tracked_posts[0]

                tracked_post_id = current_user.posts[tracked_post_number]['node']['id']

                print("Checking user:", current_user.user_name, "post:", tracked_post_id)

                curr_user_info = current_user.get_posts()
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

            time.sleep(QUERY_TIME)


class user(userBase):
    def __init__(self, user_name):
        super().__init__()
        self.user_name = user_name
        self.profile = self.get_profile()
        self.id = self.get_id()
        self.posts = self.get_posts()
        self.tracked_posts = []

    def get_profile(self):
        user_url = 'https://www.instagram.com/%s/?__a=1' % self.user_name
        try:
            return self.web_api._make_request(user_url)
        except:
            print("User does not exist.")
            return

    def get_id(self):
        user_id = self.profile["logging_page_id"]
        user_id = user_id[12:]
        return user_id

    def get_posts(self):
        try:
            self.posts = self.web_api.user_feed(self.id)
            return self.posts
        except:
            print("Error in querying instagram.")
            return

    def display_posts(self):
        print("Displaying %s (%s) posts:" % (self.user_name, self.id))
        for index, post in enumerate(self.posts):
            print(index, post)

    def track(self, post_num):
        self.tracked_posts.append(post_num)


if __name__ == '__main__':
    a = MyClient()

    user_name = input("Enter username fucker: ")
    url = 'https://www.instagram.com/%s/?__a=1' % user_name
    print(url)
    print(a._make_request(url))

    # response = requests.get(url)

    # try:
    #     response.raise_for_status()  # raises exception when not a 2xx response
    # except:
    #     print("Error in getting JSON shit from page, using Response")

    # print(response.json())

    # test_id = '10448683263'

    # users = userBase()
    # test_user = input("Input user to track: ")
    # users.add_tracked_post(test_user)
    #
    # #
    # #
    # # test_user = '1234177284'
    # #
    # # users.add_user(test_user)
    # #
    # # users.add_tracked_post(test_user)
    # Thread(target=users.foo).start()
    #
    # users.add_user('199414232')
    # users.add_tracked_post('199414232')
    # users.add_user('10448683263')
    # users.add_tracked_post('10448683263')
