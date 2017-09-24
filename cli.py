import argparse
import datetime

from footprint.modules import footprintGitlab
from footprint.modules import footprintGithub
from footprint.modules.config import footprint_config


def main():

    config = footprint_config()

    today = datetime.datetime.today()

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--from', dest='from_str', default='', type=str)
    parser.add_argument('-t', '--to', dest='to_str', default='', type=str)
    parser.add_argument('-P', '--private', dest='needs_private', action='store_true', default=False)
    parser.add_argument(
            '--gl', dest='enable_gitlab', action='store_true',
            help='[Experimental] enable getting status from gitlab.com.')
    args = parser.parse_args()

    if args.from_str:
        from_ = datetime.datetime.strptime(args.from_str, '%Y-%m-%d')
    else:
        from_ = today

    if args.to_str:
        to_ = datetime.datetime.strptime(args.to_str, '%Y-%m-%d')
    else:
        to_ = today

    header = generate_message_header(from_, to_)
    print(f'{header}\n')

    github_token = config.get('github', 'token')
    gh = footprintGithub(github_token, per_page=300)
    gh.print_activity_of_repository(from_, to_, args.needs_private)

    if args.enable_gitlab:
        gitlab_token = config.get('gitlab.com', 'token')
        gl = footprintGitlab(private_token=gitlab_token)
        gl.print_activity_of_repository(from_, to_, args.needs_private)


def generate_message_header(from_, to_):
    days_of_period = (to_ - from_).days
    if days_of_period:
        return f'{days_of_period} days of activities\n===='
    else:
        return 'Activity in {0}\n===='.format(from_.strftime('%Y-%m-%d'))


if __name__ == '__main__':
    main()
