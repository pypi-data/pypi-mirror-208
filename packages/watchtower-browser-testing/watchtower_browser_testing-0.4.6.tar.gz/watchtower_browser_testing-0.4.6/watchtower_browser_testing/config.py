import os

PACKAGE_PATH = os.path.dirname(os.path.realpath(__file__))
TEMPLATES_PATH = os.path.join(PACKAGE_PATH, 'templates')

TEST_FILE_PREFIX = 'tests_'
DEFAULT_PIPELINE_PATTERN = 'https?://pipeline[.].*'
SCENARIO_METHOD_PREFIX = 'scenario_'
VALIDATION_METHOD_PREFIX = 'validation_'
DEFAULT_TEST_DESCRIPTION = ''
DEFAULT_BROWSERS = ['chromium', 'firefox', 'webkit']
HARVEST_USER_SS_COOKIE_NAME = '_harvest_ss_user'
HARVEST_USER_WEB_COOKIE_NAME = '_harvest_web_user'
OLD_HARVEST_USER_ID_KEY = 'oldHarvestUserId'
GTM_WEB_PREVIEW_LINK_REGEX = r'^https://tagassistant[.]google[.]com/.*'
DEFAULT_PATH_TO_TAG_ASSISTANT_EXTENSION = r'tag_assistant'

VALIDATION_MD_STRING = '''<details>
<summary>{event_name} validation (click to see details)</summary>

```
allow_multiple: {allow_multiple}

check_user_id: {check_user_id}

query_params_validator: {json_string_query}

body_validator: {json_string_body}
```
</details>'''