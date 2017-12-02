import tzlocal
from github import Github


class footprintGithub(Github):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.github_user = self.get_user(self.get_user().login)
        self.pickup_types = [
            'IssuesEvent',
            'PullRequestEvent',
            'PullRequestReviewCommentEvent',
            'IssueCommentEvent',
            'CommitCommentEvent',
        ]

    def print_activity_of_repository(self, from_, to_, needs_private=False):
        gh_message_info = self.generate_user_events(from_, to_, needs_private)
        for key in gh_message_info.keys():
            print(f'### {key}\n')
            for event in gh_message_info[key]:
                print(self.generate_output_line(event))
            print()

    def generate_user_events(self, from_, to_, needs_private=False, timezone=tzlocal.get_localzone()):

        message_info = {}
        for event in self.github_user.get_events():

            from_delta = from_ - timezone.localize(event.created_at)
            to_delta = to_ - timezone.localize(event.created_at)

            if from_delta.days <= 0 and to_delta.days >= 0:
                if needs_private or event.raw_data['public']:
                    if event.type in self.pickup_types:
                        if not message_info.get(event.repo.name):
                            message_info[event.repo.name] = []
                        message_info[event.repo.name].append(event)

        return message_info

    @classmethod
    def generate_output_line(cls, event):

        result = {'title': '', 'body': '', 'link': ''}

        if event.type == 'IssueCommentEvent':

            result['title'] = event.payload["issue"]["title"] + '(comment)'
            result['link'] = event.payload['comment']['html_url']

            if len(event.payload["comment"]["body"]) > 30:
                result['body'] = repr(event.payload["comment"]["body"])[:30] + "...'"
            else:
                result['body'] = repr(event.payload["comment"]["body"])

        elif event.type == 'PullRequestReviewCommentEvent':
            result['title'] = event.payload["pull_request"]["title"] + '(comment)'
            result['link'] = event.payload['comment']['html_url']

            if len(event.payload["comment"]["body"]) > 30:
                result['body'] = repr(event.payload["comment"]["body"])[:30] + "...'"
            else:
                result['body'] = repr(event.payload["comment"]["body"])

        elif event.type == 'IssuesEvent':
            result['title'] = event.payload['action']
            result['link'] = event.payload['issue']['html_url']

            if len(event.payload["issue"]["title"]) > 30:
                result['body'] = repr(event.payload["issue"]["title"])[:30] + "...'"
            else:
                result['body'] = repr(event.payload["issue"]["title"])

        elif event.type == 'PullRequestEvent':
            result['title'] = event.payload['action']
            result['link'] = event.payload['pull_request']['html_url']

            if len(event.payload["pull_request"]["title"]) > 30:
                result['body'] = repr(event.payload["pull_request"]["title"])[:30] + "...'"
            else:
                result['body'] = repr(event.payload["pull_request"]["title"])

        return '- [{title}]({link}): {body}'.format(**result)
