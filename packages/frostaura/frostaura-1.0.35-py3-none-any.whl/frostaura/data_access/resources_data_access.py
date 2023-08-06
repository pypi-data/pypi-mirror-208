'''This module defines the interface for the resources data access components.'''

class IResourcesDataAccess:
    '''Component to perform resource related actions.'''

    def get_resource(self, path: str) -> object:
        '''Get a resource's content.'''

        raise NotImplementedError()
