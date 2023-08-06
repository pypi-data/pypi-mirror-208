import requests
from collections import namedtuple
from plumbum import local

Github = namedtuple('Github', 'repo_name description owner token')

def create_repo(github):
    return requests.post(
        'https://api.github.com/orgs/{}/repos'.format(github.owner),
        headers = {
            'Authorization': 'token {}'.format(github.token),
            'Accept': 'application/vnd.github.v3+json'
        },
        json={
            'name': github.repo_name,
            'private': True,
            'description': github.description,
            'allow_merge_commit': False,
            'allow_rebase_merge': False
        }
    )

def get_repo(github):
    return requests.get(
        'https://api.github.com/repos/{}/{}'.format(
            github.owner,
            github.repo_name
        ),
        headers = {
            'Authorization': 'token {}'.format(github.token),
            'Accept': 'application/vnd.github.v3+json'
        },
    )

def create_from_template(github):
    return requests.post(
        'https://api.github.com/repos/{}/{}/generate'.format(
            github.owner,
            github.template_name
        ),
        headers = {
            'Authorization': 'token {}'.format(github.token),
            'Accept': 'application/vnd.github.baptiste-preview+json'
        },
        json={
            'name': github.repo_name,
            'owner': github.owner,
            'private': True,
            'description': github.description
        }
    )

class Repo(object):
    _remote = None
    _branch = None
    _hash = None
    _repo = None

    @property
    def branch(self):
        if not self._branch:
            self._branch = self._get_branch()
        return self._branch

    @property
    def hash(self):
        if not self._hash:
            self._hash = self._get_hash()
        return self._hash

    @property
    def repo(self):
        if not self._repo:
            self._repo = self._get_repo()
        return self._repo

    def __init__(self, path='.'):
        self._path = path
        self._git = local['git']

    def init(self):
        self._git(
            '-C',
            self._path,
            'init'
        )
        return self

    def set_remote(self, owner, repo_name, remote_url='https://github.com/{}/{}.git'):
        remote = remote_url.format(
            owner,
            repo_name
        )

        self._git(
            '-C',
            self._path,
            'remote',
            'add',
            'origin',
            remote
        )
        self._remote = remote
        return self

    def add(self):
        self._git(
            '-C',
            self._path,
            'add',
            '.'
        )
        return self

    def commit(self, message):
        self._git(
            '-C',
            self._path,
            'commit',
            '-a',
            '-m',
            message
        )
        return self

    def push(self, branch='main'):
        self._git(
            '-C',
            self._path,
            'push',
            '--set-upstream',
            'origin',
            branch
        )
        self._branch = branch
        return self

    def _get_repo(self):
        repo = self._git(
            '-C',
            self._path,
            'rev-parse',
            '--show-toplevel'
        )
        return repo.split('/')[-1].replace('\n', '')

    def _get_branch(self):
        branch = self._git(
            '-C',
            self._path,
            'branch',
            '--show-current'
        )
        return branch.replace('\n', '')

    def _get_hash(self):
        hash = self._git(
            '-C',
            self._path,
            'show-ref',
            '--head',
            '--hash',
            'head'
        )
        return hash.replace('\n', '')
