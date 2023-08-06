import json
import os
from github import Github

from util.util import Util
from util.config_reader import ConfigReader

class GithubRepo:
    def __init__(self, args):
        self.github_config = ConfigReader.get(args, 'github')

        if not self.use_local():
            self.g = Github(self.github_config['token'])
            self.repo = self.github_config['repo']

    def get(self, file_name):
        content = ''
        if self.use_local():
            with open(os.path.join(self.github_config.get('path'), file_name), 'r') as f:
                content = f.read()
        else:
            repo = self.g.get_repo(self.repo)
            content = repo.get_contents(file_name).decoded_content
            
        return content

    def get_json(self, file_name):
        return json.loads(self.get(file_name))

    def use_local(self):
        return self.github_config.get('local', False)