import time
import urllib
import simplejson as json
from httplib2 import Http
from urlparse import urljoin

try:
    from urlparse import parse_qs, parse_qsl
except ImportError:
    from cgi import parse_qs, parse_qsl

API_VERSION = '1'

class Agency(object):
    debug = False
    endpoints = {
        'client': 'clients/%(id)s.json',
        'clients': 'clients.json',
        'project': 'clients/%(client)s/projects/%(id)s.json',
        'projects': 'clients/%(client)s/projects.json',
        'approval': 'clients/%(client)s/projects/%(project)s/approvals/%(id)s.json',
        'approvals': 'clients/%(client)s/projects/%(project)s/approvals.json',
        'page': 'clients/%(client)s/projects/%(project)s/pages/%(id)s.json',
        'pages': 'clients/%(client)s/projects/%(project)s/pages.json',
        'revision': 'clients/%(client)s/projects/%(project)s/pages/%(page)s/revision/%(id).json',
        'revisions': 'clients/%(client)s/projects/%(project)s/pages/%(page)s/revisions.json'
    }
    
    def __init__(self, subdomain, api_key, api_version=API_VERSION, host="api.clientend.com"):
        self.host = host
        self.api_version = api_version
        self.api_key = api_key
        self.subdomain = subdomain
        self.http = Http()
        self.uri = "http://%s/v%s" % (host, api_version)
        
        if self.api_key is None or self.subdomain is None:
            raise ValueError("Must set API Key")
    
    def __str__(self):
        return self.__unicode__()
    
    def __unicode__(self):
        return 'Agency (api_key=%s, subdomain=%s)' % (self.api_key, self.subdomain)

    def endpoint(self, name, **kwargs):
        try:
            endpoint = self.endpoints[name]
        except KeyError:
            raise Exception('No endpoint named "%s"' % name)
        try:
            endpoint = endpoint % kwargs
        except KeyError, e:
            raise TypeError('Missing required argument "%s"' % (e.args[0],))
        return urljoin(urljoin(self.uri, 'api/v'+ self.api_version + '/'), endpoint)
    
    # Clients
    def get_clients(self):
        endpoint = self.endpoint('clients')
        return self._request(endpoint, 'GET')
    
    def get_client(self, id):
        endpoint = self.endpoint('client', id=id)
        return self._request(endpoint, 'GET')
    
    # Projects
    def get_projects(self, client):
        endpoint = self.endpoint('projects', client=client)
        return self._request(endpoint, 'GET')
        
    def get_project(self, client, id):
        endpoint = self.endpoint('project', client=client, id=id)
        return self._request(endpoint, 'GET')
    
    # Approvals
    def get_approvals(self, client, project):
        endpoint = self.endpoint('approvals', client=client, project=project)
        return self._request(endpoint, 'GET')
        
    def get_approvals(self, client, project, id):
        endpoint = self.endpoint('approval', client=client, project=project, id=id)
        return self._request(endpoint, 'GET')
    
    # Projects
    def get_pages(self, client, project):
        endpoint = self.endpoint('pages', client=client, project=project)
        return self._request(endpoint, 'GET')
        
    def get_page(self, client, project, id):
        endpoint = self.endpoint('page', client=client, project=project, id=id)
        return self._request(endpoint, 'GET')
    
    # Projects
    def get_revisions(self, client, project, page):
        endpoint = self.endpoint('revisions', client=client, project=project, page=page)
        return self._request(endpoint, 'GET')
        
    def get_revision(self, client, project, page, id):
        endpoint = self.endpoint('revision', client=client, project=project, page=page, id=id)
        return self._request(endpoint, 'GET')
    
    def _request(self, endpoint, method, data=None):
        body = None
        
        if data is None:
            data = { 'api_key': self.api_key }
        else:
            if isinstance(data, dict):
                data['api_key'] = self.api_key
        
        if method == "GET" and isinstance(data, dict):
            endpoint = endpoint + '?' + urllib.urlencode(data)
        else:
            if isinstance(data, dict):
                body = urllib.urlencode(data)
            else:
                body = data
        
        resp, content = self.http.request(endpoint, method, body=body)
        
        if self.debug:
            print resp
            print content
            
        if content:
            try:
                content = json.loads(content)
            except ValueError:
                raise DecodeError(resp, content)

        if resp['status'][0] != '2':
            code = resp['status']
            message = content
            if isinstance(content, dict):
                code = content['code']
                message = content['message']
            raise APIError(code, message, resp)
        
        return content