'''
See:
    http://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods
    http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html
'''

class HttpMethod(object):
    GET = 'GET'
    HEAD = 'HEAD'
    POST  = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    TRACE = 'TRACE'
    OPTIONS = 'OPTIONS'
    CONNECT = 'CONNECT'
    PATCH = 'PATCH'
