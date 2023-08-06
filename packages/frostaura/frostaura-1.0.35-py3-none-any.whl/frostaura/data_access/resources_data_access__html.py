'''This module defines HTTP resources data access component.'''
import requests
from bs4 import BeautifulSoup
from logging import debug, info
from frostaura.data_access.resources_data_access import IResourcesDataAccess

class HtmlResourcesDataAccess(IResourcesDataAccess):
    '''Component to perform HTML resource related actions.'''

    def __init__(self, config: dict = {}):
        self.config = config
        self.default_user_agent = 'PostmanRuntime/7.29.0'

    def get_resource(self, path: str) -> BeautifulSoup:
        '''Get a queryable HTML page via a URL (path).'''

        info(f'Fetching HTML page from URL "{path}".')

        user_agent_setting_key: str = 'user-agent'

        if user_agent_setting_key not in self.config:
            debug(f'No key "{user_agent_setting_key}" found in config. Defaulting to user agent value "{self.default_user_agent}".')

            self.config[user_agent_setting_key] = self.default_user_agent
        else:
            debug(f'User agent override found in config. Using value "{self.config[user_agent_setting_key]}".')

        response: requests.Response = requests.get(url=path, headers={
            'User-Agent': self.config[user_agent_setting_key]
        })
        response_text: str = response.text

        return BeautifulSoup(response_text, 'html.parser')
