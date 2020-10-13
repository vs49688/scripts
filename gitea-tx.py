#!/usr/bin/env python3

import json
import urllib.request
import urllib.parse

FROM_ORGS = [
    'Org1Name',
    'Org2Name',
]

TO_ORG = 'ToOrgName'

class giteaapi(object):
    def __init__(self, api, token):
        self._api = api
        self._token = token

    def _post_url_raw(self, url, data, content_type, method='POST'):
        req = urllib.request.Request(
            url=url,
            headers={
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/json',
                'Content-Type': content_type,
                'Authorization': f'token {self._token}'
            },
            data=data,
            method=method
        )

        with urllib.request.urlopen(req) as x:
            return (x.getcode(), json.loads(x.read().decode('utf-8')))

    def _post_url_json(self, url, data, method='POST'):
        return self._post_url_raw(url, json.dumps(data).encode('utf-8'), 'application/json', method)

    def get_org_repos(self, org):
        url = urllib.parse.urljoin(self._api, f'orgs/{org}/repos')

        result = self._post_url_raw(url, b'', '', 'GET')
        if result[0] != 200:
            raise Exception(f'Error querying org {org}')
        return result[1]

    def transfer(self, owner, name, to_owner):
        body = {'new_owner': to_owner, 'team_ids': None}

        url = urllib.parse.urljoin(self._api, f'repos/{owner}/{name}/transfer')
        print(url)

        result = self._post_url_json(url, body, 'POST')
        if result[0] != 202:
            raise Exception('Migration error')

        return result[1]

def main():
    gitea = giteaapi('https://gitea.example.com/git/api/v1/', 'gitea-token')

    # for org in FROM_ORGS:
    #     x = gitea.get_org_repos(org)
    #     for repo in x:
    #         print(f"migrating {org}/{repo['name']}")
    #         y = gitea.transfer(org, repo['name'], TO_ORG)

    for org in FROM_ORGS:
        url = urllib.parse.urljoin(gitea._api, f'orgs/{org}')

        req = urllib.request.Request(url=url, headers={'Authorization': f'token {gitea._token}'}, method='DELETE')
        with urllib.request.urlopen(req) as x:
            print(f"del {org} = {x.getcode()}")

    return 0

if __name__ == '__main__':
    exit(main())
