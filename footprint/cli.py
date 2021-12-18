import argparse
import datetime

import tzlocal

from .modules import footprintGitlab
from .modules import footprintGithub
from .modules.config import footprint_config
from . import __version__


def main():

    config = footprint_config()
    local_tz = tzlocal.get_localzone()

    parser = argparse.ArgumentParser()
    parser.add_argument(
            '-f', '--from', dest='from_str', default='', type=str,
            help='set start of date formated "YYYY-MM-DD". (default: current day)')
    parser.add_argument(
            '-t', '--to', dest='to_str', default='', type=str,
            help='set end of start date formated "YYYY-MM-DD". (default: current day)')
    parser.add_argument(
            '-P', '--private', dest='needs_private', action='store_true',
            help='enable get data from private repository. (default: disable)')
    parser.add_argument(
            '--gl', dest='enable_gitlab', action='store_true',
            help='[Experimental] enable getting status from gitlab.com.')
    parser.add_argument('-v', '--version', action='version', version=__version__)

    args = parser.parse_args()

    from_ = date_parser(args.from_str, local_tz)
    to_ = date_parser(args.to_str, local_tz)

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


def date_parser(date_str, timezone):

    today = datetime.datetime.today()

    if date_str:
        date_result = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    else:
        date_result = today

    return date_result


if __name__ == '__main__':
    main()
