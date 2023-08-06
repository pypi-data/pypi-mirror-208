import os

from .utils import graphql_request


def setToken(token):
    """
        设置 用户申请的 sdk token 

        :params: token token 

        >>> cloudpss.setToken(token)
    """
    os.environ['CLOUDPSS_TOKEN'] = token


def userToken(token):
    query = '''
        query ($input: UserTokenInput!) {               
            userToken(input: $input){                   
                user{                      
                    name                 
                }               
            } 
        }          
    '''

    result = graphql_request(query, {'input': {'token': token}})
    if 'errors' in result:
        raise Exception(result['errors'])
    return result['data']['userToken']['user']


def userName(token=None):
    if token is None:
        token = os.environ.get('CLOUDPSS_TOKEN', None)
    if token is None:
        raise Exception('token is None')
    return userToken(token)['name']


def verifyToken(token):
    return userToken(token)
