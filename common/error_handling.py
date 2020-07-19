error_codes = {
    ## -- todo
    '01x001': 'Invalid version.',
    '01x002': 'Invalid or missing {key}. Value must be an integer value greater than {minimum} and less than {maximum}.',
    '01x003': None, # Removed due to code update that made this obsolete. This code can be reused.
    '01x004': 'Invalid site_id. Value must be a valid 4 character id found in http://nadp.slh.wisc.edu/data/sites/CSV/?net=NTN.',
    '01x005': 'Invalid include_inactive. Value must be a boolean value (True or False).',
    '01x006': 'Invalid location. Value must be a tuple of floats values.',
    '01x007': 'Invalid or missing {key}. Value must be a float value greater than {minimum} and less than {maximum}.',
    
    '01x999': 'Unknown error occured.',
}


def get_error(error_key, **kwargs):
    '''
        Helper function that returns error codes in a common format.
    '''
    return {error_key: error_codes.get(error_key, '').format(**kwargs)}
