import json
import urllib.request


class Gitlab(object):
    def __init__(self, gitlab_url='https://gitlab.com', private_token=None):

        self.gitlab_url = gitlab_url
        self.private_token = private_token

        self.api_entry_point = f'{self.gitlab_url}/api/v4'
        self.headers = {'PRIVATE-TOKEN': self.private_token}
        self._get_authenticated_useruser()

    def _get_authenticated_useruser(self):

        req = urllib.request.Request(
                url=f'{self.api_entry_point}/user/',
                headers=self.headers)

        with urllib.request.urlopen(req) as res:
            result = json.load(res)

        self.auth_username = result['username']
        self.auth_user_id = result['id']

    def user_events(self):

        req = urllib.request.Request(
                url=f'{self.api_entry_point}/users/{self.auth_user_id}/events',
                headers=self.headers)

        with urllib.request.urlopen(req) as res:
            return json.load(res)