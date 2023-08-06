'''This module defines embedded resources data access component.'''
from typing import BinaryIO
from logging import info
import inspect
from frostaura.data_access.resources_data_access import IResourcesDataAccess

class EmbeddedResourcesDataAccess(IResourcesDataAccess):
    '''Component to perform embedded resource related actions.'''

    def __init__(self, config: dict = {}):
        self.config = config

    def get_resource(self, path: str) -> BinaryIO:
        '''Get a resource as a byte stream that was embedded in a given package.'''

        directories_to_move_up: int = 2
        current_executing_path: str = inspect.getfile(self.__class__)
        current_executing_path = current_executing_path.replace('\\', '/')
        root_path: str = '/'.join(current_executing_path.split('/')[:-directories_to_move_up])
        resource_path: str = f'{root_path}/resources/{path}'

        info(f'Fetching embedded resource "{resource_path}".')

        return open(resource_path)
