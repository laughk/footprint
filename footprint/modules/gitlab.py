import json
import urllib.request
import urllib.parse
import datetime

import dateutil.parser

PICKUP_TYPE = {
    'action': [
        'created',
        'closed',
        'reopened',
        'commented on',
        'merged',
        'opened'
    ],
    'target': [
        'issue',
        'note',
        'merge_request',
        'note',
        'project',
    ]
}


class footprintGitlab(object):
    def __init__(self, private_token=None,
                 gitlab_url='https://gitlab.com', per_page=100, max_page=3):

        self.gitlab_url = gitlab_url
        self.private_token = private_token
        self.per_page = per_page
        self.max_page = max_page

        self.api_entry_point = f'{self.gitlab_url}/api/v4'
        self.api_v3_entry_point = f'{self.gitlab_url}/api/v3'
        self.headers = {'PRIVATE-TOKEN': self.private_token}

        self.request_param = urllib.parse.urlencode({'per_page': self.per_page})
        self.get_query = self.request_param

        self.projects = {}
        self.target_info = {}
        self._get_authenticated_user()

    def _request_to_api(self, path, query, api_version='v4'):

        result = {'body': None, 'info': None}

        req = urllib.request.Request(
                url=f'{self.api_entry_point}{path}?{query}',
                headers=self.headers)

        with urllib.request.urlopen(req) as res:
            result['body'] = json.load(res)
            result['info'] = res.info()

        return result

    def _get_authenticated_user(self):

        req = urllib.request.Request(
                url=f'{self.api_entry_point}/user/',
                headers=self.headers)

        with urllib.request.urlopen(req) as res:
            result = json.load(res)

        self.auth_username = result['username']
        self.auth_user_id = result['id']

    def user_events(self, from_, to_):

        events = []
        query_data = {
            'per_page': self.per_page,
            'before': (to_ + datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
            'after': (from_ - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        }

        while True:
            _events = self._request_to_api(
                f'/users/{self.auth_user_id}/events',
                urllib.parse.urlencode(query_data))
            events.extend(_events['body'])
            if not _events['info'].get('X-Next-Page') or _events['info'].get('X-Next-Page') == self.max_page:
                break
            else:
                query_data['page'] = _events["info"]["X-Next-Page"]

        return self.user_events_parse(events, from_, to_)

    def user_events_parse(self, events, from_, to_):
        result = {}
        for event in events:
            if event.get('action_name') in PICKUP_TYPE['action']:
                event_created_at = dateutil.parser.parse(event['created_at'])

                from_delta = from_.astimezone() - event_created_at
                to_delta = to_.astimezone() - event_created_at

                if from_delta.days <= 0 and to_delta.days >= 0:
                    project_name = self.get_project_name(event['project_id'])
                    if not result.get(project_name):
                        result[project_name] = []

                    if event.get('note') and event["note"]["noteable_id"]:
                        event['_target_url'] = f'{self.get_target_url(event["project_id"], event["note"]["noteable_type"], event["note"]["noteable_id"])}#note_{event["note"]["id"]}'
                    elif event.get('target_type'):
                        event['_target_url'] = f'{self.get_target_url(event["project_id"], event["target_type"], event["target_id"])}'
                    elif event['action_name'] == 'created':
                        event['_target_url'] = f'{self.gitlab_url}/{project_name}'
                    result[project_name].append(event)
        return result

    def get_project_name(self, project_id):

        if self.projects.get(project_id):
            return self.projects[project_id]['path_with_namespace']

        req = urllib.request.Request(
                url=f'{self.api_entry_point}/projects/{project_id}',
                headers=self.headers)

        with urllib.request.urlopen(req) as res:
            self.projects[project_id] = json.load(res)

        return self.projects[project_id]['path_with_namespace']

    def get_target_url(self, project_id, target_type, target_id):

        # 2017-07-30 時点で対象 issue/mr の iid を取得する方法が無いため
        # 一時的に API v3 を使う
        # ref. https://gitlab.com/gitlab-org/gitlab-ce/issues/34873

        if self.target_info.get(f'p{project_id}t{target_id}'):
            return self.target_info[f'p{project_id}t{target_id}']['web_url']

        if target_type == 'Issue':
            request_url = f'{self.api_v3_entry_point}/projects/{project_id}/issues/{target_id}'
        elif target_type == 'MergeRequest':
            request_url = f'{self.api_v3_entry_point}/projects/{project_id}/merge_requests/{target_id}'
        else:
            return ''

        req = urllib.request.Request(url=request_url, headers=self.headers)

        with urllib.request.urlopen(req) as res:
            self.target_info[f'p{project_id}t{target_id}'] = json.load(res)

        return self.target_info[f'p{project_id}t{target_id}']['web_url']

    def print_activity_of_repository(self, from_, to_, needs_private=False):
        gl_events = self.user_events(from_, to_)
        for key in gl_events:
            print(f'### {key}\n')
            for event in gl_events[key]:
                print(self.generate_output_line(event))
            print()

    @classmethod
    def generate_output_line(cls, event):
        result = {'title': '', 'body': '', 'link': ''}

        if event['action_name'] == 'opened':
            result['title'] = event["action_name"]
            result['link'] = event['_target_url']

            if len(event["target_title"]) > 30:
                result['body'] = repr(event["target_title"])[:30] + '...'
            else:
                result['body'] = repr(event["target_title"])

        elif event['action_name'] == 'commented on':
            result['title'] = event["target_title"] + '(comment)'
            result['link'] = event['_target_url']

            if len(event['note']['body']) > 30:
                result['body'] = repr(event['note']['body'])[:30] + '...'
            else:
                result['body'] = repr(event['note']['body'])

        elif event['action_name'] == 'closed':

            result['title'] = event["action_name"]
            result['link'] = event['_target_url']

            if len(event["target_title"]) > 30:
                result['body'] = repr(event["target_title"])[:30] + '...'
            else:
                result['body'] = repr(event["target_title"])

        elif event['action_name'] == 'created':

            result['title'] = event['_target_url']
            result['link'] = event['_target_url']
            result['body'] = event["action_name"]

        return '- [{title}]({link}): {body}'.format(**result)
