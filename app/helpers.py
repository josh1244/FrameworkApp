'''This file contains helper functions for the application, including asset path retrieval.
'''

import os

def get_asset_path(filename):
        '''Returns the path to the specified asset image.'''
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", filename)
