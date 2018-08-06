import argparse
import os
from collections import defaultdict
from datetime import datetime, timedelta

import requests
from requests.auth import HTTPBasicAuth

GITHUB_ACCESS_TOKEN = os.environ['GITHUB_ACCESS_TOKEN']

parser = argparse.ArgumentParser(description='ghpr')
parser.add_argument('--user', help='Username')
parser.add_argument('--org', help='Orgnization')

sub = parser.add_subparsers()
period_monthly = sub.add_parser('monthly', help='List monthly pull requests')
period_weekly = sub.add_parser('weekly', help='List weekly pull requests')
period_daily = sub.add_parser('daily', help='List daily pull requests')
review_pull_request = sub.add_parser('pr', help='List review pull requests')


def list_org_repos(org, auth):
    url = "https://api.github.com/orgs/{}/repos".format(org)
    resp = requests.get(url, params={'type': 'member'}, auth=auth)
    data = resp.json()
    return [r['name'] for r in data]


def list_review_pull_requests(org, auth):
    # url = "https://api.github.com/repos/{}/{}/pulls".format(owner, repo)
    # params = {
    #     'filter': 'assigned',
    #     'state': 'all',
    #     'sort': 'updated',
    #     'since': since
    # }
    url = "https://api.github.com/orgs/{}/issues".format(org)
    params = {
        'filter': 'all',
        'state': 'open',
        'sort': 'updated',
        'labels': 'REVIEW',
    }
    resp = requests.get(url, params=params, auth=auth)
    data = resp.json()
    pull_requests =  [issue for issue in data if 'pull_request' in issue]

    repos = defaultdict(list)

    for pr in pull_requests:
        repos[pr['repository']['full_name']].append(pr)

    for repo, prs in repos.items():
        print()
        print("## ", repo)
        for pr in prs:
            print("- [{} #{}]({})".format(pr['title'], pr['number'], pr['html_url']))

def list_my_pull_requests(org, auth, since):
    url = "https://api.github.com/orgs/{}/issues".format(org)
    params = {
        'filter': 'assigned',
        'state': 'all',
        'sort': 'updated',
        'since': since
    }
    resp = requests.get(url, params=params, auth=auth)
    data = resp.json()
    pull_requests =  [issue for issue in data if 'pull_request' in issue]

    repos = defaultdict(list)

    for pr in pull_requests:
        repos[pr['repository']['full_name']].append(pr)

    for repo, prs in repos.items():
        print("- ", repo)
        for pr in prs:
            print("  - [{} #{}]({})".format(pr['title'], pr['number'], pr['html_url']))


def list_monthly(args):
    org = args.org
    auth = HTTPBasicAuth(args.user, GITHUB_ACCESS_TOKEN)

    first_of_month = datetime.today().replace(day=1)
    since = first_of_month.isoformat()  # FIXME JST -> UTC

    list_my_pull_requests(org, auth, since)


def list_weekly(args):
    org = args.org
    auth = HTTPBasicAuth(args.user, GITHUB_ACCESS_TOKEN)

    today = datetime.today()
    first_of_week = today - timedelta(today.weekday())
    since = first_of_week.isoformat()  # FIXME JST -> UTC

    list_my_pull_requests(org, auth, since)


def list_daily(args):
    org = args.org
    auth = HTTPBasicAuth(args.user, GITHUB_ACCESS_TOKEN)

    today = datetime.today()
    since = today.date().isoformat()  # FIXME JST -> UTC

    list_my_pull_requests(org, auth, since)


def list_pull_requests(args):
    org = args.org
    auth = HTTPBasicAuth(args.user, GITHUB_ACCESS_TOKEN)
    list_review_pull_requests(org, auth)


def main():
    period_monthly.set_defaults(func=list_monthly)
    period_weekly.set_defaults(func=list_weekly)
    period_daily.set_defaults(func=list_daily)
    review_pull_request.set_defaults(func=list_pull_requests)
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
