import re
from urllib.parse import urlparse, parse_qs
from http.cookies import SimpleCookie

from cerberus import Validator
import playwright.sync_api

from watchtower_browser_testing import config


class ValidatorError(Exception): pass


class RequestWrapper(object):

    def __init__(self,
                 request):

        self.request = request
        self.errors = None

    @property
    def url(self):

        return self.request.url

    @property
    def parsed_url(self):

        return urlparse(self.url)

    @property
    def parsed_qs(self):

        parsed_qs = parse_qs(self.parsed_url.query)

        for key, value in parsed_qs.items():
            if isinstance(value, list):
                if len(value) == 1:
                    parsed_qs[key] = value[0]
                elif len(value) == 0:
                    parsed_qs.pop(key)

        return parsed_qs

    @property
    def headers(self):

        return self.request.all_headers()

    @property
    def cookies(self):

        cookies = SimpleCookie()
        cookies.load(self.headers.get('cookie', ''))
        return cookies

    @property
    def harvest_user_id(self):

        cookies = self.cookies

        if config.HARVEST_USER_SS_COOKIE_NAME in cookies:
            return cookies[config.HARVEST_USER_SS_COOKIE_NAME].value

        elif config.HARVEST_USER_WEB_COOKIE_NAME in cookies:
            return cookies[config.HARVEST_USER_WEB_COOKIE_NAME].value

        elif not self.post_data_json is None and config.OLD_HARVEST_USER_ID_KEY in self.post_data_json:
            return self.post_data_json[config.OLD_HARVEST_USER_ID_KEY]

        return None

    @property
    def frame_url(self):
        return self.request.frame.url

    @property
    def method(self):
        return self.request.method

    @property
    def post_data_json(self):
        try:
            return self.request.post_data_json
        except playwright.sync_api.Error:
            return None

    def add_error(self,
                  namespace,
                  key,
                  error):

        namespace_errors = self.errors.get(namespace, {})
        namespace_errors[key] = namespace_errors.get(key, []) + [error]
        self.errors[namespace] = namespace_errors

    def validate_query_string(self,
                              validator):

        if isinstance(validator, Validator):

            validator.allow_unknown = True
            if not validator.validate(self.parsed_qs):
                self.errors['query_string'] = validator.errors

        elif isinstance(validator, dict):

            for key, value in validator.items():
                actual_value = self.parsed_qs.get(key)
                if actual_value is None:
                    self.add_error('query_string', key, f'should have value "{value}", but was missing')
                elif actual_value != value:
                    self.add_error('query_string', key, f'should have value "{value}", not "{actual_value}"')
        else:
            raise ValidatorError('Query string validator should be a dict or Validator object')

    @staticmethod
    def build_validation_rule(value):

        return {
            'type': {
                'bool': 'boolean',
                'bytes': 'binary',
                'datetime.date': 'date',
                'datetime.datetime': 'datetime',
                'float': 'float',
                'int': 'integer',
                'str': 'string'
            }[type(value).__name__],
            'allowed': [value]
        }

    def validate_body(self,
                      validator):

        if isinstance(validator, dict):

            validator = Validator({key: self.build_validation_rule(value) for key, value in validator.items()})

        if isinstance(validator, Validator):

            validator.allow_unknown = True
            if not validator.validate(self.post_data_json):
                self.errors['body'] = validator.errors

        else:
            raise ValidatorError('Body validator should be a dict or Validator object')

    def is_valid(self,
                 validators):

        self.errors = {}

        if 'query_string' in validators:

            v = validators['query_string']
            self.validate_query_string(v)

        if 'body' in validators:

            v = validators['body']
            self.validate_body(v)

        if not 'check_user_id' in validators or validators['check_user_id']:

            if self.harvest_user_id is None:
                self.add_error('general', 'harvest_user_id', 'No valid value found')

        return len(self.errors) == 0


class RequestValidator(object):

    def __init__(self,
                 selectors,
                 validators,
                 allow_multiple=False):

        self.selectors = selectors
        self.validators = validators

        self.allow_multiple = allow_multiple
        self.matched_requests = []
        self.errors = None

    def is_valid(self):

        self.errors = []

        if self.n_matched_requests == 0:
            self.errors.append({'details': 'No matched requests found'})

        for request in self.matched_requests:
            if not request.is_valid(validators=self.validators):
                self.errors.append(request.errors)

        if not self.allow_multiple and self.n_matched_requests > 1:
            self.errors.append({'details': 'multiple matching requests are not allowed'})

        return len(self.errors) == 0

    @property
    def n_matched_requests(self):
        return len(self.matched_requests)

    def select(self, requests):

        for request_ in requests:

            request = RequestWrapper(request=request_)

            if 'method' in self.selectors:
                if request.method != self.selectors['method']:
                    continue

            if 'body' in self.selectors:

                if not isinstance(request.post_data_json, dict):
                    continue

                select = True

                for key, value in self.selectors['body'].items():
                    if request.post_data_json.get(key) != value:
                        select = False
                        break

                if not select:
                    continue

            if 'url' in self.selectors:
                if not request.url.startswith(self.selectors['url']):
                    continue

            if 'frame_url' in self.selectors:
                if not request.frame_url.startswith(self.selectors['frame_url']):
                    continue

            if 'query_string' in self.selectors:
                select = True
                for key, value in self.selectors['query_string'].items():
                    if value not in request.parsed_qs.get(key, []):
                        select = False
                        break

                if not select:
                    continue

            self.matched_requests.append(request)

        return len(self.matched_requests) > 0


class EventQueue(object):

    def __init__(self,
                 url_patterns):

        self.url_patterns = url_patterns
        self.requests = []

    def register(self, request):

        if self.registration_filter(request):
            self.requests.append(request)

    def registration_filter(self, request):

        if not any(re.match(url_pattern, request.url) for url_pattern in self.url_patterns):
            return False
        return True
