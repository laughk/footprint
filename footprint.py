import argparse
import datetime

from github import Github
import settings

PICKUP_TYPES = [
    'IssuesEvent',
    'PullRequestEvent',
    'PullRequestReviewCommentEvent',
    'IssueCommentEvent',
    'CommitCommentEvent',
]


def main():

    utc_today = datetime.datetime.utcnow()

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--from', dest='from_str', default='', type=str)
    parser.add_argument('-t', '--to', dest='to_str', default='', type=str)
    parser.add_argument('-P', '--private', dest='needs_private', action='store_true', default=False)
    args = parser.parse_args()

    if args.from_str:
        from_ = datetime.datetime.strptime(args.from_str, '%Y-%m-%d')
    else:
        from_ = utc_today

    if args.to_str:
        to_ = datetime.datetime.strptime(args.to_str, '%Y-%m-%d')
    else:
        to_ = utc_today

    gh = Github(settings.GITHUB_TOKEN, per_page=300)
    if settings.GITHUB_USER:
        user = gh.get_user(settings.GITHUB_USER)
    else:
        user = gh.get_user(gh.get_user().login)

    header = generate_message_header(from_, to_)
    print(header)
    print()

    message_info = generate_user_events(user, from_, to_, args.needs_private)
    for key in message_info.keys():
        print(f'# {key}')
        print()
        for event in message_info[key]:
            print(generate_output_line(event))
        print()


def generate_message_header(from_, to_):
    days_of_period = (to_ - from_).days
    if days_of_period:
        return f'{days_of_period} days of activities\n===='
    else:
        return 'Activity in {0}\n===='.format(from_.strftime('%Y-%m-%d'))


def generate_user_events(user, from_, to_, needs_private=False):

    message_info = {}
    for event in user.get_events():

        from_delta = from_ - event.created_at
        to_delta = to_ - event.created_at

        if from_delta.days <= 0 and to_delta.days >= 0:
            if needs_private or event.raw_data['public']:
                if event.type in PICKUP_TYPES:
                    if not message_info.get(event.repo.name):
                        message_info[event.repo.name] = []
                    message_info[event.repo.name].append(event)

    return message_info


def generate_output_line(event):

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


if __name__ == '__main__':
    main()
