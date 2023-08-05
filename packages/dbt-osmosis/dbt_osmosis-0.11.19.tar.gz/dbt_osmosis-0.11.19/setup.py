# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dbt_osmosis',
 'dbt_osmosis.components',
 'dbt_osmosis.core',
 'dbt_osmosis.vendored',
 'dbt_osmosis.vendored.dbt_core_interface']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>3,<4',
 'click>7',
 'dbt-core>=1',
 'orjson>3,<4',
 'pydantic<2',
 'rich>=10',
 'ruamel.yaml>=0.17']

extras_require = \
{'duckdb': ['dbt-duckdb>=1.0.0'],
 'postgres': ['dbt-postgres>=1.0.0'],
 'sqlite': ['dbt-sqlite>=1.0.0'],
 'workbench': ['streamlit==1.20.0',
               'streamlit-ace>=0.1.0',
               'ydata-profiling>=3.6.0',
               'feedparser>=6.0.10,<7.0.0',
               'streamlit-elements-fluence>=0.1.4']}

entry_points = \
{'console_scripts': ['dbt-osmosis = dbt_osmosis.main:cli']}

setup_kwargs = {
    'name': 'dbt-osmosis',
    'version': '0.11.19',
    'description': 'A dbt server and suite of optional developer tools to make developing with dbt delightful.',
    'long_description': '# dbt-osmosis\n\n<!--![GitHub Actions](https://github.com/z3z1ma/dbt-osmosis/actions/workflows/master.yml/badge.svg)-->\n\n![PyPI](https://img.shields.io/pypi/v/dbt-osmosis)\n![Downloads](https://pepy.tech/badge/dbt-osmosis)\n![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-green.svg)\n![black](https://img.shields.io/badge/code%20style-black-000000.svg)\n[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://z3z1ma-dbt-osmosis-srcdbt-osmosisapp-v2-i0ico9.streamlit.app/)\n\n\n[![Scc Count Badge](https://sloc.xyz/github/z3z1ma/dbt-osmosis/)](https://github.com/z3z1ma/dbt-osmosis/)\n[![Scc Count Badge](https://sloc.xyz/github/z3z1ma/dbt-osmosis/?category=cocomo)](https://github.com/z3z1ma/dbt-osmosis/)\n\n## New to dbt-osmosis?\n\nWe now have a spiffy [dbt-osmosis documentation site](https://z3z1ma.github.io/dbt-osmosis/)! 🎉\n\nPlease check it out for a more in-depth introduction to dbt-osmosis. 👇\n\n[![dbt-osmosis](/screenshots/docs_site.png)](https://z3z1ma.github.io/dbt-osmosis/)\n\n## What is dbt-osmosis?\n\nHello and welcome to the project! [dbt-osmosis](https://github.com/z3z1ma/dbt-osmosis) 🌊 serves to enhance the developer experience significantly. We do this through providing 4 core features:\n\n1. Automated schema YAML management.\n    \n    1a. `dbt-osmosis yaml refactor --project-dir ... --profiles-dir ...`\n\n    > Automatically generate documentation based on upstream documented columns, organize yaml files based on configurable rules defined in dbt_project.yml, scaffold new yaml files based on the same rules, inject columns from data warehouse schema if missing in yaml and remove columns no longer present in data warehouse (organize -> document)\n\n    1b. `dbt-osmosis yaml organize --project-dir ... --profiles-dir ...`\n\n    > Organize yaml files based on configurable rules defined in dbt_project.yml, scaffold new yaml files based on the same rules\n\n    1c. `dbt-osmosis yaml document --project-dir ... --profiles-dir ...`\n\n    > Automatically generate documentation based on upstream documented columns\n\n2. A highly performant dbt server which integrates with tools such as dbt-power-user for VS Code to enable interactive querying + realtime compilation from your IDE\n\n    2a. `dbt-osmosis server serve --project-dir ... --profiles-dir ...`\n\n    > Spins up a WSGI server. Can be passed --register-project to automatically register your local project\n\n3. Workbench for dbt Jinja SQL. This workbench is powered by streamlit and the badge at the top of the readme will take you to a demo on streamlit cloud with jaffle_shop loaded (requires extra `pip install dbt-osmosis[workbench]`). \n\n    3a. `dbt-osmosis workbench --project-dir ... --profiles-dir ...`\n\n    > Spins up a streamlit app. This workbench offers similar functionality to the osmosis server + power-user combo without a reliance on VS code. Realtime compilation, query execution, pandas profiling all via copying and pasting whatever you are working on into the workbenchat your leisure. Spin it up and down as needed.\n\n4. Diffs for data model outputs to model outputs across git revisions (🚧 this is in development)\n\n    4a. `dbt-osmosis diff -m some_model  --project-dir ... --profiles-dir ...`\n\n    > Run diffs on models dynamically. This pulls the state of the model before changes from your git history, injects it as a node to the dbt manifest, compiles the old and modified nodes, and diffs their query results optionally writing nodes to temp tables before running the diff query for warehouses with performance or query complexity limits (👀 bigquery)\n\n____\n\n## Pre-commit\n\nYou can use dbt-osmosis as a pre-commit hook. This will run the `dbt-osmosis yaml refactor` command on your models directory before each commit. This is one way to ensure that your schema.yml files are always up to date. I would recommend reading the docs for more information on what this command does.\n\n```yaml title=".pre-commit-config.yaml"\nrepos:\n  - repo: https://github.com/z3z1ma/dbt-osmosis\n    rev: v0.11.11 # verify the latest version\n    hooks:\n      - id: dbt-osmosis\n        files: ^models/\n        # you\'d normally run this against your prod target, you can use any target though\n        args: [--target=prod]\n        additional_dependencies: [dbt-<adapter>]\n```\n\n___\n\n## Workbench\n\nThe workbench is a streamlit app that allows you to work on dbt models in a side-by-side editor and query tester. I\'ve kept this portion of the README since users can jump into the streamlit hosted workbench to play around with it via the badge below. Expect the living documentation moving forward to exist at the [dbt-osmosis documentation site](https://z3z1ma.github.io/dbt-osmosis/).\n\nI also expect there is some untapped value in the workbench that is only pending some time from myself. I\'ve seen a path to a truly novel development experience and look forward to exploring it.\n\nDemo the workbench 👇 \n\n[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://z3z1ma-dbt-osmosis-srcdbt-osmosisapp-v2-i0ico9.streamlit.app/)\n\n \n```sh\n# NOTE this requires the workbench extra as you can see\npip install dbt-osmosis[workbench]\n\n# Command to start server\ndbt-osmosis workbench\n```\n\nPress "r" to reload the workbench at any time.\n\n\n✔️ dbt Editor with instant dbt compilation side-by-side or pivoted\n\n✔️ Full control over model and workbench theme, light and dark mode\n\n✔️ Query Tester, test the model you are working on for instant feedback\n\n✔️ Data Profiler (leverages pandas-profiling)\n\n\n**Editor** \n\nThe editor is able to compile models with control+enter or dynamically as you type. Its speedy! You can choose any target defined in your profiles yml for compilation and execution.\n\n![editor](/screenshots/osmosis_editor_main.png?raw=true "dbt-osmosis Workbench")\n\nYou can pivot the editor for a fuller view while workbenching some dbt SQL.\n\n![pivot](/screenshots/osmosis_editor_pivot.png?raw=true "dbt-osmosis Pivot Layout")\n\n\n**Test Query**\n\nTest dbt models as you work against whatever profile you have selected and inspect the results. This allows very fast iterative feedback loops not possible with VS Code alone.\n\n![test-model](/screenshots/osmosis_tester.png?raw=true "dbt-osmosis Test Model")\n\n**Profile Model Results**\n\nProfile your datasets on the fly while you develop without switching context. Allows for more refined interactive data modelling when dataset fits in memory.\n\n![profile-data](/screenshots/osmosis_profile.png?raw=true "dbt-osmosis Profile Data")\n\n\n**Useful Links and RSS Feed**\n\nSome useful links and RSS feeds at the bottom. 🤓\n\n![profile-data](/screenshots/osmosis_links.png?raw=true "dbt-osmosis Profile Data")\n\n\n___\n\n![graph](https://repobeats.axiom.co/api/embed/df37714aa5780fc79871c60e6fc623f8f8e45c35.svg "Repobeats analytics image")\n',
    'author': 'z3z1ma',
    'author_email': 'butler.alex2010@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/z3z1ma/dbt-osmosis',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8, !=2.7.*, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.*, !=3.7.*',
}


setup(**setup_kwargs)
