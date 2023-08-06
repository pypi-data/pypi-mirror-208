'''This module defines private manager components.'''

class IAssetReportingManager:
    '''Component to perform functions related to asset reporting.'''

    def send_reports(self):
        '''Generate and send asset reports.'''

        raise NotImplementedError()
