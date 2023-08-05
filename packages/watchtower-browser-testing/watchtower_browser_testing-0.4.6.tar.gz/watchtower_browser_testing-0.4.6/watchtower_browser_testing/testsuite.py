import os
import re
import glob
import importlib.util
import inspect
import sys
import types
import functools
import json
import datetime
import webbrowser

from playwright.sync_api import sync_playwright
from marko.ext.gfm import gfm as markdown
import jinja2
import pytz
import tzlocal

from watchtower_browser_testing.tracking_validation import EventQueue, RequestValidator, Validator
from watchtower_browser_testing import exceptions
from watchtower_browser_testing import config
from watchtower_browser_testing import helpers


class TestContext(object):

    def __init__(self):

        self.scenario_context = {}
        self.context = {}

    def get(self, key):

        return self.scenario_context.get(key) or self.context.get(key)

    def set(self, key, value, level='test'):

        assert level in ('test', 'scenario'), '`level` should be test or scenario'

        if level == 'test':
            self.context[key] = value
            self.scenario_context.pop(key, None)
        else:
            self.scenario_context[key] = value
            self.context.pop(key, None)

    def reset_scenario_context(self):

        self.scenario_context = {}

    def reset_context(self):

        self.context = {}


class TestResult(object):

    def __init__(self,
                 test_name,
                 browser,
                 measurement_plan=None,
                 scenario=None,
                 event=None,
                 ok=True,
                 errors=None,
                 data=None):

        self.test_name = test_name
        self.measurement_plan = measurement_plan
        self.scenario = scenario
        self.event = event
        self.browser = browser
        self.ok = ok
        self.errors = errors
        self.data = data

    @property
    def css_id(self):

        return 'e_' + '_'.join([str(x) for x in [
            self.measurement_plan,
            self.test_name,
            self.scenario,
            self.event
        ]])

    def as_dict(self):

        return {
            'measurement_plan': self.measurement_plan,
            'name': self.test_name,
            'scenario': self.scenario,
            'event': self.event,
            'browser': self.browser,
            'ok': self.ok,
            'errors': self.errors,
            'data': self.data
        }

    def test_report_data(self):

        return {
            'ok': self.ok,
            'browser': self.browser,
            'errors': self.errors,
            'data': self.data,
            'css_id': self.css_id
        }

def new_page_from_gtm(self, ta_page, *args, **kwargs):

    with ta_page.expect_popup() as page_info:
        ta_page.get_by_role("button", name="Reopen").click()
    return page_info.value


class TrackingTest(object):

    browsers = config.DEFAULT_BROWSERS

    pipeline_patterns = [config.DEFAULT_PIPELINE_PATTERN]

    def setUpInstance(self,
                      playwright,
                      browser,
                      gtm_web_preview_link=None,
                      tag_assistant_path=None,
                      headless=False):

        self.app = getattr(playwright, browser)

        if gtm_web_preview_link and re.match(config.GTM_WEB_PREVIEW_LINK_REGEX, gtm_web_preview_link):
            self.browser = None
            tag_assistant_path is tag_assistant_path or config.DEFAULT_PATH_TO_TAG_ASSISTANT_EXTENSION
            args = [
                f'--disable-extensions-except={tag_assistant_path}',
                f'--load-extension={tag_assistant_path}']
            if headless:
                args.append('--headless=new')
            self.context = self.app.launch_persistent_context(
                '',
                headless=False,
                args=args
            )
            self.ta_page = self.context.new_page()
            self.ta_page.goto(gtm_web_preview_link)
            with self.ta_page.expect_popup() as page_info:
                self.ta_page.get_by_role("button", name="Connect").click()
            self.page = page_info.value
            self.ta_page.get_by_role("button", name="Continue", exact=True).click()
            self.page.close()
            func = functools.partial(new_page_from_gtm, ta_page=self.ta_page)
            self.context.new_page = types.MethodType(func, self.context)

        else:
            self.browser = self.app.launch(headless=headless)
            self.context = self.browser.new_context()

        self.data_context = TestContext()

    def tearDownInstance(self):

        self.context.close()
        if self.browser:
            self.browser.close()

    def beforeEach(self):

        self.page = self.context.new_page()
        self.data_context.reset_scenario_context()

    def afterEach(self):

        self.page.close()

    def record_events(self):

        self.event_queue = EventQueue(url_patterns=self.pipeline_patterns)
        self.page.on('request', self.event_queue.register)

    def run(self,
            browser=None,
            headless=False,
            gtm_web_preview_link=None,
            tag_assistant_path=None,
            measurement_plan=None,
            report_data=None):

        if browser is None:
            browsers = self.browsers
        else:
            browsers = [browser]

        self.results = []
        report_data = report_data or {}

        for browser in browsers:

            with sync_playwright() as playwright:

                self.setUpInstance(playwright,
                                   browser,
                                   gtm_web_preview_link=gtm_web_preview_link,
                                   tag_assistant_path=tag_assistant_path,
                                   headless=headless)

                tests = [func for func in dir(self) if func.startswith(config.SCENARIO_METHOD_PREFIX)]

                for test in tests:

                    scenario = test[len(config.SCENARIO_METHOD_PREFIX):]

                    self.beforeEach()

                    getattr(self, test)()
                    validation_setup = getattr(self, config.VALIDATION_METHOD_PREFIX + scenario)()

                    for event, setup in validation_setup.items():

                        validator = RequestValidator(**setup)
                        validator.select(self.event_queue.requests)

                        if validator.is_valid():
                            self.result(browser=browser, measurement_plan=measurement_plan, scenario=scenario,
                                        event=event, ok=True,
                                        data={'n_matched_requests': validator.n_matched_requests, **report_data})
                        else:
                            self.result(browser=browser, measurement_plan=measurement_plan, scenario=scenario,
                                        event=event, ok=False,
                                        errors=validator.errors,
                                        data={'n_matched_requests': validator.n_matched_requests, **report_data})

                    self.afterEach()

                self.tearDownInstance()

    def result(self,
               browser,
               measurement_plan,
               scenario,
               event,
               ok,
               errors=None,
               data=None):

        self.results.append(
            TestResult(
                test_name=self.name,
                measurement_plan=measurement_plan,
                scenario=scenario,
                event=event,
                browser=browser,
                ok=ok,
                errors=errors,
                data=data)
        )

    @property
    def name(self):

        return self.__class__.__name__

    @classmethod
    def scen_methods(cls):

        return [x for x in dir(cls) if x.startswith(config.SCENARIO_METHOD_PREFIX)]

    @classmethod
    def md_description(cls, parent):

        test_name = cls.__name__
        test_id = parent + '_' + cls.__name__

        structure = {'name': test_name,
                     'type': 'test',
                     'id': 't_' + test_id,
                     'description': markdown.convert(helpers.trim(cls.__doc__) or ''),
                     'children': []}

        for scenario_method in cls.scen_methods():

            scenario_name = scenario_method[len(config.SCENARIO_METHOD_PREFIX):]
            scenario_id = test_id + '_' + scenario_name
            scenario_struct = {'name': scenario_name,
                               'type': 'scenario',
                               'id': 's_' + scenario_id,
                               'description': markdown.convert(
                                   helpers.trim(getattr(cls, scenario_method).__doc__) or ''),
                               'children': []}
            validation_method = config.VALIDATION_METHOD_PREFIX + scenario_method[len(config.SCENARIO_METHOD_PREFIX):]
            val = getattr(cls, validation_method)()

            for event_name, obj in val.items():

                event_id = scenario_id + '_' + event_name
                body_validator = obj['validators'].get('body')
                if body_validator and isinstance(body_validator, Validator):
                    body_validator = body_validator.schema
                json_string_body = json.dumps(dict(body_validator or {}), indent=4, cls=helpers.ExtendedEncoder)

                query_validator = obj['validators'].get('query_string')
                if query_validator and isinstance(query_validator, Validator):
                    query_validator = query_validator.schema
                json_string_query = json.dumps(dict(query_validator or {}), indent=4, cls=helpers.ExtendedEncoder)

                check_user_id = not 'check_user_id' in obj['validators'] or obj['validators']['check_user_id']
                allow_multiple = obj.get('allow_multiple', False)

                mdstring = config.VALIDATION_MD_STRING.format(event_name=event_name,
                                                              allow_multiple=allow_multiple,
                                                              check_user_id=check_user_id,
                                                              json_string_query=json_string_query,
                                                              json_string_body=json_string_body)
                event_struct = {'name': event_name,
                                'id': 'e_' + event_id,
                                'type': 'event',
                                'description': markdown.convert(mdstring)}

                scenario_struct['children'].append(event_struct)

            structure['children'].append(scenario_struct)

        return structure


class MeasurementPlan(object):

    test_modules = None
    test_directory = None
    display_name = None
    slug = None

    def __init__(self,
                 test_modules=None,
                 test_directory=None):

        self.test_modules = self.test_modules or test_modules
        self.test_directory = self.test_directory or test_directory
        self.test_results = None

    def get_tests(self):

        directory = self.test_directory or os.getcwd()

        mods = glob.glob(os.path.join(directory, '*.py'))
        test_modules = [os.path.basename(f)[:-3] for f in mods
                        if os.path.isfile(f) and os.path.basename(f).startswith(config.TEST_FILE_PREFIX)]

        if self.test_modules:

            missing = set(self.test_modules) - set(test_modules)
            if len(missing) > 0:
                raise exceptions.NotFoundError(f'Did not find test module(s): {", ".join(missing)}')

            test_modules = [tf for tf in test_modules if tf in self.test_modules]

        tests = []

        for module_name in test_modules:

            spec = importlib.util.spec_from_file_location(module_name, os.path.join(directory, module_name + '.py'))
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            for attr in module.__dir__():
                if inspect.isclass(getattr(module, attr)) and issubclass(getattr(module, attr), TrackingTest):
                    if any(x.startswith(config.SCENARIO_METHOD_PREFIX) for x in dir(getattr(module, attr))):
                        tests.append({'module': module_name, 'class': getattr(module, attr)})

        missing_validation_methods = []
        for test in tests:
            for method in dir(test['class']):
                if method.startswith(config.SCENARIO_METHOD_PREFIX):
                    scenario = method[len(config.SCENARIO_METHOD_PREFIX):]
                    if not hasattr(test['class'], config.VALIDATION_METHOD_PREFIX + scenario):
                        missing_validation_methods.append(
                            test['module'] +
                            '.' + test['class'].__name__ +
                            '.' + config.VALIDATION_METHOD_PREFIX + scenario)

        if len(missing_validation_methods) > 0:
            raise exceptions.NotFoundError(
                f'The following validation methods are missing: {", ".join(missing_validation_methods)}')

        return tests

    def run_tests(self,
                  headless=False,
                  browser=None,
                  gtm_web_preview_link=None,
                  tag_assistant_path=None):

        if not gtm_web_preview_link is None and not re.match(config.GTM_WEB_PREVIEW_LINK_REGEX, gtm_web_preview_link):
            raise exceptions.InvalidInputError(f'This does not look like a valid gtm-preview link: {gtm_web_preview_link}')

        if not gtm_web_preview_link is None and browser != 'chromium':
            raise exceptions.InvalidInputError(f'Debugging with GTM preview only works in chromium, not {browser}')

        if not gtm_web_preview_link is None:
            tag_assistant_path = tag_assistant_path or config.DEFAULT_PATH_TO_TAG_ASSISTANT_EXTENSION
            if not (os.path.isdir(tag_assistant_path)
                    and os.path.isfile(os.path.join(tag_assistant_path, 'manifest.json'))):
                raise exceptions.InvalidInputError(f'No tag assistant extension found at {tag_assistant_path}')

        tests = self.get_tests()

        results = []
        for test in tests:

            test_instance = test['class']()
            report_data = {'module': test['module']}
            test_instance.run(headless=headless,
                              browser=browser,
                              gtm_web_preview_link=gtm_web_preview_link,
                              tag_assistant_path=tag_assistant_path,
                              measurement_plan=self.__class__.__name__,
                              report_data=report_data)
            results.extend(test_instance.results)

        self.test_results = results

    def test_report_data(self,
                         timezone=None):

        if self.test_results is None:
            raise exceptions.TestError('Run tests firsts')

        if timezone is None:
            timezone = tzlocal.get_localzone()
        elif isinstance(timezone, str):
            timezone = pytz.timezone(timezone)

        time = pytz.utc.localize(datetime.datetime.utcnow()).astimezone(timezone)

        n_errors = len([r for r in self.test_results if not r.ok])

        return {
            'time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'n_errors': n_errors,
            'results': [result.test_report_data() for result in self.test_results]
        }

    def md_description(self):

        tests = self.get_tests()

        name = self.__class__.__name__
        structure = {'name': name,
                     'id': 'm_' + name,
                     'type': 'measurement_plan',
                     'description': markdown.convert(helpers.trim(self.__doc__) or ''),
                     'children': []}

        for test in tests:
            structure['children'].append(test['class'].md_description(parent=name))


        return structure

    def html_report(self,
                    title='Measurement Plan',
                    test_results=None):

        content = self.md_description()

        test_results = test_results or {}

        return self.render_html(title=title,
                                content=content,
                                test_results=test_results)

    def view_in_browser(self,
                        title='Measurement plan',
                        test_results=None,
                        temp_file_path='temp.html'):

        if not os.path.isabs(temp_file_path):
            temp_file_path = os.path.abspath(os.path.join(os.getcwd(), temp_file_path))

        html = self.html_report(title=title, test_results=test_results)
        with open(temp_file_path, 'w') as f:
            f.write(html)

        webbrowser.open('file://' + os.path.realpath(temp_file_path))



    @classmethod
    def render_html(cls,
                    title,
                    content,
                    test_results,
                    run_tests_token=None):

        jenv = jinja2.Environment(loader=jinja2.FileSystemLoader(config.TEMPLATES_PATH))
        template = jenv.get_template('measurement_plan.html')

        return template.render(title=title, content=content,
                               test_results=test_results, run_tests_token=run_tests_token)