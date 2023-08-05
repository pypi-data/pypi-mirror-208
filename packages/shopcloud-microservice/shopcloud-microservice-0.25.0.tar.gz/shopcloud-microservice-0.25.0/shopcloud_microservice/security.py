import time
from typing import List, Optional

import requests
from joblib import Parallel, delayed, parallel_backend
from shopcloud_secrethub import SecretHub

from . import helpers


def github_fetch_pull_requests(owner: str, repo: str, **kwargs):
    if kwargs.get('is_simulate', False):
        return [{
            'merged': False,
            'number': 1,
            'mergeable': True,
            'title': '[SECURITY] Add automatic dependencies upgrade',
            'mergeable_state': 'clean',
        }]
    token = kwargs.get('api_token', None)
    if token is None:
        raise Exception('Missing API token')

    response = requests.get(
        f'https://api.github.com/repos/{owner}/{repo}/pulls',
        headers={
            'Authorization': f'token {token}',
        },
        params={
            'state': 'open',
            'sort': 'created',
            'direction': 'asc',
        },
    )

    if not (response.status_code >= 200 and response.status_code <= 299):
        raise Exception('Error while fetching pull requests')

    return response.json()


def github_fetch_pull_request(owner: str, repo: str, pull_request_number: int, **kwargs):
    if kwargs.get('is_simulate', False):
        return {
            'merged': False,
            'number': 1,
            'mergeable': True,
            'title': '[SECURITY] Add automatic dependencies upgrade',
        }
    token = kwargs.get('api_token', None)
    if token is None:
        raise Exception('Missing API token')

    response = requests.get(
        f'https://api.github.com/repos/{owner}/{repo}/pulls/{pull_request_number}',
        headers={
            'Authorization': f'token {token}',
        },
    )

    if not (response.status_code >= 200 and response.status_code <= 299):
        raise Exception('Error while fetching pull requests')

    return response.json()


def github_merge_pull_request(owner: str, repo: str, pull_request_number: int, **kwargs):
    if kwargs.get('is_simulate', False):
        return {}
    token = kwargs.get('api_token', None)
    if token is None:
        raise Exception('Missing API token')

    for i in range(10):
        response = requests.put(
            f'https://api.github.com/repos/{owner}/{repo}/pulls/{pull_request_number}/merge',
            headers={
                'Authorization': f'token {token}',
            },
        )

        print(response.text)
        if not (response.status_code >= 200 and response.status_code <= 299):
            if response.status_code == 403 and i < 9:
                time.sleep(30)
                continue
            raise Exception('Error while fetching pull requests')

    return response.json()


def get_api_token(**kwargs) -> Optional[str]:
    if kwargs.get('is_simulate', False):
        return 'test-token'
    hub = SecretHub(user_app="microservice-cli")
    return hub.read('talk-point/app-microservices-cli/production/github-key')


def run_repo_merge_security_pull_requests(owner: str, repo: str, **kwargs) -> Optional[bool]:
    try:
        is_simulate = kwargs.get('is_simulate', False)
        api_token = kwargs.get('api_token')

        pull_requests = [
            x for x in
            github_fetch_pull_requests(
                owner,
                repo,
                is_simulate=is_simulate,
                api_token=api_token,
            )
            if "[SECURITY] Add automatic dependencies upgrade" in x.get('title')
        ]
        if len(pull_requests) == 0:
            print(f'+ {owner}/{repo} - No pull requests found')
            return None

        pull_request = github_fetch_pull_request(
            owner,
            repo,
            pull_requests[0].get('number'),
            is_simulate=is_simulate,
            api_token=api_token
        )
        if pull_request.get('merged') in [None, True]:
            print(f'+ {owner}/{repo} - Already merged')
            return None

        if pull_request.get('mergeable') in [None, False]:
            url = pull_request.get('html_url')
            print(helpers.bcolors.FAIL + f'+ {owner}/{repo} - Can not be merged - {url}' + helpers.bcolors.ENDC)
            return None

        if pull_request.get('mergeable_state') != 'clean':
            url = pull_request.get('html_url')
            print(helpers.bcolors.FAIL + f'+ {owner}/{repo} - Can not be merged - {url}' + helpers.bcolors.ENDC)
            return None

        github_merge_pull_request(
            owner,
            repo,
            pull_request.get('number'),
            is_simulate=is_simulate,
            api_token=api_token
        )
        print(helpers.bcolors.OKGREEN + f'+ {owner}/{repo} - Merging pull request' + helpers.bcolors.ENDC)
        return True
    except Exception as e:
        print(helpers.bcolors.FAIL + f'+ {owner}/{repo} - Error while merging pull request - {e}' + helpers.bcolors.ENDC)
        return False


def load_repos(config) -> List[str]:
    repos = {x.get('repo') for x in config.load_projects() if x.get('repo') is not None}
    repos = [
        "/".join(x.replace('https://github.com/', '').split('/')[1:])
        for x in repos if x is not None
    ]
    return list(repos)


def cli_main(args, config):
    if args.action == 'merge-security-pull-requests':
        owner = 'Talk-Point'
        repos = [args.repo] if args.repo is not None else load_repos(config)
        api_token = get_api_token(is_simulate=args.simulate)

        with parallel_backend('threading', n_jobs=-1):
            Parallel()(
                delayed(run_repo_merge_security_pull_requests)(owner, m, is_simulate=args.simulate, api_token=api_token)
                for m in repos
            )
    elif args.action == 'ci-secrets-rolling':
        print('Got to https://github.com/organizations/Talk-Point/settings/secrets/actions')
        print('- PYPY_TOKEN - generate a new token on the PyPi website')
        print('- SECRETHUB_TOKEN - rotate the token for the github-ci user')
        print('- TOKEN - rotate the token for the github-ci user in TP-Server')

    return 0
