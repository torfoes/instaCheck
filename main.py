import datetime
import hashlib
import random
import string
import time

from threading import Thread
from instagram_web_api import Client, ClientError, ClientLoginError

# how often a query is sent to instagram to see if the post has been archived, or deleted
QUERY_TIME = 30

# number of posts that you would like to get from instagram (from most recent) - cannot be more than fifty
NUM_QUERY_POSTS = 10

EMAIL_FOR_NOTIFICATION = "karloszuru@gmail.com"

# this class here because I was having issues with the built in client from the insta_api client
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
    """Main class that holds users and allows you to perform different operations on them"""
    def __init__(self):
        self.user_dict = {}
        self.web_api = MyClient()

    def display(self):
        """Displays all a user's posts that were returned from the original query"""
        for user in self.user_dict:
            print("User: " + user)
            for post in self.user_dict[user]:
                print(post['node'])

    def all_users(self):
        """Displays all usernames saved in the dictionary"""
        for user in self.user_dict:
            print("User: " + user)

    def add_user(self):
        """Adds a user class to the dictionary with all of their information.
        Usually a helper function called by the add_tracked_post."""
        username = input("Input user to track: ")
        new_user = user(username)

        if new_user is None:
            print("Nothing returned from query or something else :3")
            return
        else:
            self.user_dict[username] = new_user
            return new_user

    def add_tracked_post(self):
        """creates a new user based input username"""
        tracked_user = self.add_user()

        print("Which post would you like to track: ")
        tracked_user.display_posts()
        post_index = int(input("Enter post index: "))

        tracked_user.track(post_index)

    def periodic_check(self):
        while True:
            for user_key in self.user_dict:
                current_user = self.user_dict[user_key]
                tracked_post_number = current_user.tracked_posts[0]

                tracked_post_id = current_user.posts[tracked_post_number]['node']['id']

                print("Checking for user:", current_user.username, "post id:", tracked_post_id)

                curr_user_info = current_user.get_posts()

                post_exists = False

                for post in curr_user_info:
                    current_post_id = post['node']['id']

                    if current_post_id == tracked_post_id:
                        post_exists = True

                if not post_exists:
                    print("Post", tracked_post_id, "was deleted.")

            time.sleep(QUERY_TIME)


class user(userBase):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.profile = self.get_profile()
        self.id = self.get_id()
        self.posts = self.save_posts()
        self.tracked_posts = []

    def get_profile(self):
        """Gets user profile from username."""
        print("Getting profile information.")
        user_url = 'https://www.instagram.com/%s/?__a=1' % self.username
        try:
            return self.web_api._make_request(user_url)
        except:
            print("User does not exist.")
            return

    def get_id(self):
        """Strips user ID from profile information"""
        user_id = self.profile["logging_page_id"]
        user_id = user_id[12:]
        return user_id

    def get_posts(self):
        """Uses user ID to get all CURRENT posts from a user without updating saved posts."""
        try:
            current_posts = self.web_api.user_feed(self.id, count=NUM_QUERY_POSTS)
            return current_posts
        except:
            print("Error in querying instagram.")
            return

    def save_posts(self):
        print("Saving posts to current user.")
        return self.get_posts()

    def display_posts(self):
        """Displays all of the posts of a user (up to fifty)"""
        print("Displaying %s (%s) posts:" % (self.username, self.id))
        for index, post in enumerate(self.posts):
            print(index, post)

    def track(self, post_id):
        """Adds post to tracked posts list"""
        self.tracked_posts.append(post_id)


if __name__ == '__main__':
    users = userBase()
    users.add_tracked_post()
    users.add_tracked_post()

    Thread(target=users.periodic_check).start()
