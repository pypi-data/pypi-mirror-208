# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['smart_webdriver_manager']

package_data = \
{'': ['*']}

install_requires = \
['backoff>=1.11.1,<2.0.0', 'requests>=2.26.0,<3.0.0', 'tqdm>=4.65.0,<5.0.0']

extras_require = \
{'dev': ['bump2version>=1.0.1,<2.0.0'],
 'test': ['mock>=4.0.3,<5.0.0',
          'selenium>=4.1.0,<5.0.0',
          'pytest>=6.2.5,<7.0.0',
          'pytest-cov>=3.0.0,<4.0.0',
          'asserts>=0.11.1,<0.12.0']}

setup_kwargs = {
    'name': 'smart-webdriver-manager',
    'version': '0.4.0',
    'description': 'A smart webdriver and browser manager',
    'long_description': 'Smart Webdriver Manager\n=======================\n[![PyPI](https://img.shields.io/pypi/v/smart-webdriver-manager.svg)](https://pypi.org/project/smart-webdriver-manager)\n[![Supported Python Versions](https://img.shields.io/pypi/pyversions/smart-webdriver-manager.svg)](https://pypi.org/project/smart-webdriver-manager/)\n\nA smart webdriver manager. Inspired by [webdriver_manager](https://github.com/SergeyPirogov/webdriver_manager/) and [chromedriver-binary-auto](https://github.com/danielkaiser/python-chromedriver-binary).\n\nUnlike other managers, this module provides a version-synchronized context for the driver, the browser, and the data directory.\n\nThese are then cached for future use in the user-specified directory (or default).\n\nCurrently Linux and Windows are fully tested. (See TODO)\n\nExamples\n--------\n\n```python\npip install smart-webdriver-manager\n```\n\n```python\nimport os\nfrom selenium import webdriver\nfrom selenium.webdriver import ChromeOptions\nfrom selenium.webdriver.chrome.service import Service\nfrom smart_webdriver_manager import ChromeDriverManager\n\nversion = os.getenv(\'MY_ENVIRONMENTAL_VARIABLE\')\ncdm = ChromeDriverManager(version=version)\n\ndriver_path = cdm.get_driver()\nbrowser_path = cdm.get_browser()\nuser_data_path = cdm.get_browser_user_data()\n\noptions = ChromeOptions()\noptions.binary_location = browser_path\noptions.add_argument(f\'--user-data-dir={user_data_path}\')\nservice = Service(executable_path=driver_path)\ndriver = webdriver.Chrome(service=service, options=options)\ntry:\n    driver.get("http://google.com")\nfinally:\n    driver.quit()\n```\n\nWhile it is more verbose than other managers, we can run parallel tests across supported versions.\n\n```python\nfor version in [0, 75, 80, 95, 96]: # 0 -> latest\n  # ... same code as above, replacing version\n```\n\nThe compoenents themselves are modular. You can use the the driver or the browser independently.\nHowever, both the driver and browser are installed together. If you only need a driver then other modules may be better suited.\n\nWhats really nice is the work required to update tests is now minimal. Just decrement back if the tests don\'t work.\nNo need to install/uninstall browsers when verifying versions.\n\nDevelopment\n-----------\n\nThere are two ways to run local tests\n\n```python\npip install -U pip poetry tox\ngit clone https://github.com/bissli/smart-webdriver-manager.git\ncd smart-webdriver-manager\ntox\n```\n\n```python\npip install -U pip poetry\ngit clone https://github.com/bissli/smart-webdriver-manager.git\ncd smart-webdriver-manager\npoetry install\npoetry shell\npip install pytest mock selenium asserts\npytest\n```\n\nTechnical Layout\n----------------\n\nSome module definitions:\n\n- `Version`: main browser version, ie Chrome 95\n- `Release`: subversion: ie Chrome 95.01.1121\n- `Revision`: browser-only, snapshots within a release\n\nTo clarify how the module works, below is the cache directory illustrated:\n\n1. For browsers with revisions, we return the latest revision to the browser.\n2. For driver with releases, we return the latest releases to the driver corresponding to the browser.\n3. A user data directory is aligned with the release (see TODO)\n\nFor example if the user requests chromedriver v96, revision 92512 will be returned for the browser and 96.1.85.111 for the driver.\n\n```python\n"""Cache structure\nswm/\n    browsers/\n        chromium/ [linux]\n            96.1.85.54/\n                929511/\n                    chrome-linux/\n                        chrome\n                        ...\n                    929511-chrome-linux.zip\n                929512/\n                    chrome-linux/\n                        chrome\n                        ...\n                    929512-chrome-linux.zip\n            user-data/\n                ...\n        firefox/\n          ...\n    drivers/\n        chromedriver/ [windows]\n            96.1.85.54/\n                driver.zip\n                chromedriver.exe\n            96.1.85.111/\n                driver.zip\n                chromedriver.exe\n        geckodriver/ [linux]\n            0.29.8/\n                driver.zip\n                geckodriver\n            0.29.9/\n                driver.zip\n                geckodriver\n    browsers.json\n    drivers.json\n"""\n```\n\nThe default directory for the cache is as follows:\n\n- `Windows`: ~/appdata/roaming/swm\n- `Linux`:   ~/.local/share/swm\n- `Mac`:  ~/Library/Application Support/swm\n\nTODO\n----\n- [ ] Migrate off omahaproxy.appspot.com (discontinued). See https://groups.google.com/a/chromium.org/g/chromium-dev/c/uH-nFrOLWtE?pli=1 \n- [x] Change the user data directory to fall under the major version, not release (see illustration above).\n- [ ] Complete support for Mac. Parse .app directory and create workaround for Gatekeeper.\n- [x] Decide whether symlinks have value, remove code if not. (REMOVED)\n- [ ] Complete the cache clear/remove methods. Write methods to delete the data directory or parts of the cache.\n- [ ] Add Firefox as another supported platform. Current support is limited to Chromium/Chromedriver.\n- [ ] Ability to recover if part of the cache is missing (ie a browser not there but browsers.json says so) (check path exists)\n\nContributing\n------------\n\nActive contributions are welcome (collaboration). Please open a PR for features or bug fixes.\n',
    'author': 'bissli',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/bissli/smart-webdriver-manager',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
