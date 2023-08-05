import time
from typing import List, Optional

import requests
from shopcloud_secrethub import SecretHub

from . import helpers


def check_health(url: str, **kwargs) -> int:
    is_simulate = kwargs.get('is_simulate', False)
    status_code = None
    try:
        if is_simulate:
            return 200
        response = requests.get(url, timeout=30)
        return response.status_code
    except Exception:
        status_code = None
    return status_code



def load_base_urls(config) -> List[str]:
    items = {x.get('base_url') for x in config.load_projects() if x.get('base_url') is not None}
    return list(set(items))


def load_apps(config) -> List[dict]:
    return [
        x for x in config.load_projects()
        if x.get('name') is not None and ("django" in x.get('types', []) or "serverless" in x.get('types', []))
    ]


def get_api_token(**kwargs) -> Optional[str]:
    if kwargs.get('is_simulate', False):
        return 'test-token'
    hub = SecretHub(user_app="microservice-cli")
    return hub.read('talk-point/app-microservices-cli/production/deploy-api-token')


def generate_release(data: dict, **kwargs) -> dict:
    try:
        is_simulate = kwargs.get('is_simulate', False)
        repo = data.get('repo')
        if repo is None:
            return {
                'status': 'ERROR',
                'message': 'Missing repo',
            }
        pieces = repo.replace('https://github.com/', '').split('/')
        if len(pieces) != 2:
            return {
                'status': 'ERROR',
                'message': 'Invalid repo',
            }
        owner = pieces[0]
        repo = pieces[1]
        if is_simulate:
            return {
                'status': 'OK',
            }
        for i in range(10):
            response = requests.post(
                'https://shopcloud-deploy-api-2yj8sc5z.ew.gateway.dev/pull-request/open',
                headers={
                    'X-Api-Key': get_api_token(is_simulate=is_simulate),
                },
                json={
                    'owner': owner,
                    'repo': repo,
                }
            )
            print(f'+ {repo} - {response.status_code}')
            if not (response.status_code >= 200 and response.status_code <= 299):
                print(f'+ {repo} - {response.text}')
                if response.status_code == 403 and i < 9:
                    time.sleep(30)
                    continue
                return {
                    'status': 'ERROR',
                    'message': 'Error while creating pull request',
                }

            return {
                'status': 'OK',
            }

        return {
            'status': 'OK',
        }
    except Exception as e:
        return {
            'status': 'ERROR',
            'message': str(e),
        }


def cli_main(args, config) -> int:
    return_code = 0
    if args.action == 'health':
        items = load_base_urls(config)
        datas = [{
            'url': x,
            'status_code': check_health(x, is_simulate=args.simulate)
        } for x in items]
        datas = [{
            **x,
            **{
                'status': 'DOWN' if x.get('status_code') is None else 'OK' if 200 <= x.get('status_code') < 300 else 'DOWN'
            }
        } for x in datas]

        if args.debug:
            print(datas)

        for d in datas:
            if d.get('status') == 'DOWN':
                print(f"- {d.get('url')} {helpers.bcolors.FAIL}DOWN{helpers.bcolors.ENDC}")
            elif d.get('status') == 'OK':
                print(f"- {d.get('url')} {helpers.bcolors.OKGREEN}{d.get('status_code')} OK{helpers.bcolors.ENDC}")

        if [x for x in datas if x.get('status') == 'DOWN']:
            return 1
    elif args.action == 'list':
        items = load_apps(config)
        for item in items:
            print(f"- {item.get('name')} {item.get('base_url')}")
    elif args.action == 'release':
        items = load_apps(config)
        if args.name is not None:
            items = [x for x in items if x.get('name') == args.name]
        items = [{
            'item': x,
            'action': generate_release(x, is_simulate=args.simulate),
        } for x in items]

        print('Result')

        for item in items:
            if item.get('action').get('status') == 'OK':
                print(helpers.bcolors.OKGREEN + f"- {item.get('item').get('name')} {item.get('action').get('status')}" + helpers.bcolors.ENDC)
            else:
                print(f"+ {item.get('item').get('name')} {item.get('action').get('status')} - {item.get('action').get('message')}")
                return_code = 1
    return return_code
