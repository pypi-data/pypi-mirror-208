# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['calcipy',
 'calcipy.check_for_stale_packages',
 'calcipy.code_tag_collector',
 'calcipy.dot_dict',
 'calcipy.experiments',
 'calcipy.md_writer',
 'calcipy.noxfile',
 'calcipy.tasks']

package_data = \
{'': ['*']}

install_requires = \
['beartype>=0.12.0', 'corallium>=0.2.1', 'invoke>=2.1.0', 'pydantic>=1.10.5']

extras_require = \
{'ddict': ['python-box>=6.0.2'],
 'doc': ['commitizen>=2.42.0',
         'mkdocs>=1.4.1',
         'mkdocs-build-plantuml-plugin>=1.7.4',
         'mkdocs-gen-files>=0.4.0',
         'mkdocs-git-revision-date-localized-plugin>=1.0.1',
         'mkdocs-literate-nav>=0.5.0',
         'mkdocs-material>=8.2.16',
         'mkdocs-section-index>=0.3.4',
         'mkdocstrings[python]>=0.21.1',
         'pandas>=1.5.3',
         'pylint>=2.16.2',
         'pymdown-extensions>=10.0.1',
         'pyyaml>=5.2',
         'transitions>=0.9.0'],
 'doc:python_version < "3.12"': ['mkdocs-include-markdown-plugin>=4.0.3'],
 'flake8': ['dlint>=0.14.0',
            'flake8>=6.0.0',
            'flake8-adjustable-complexity>=0.0.6',
            'flake8-annotations-complexity>=0.0.7',
            'flake8-executable>=2.1.3',
            'flake8-expression-complexity>=0.0.11',
            'flake8-functions>=0.0.7',
            'flake8-pep3101>=2.0.0',
            'flake8-pie>=0.16.0',
            'flake8-printf-formatting>=1.1.2',
            'flake8-raise>=0.0.5',
            'flake8-require-beartype>=0.1.1',
            'flake8-sql>=0.4.1',
            'flake8-string-format>=0.3.0',
            'flake8-super>=0.1.3',
            'flake8-tuple>=0.4.1',
            'flake8-typing-imports>=1.14.0',
            'flake8-use-pathlib>=0.3.0',
            'flake8-variables-names>=0.0.5'],
 'lint': ['autopep8>=2.0.1',
          'bandit>=1.7.4',
          'pip-check>=2.8.1',
          'ruff>=0.0.253',
          'semgrep>=1.12.1'],
 'nox': ['nox-poetry>=1.0.2'],
 'pylint': ['pylint>=2.16.2'],
 'stale': ['arrow>=1.2.3',
           'bidict>=0.22.1',
           'pyrate_limiter>=2.4',
           'requests>=2.28.1'],
 'tags': ['arrow>=1.2.3', 'pandas>=1.5.3', 'pyyaml>=5.2', 'tabulate>=0.9.0'],
 'test': ['pytest>=7.2.1',
          'pytest-cov>=4.0.0',
          'pytest-randomly>=3.12.0',
          'pytest-watcher>=0.2.6'],
 'types': ['mypy>=1.0.0']}

entry_points = \
{'console_scripts': ['calcipy = calcipy.scripts:start',
                     'calcipy_lint = calcipy.scripts:start_lint',
                     'calcipy_tags = calcipy.scripts:start_tags',
                     'calcipy_types = calcipy.scripts:start_types']}

setup_kwargs = {
    'name': 'calcipy',
    'version': '1.2.4',
    'description': 'Python package to simplify development',
    'long_description': '# calcipy\n\n![./calcipy-banner-wide.svg](https://raw.githubusercontent.com/KyleKing/calcipy/main/docs/calcipy-banner-wide.svg)\n\n`calcipy` is a Python package that implements best practices such as code style (linting, auto-fixes), documentation, CI/CD, and logging. Like the calcium carbonate in hard coral, packages can be built on the `calcipy` foundation.\n\n`calcipy` has some configurability, but is tailored for my particular use cases. If you want the same sort of functionality, there are a number of alternatives to consider:\n\n- [pyscaffold](https://github.com/pyscaffold/pyscaffold) is a much more mature project that aims for the same goals, but with a slightly different approach and tech stack (tox vs. nox, cookiecutter vs. copier, etc.)\n- [tidypy](https://github.com/jayclassless/tidypy#features), [pylama](https://github.com/klen/pylama), and [codecheck](https://pypi.org/project/codecheck/) offer similar functionality of bundling and running static checkers, but makes far fewer assumptions\n- [pytoil](https://github.com/FollowTheProcess/pytoil) is a general CLI tool for developer automation\n- And many more such as [pyta](https://github.com/pyta-uoft/pyta), [prospector](https://github.com/PyCQA/prospector), [wemake-python-styleguide](https://github.com/wemake-services/wemake-python-styleguide) / [cjolowicz/cookiecutter-hypermodern-python](https://github.com/cjolowicz/cookiecutter-hypermodern-python), [formate](https://github.com/python-formate/formate), [johnthagen/python-blueprint](https://github.com/johnthagen/python-blueprint), [oxsecurity/megalinter](https://github.com/oxsecurity/megalinter), etc.\n\n## Installation\n\nCalcipy needs a few static files managed using copier and a template project: [kyleking/calcipy_template](https://github.com/KyleKing/calcipy_template/)\n\nYou can quickly use the template to create a new project or add calcipy to an existing one:\n\n```sh\n# Install copier. pipx is recommended\npipx install copier\n\n# To create a new project\ncopier copy gh:KyleKing/calcipy_template new_project\ncd new_project\n\n# Or convert/update an existing one\ncd my_project\ncopier copy gh:KyleKing/calcipy_template .\ncopier update\n```\n\nSee [./Advanced_Configuration.md](./Advanced_Configuration.md) for documentation on the configurable aspects of `calcipy`\n\n### Calcipy CLI\n\nAdditionally, `calcipy` can be run as a CLI application without adding the package as a dependency.\n\nQuick Start:\n\n```sh\npipx install calcipy\n\n# Use \'tags\' to create a CODE_TAG_SUMMARY of the specified directory\ncalcipy tags --help\ncalcipy tags --base-dir=~/path/to/my_project\n\n# See additional documentation from the CLI help\n> calcipy\n\nSubcommands:\n\nmain                                     Main task pipeline.\nother                                    Run tasks that are otherwise not exercised in main.\nrelease                                  Release pipeline.\ncl.bump                                  Bumps project version based on commits & settings in pyproject.toml.\ncl.write                                 Write a Changelog file with the raw Git history.\ndoc.build                                Build documentation with mkdocs.\ndoc.deploy                               Deploy docs to the Github `gh-pages` branch.\ndoc.watch                                Serve local documentation for local editing.\nlint.autopep8                            Run autopep8.\nlint.check (lint)                        Run ruff as check-only.\nlint.fix                                 Run ruff and apply fixes.\nlint.flake8                              Run ruff and apply fixes.\nlint.pre-commit                          Run pre-commit.\nlint.pylint                              Run ruff and apply fixes.\nlint.security                            Attempt to identify possible security vulnerabilities.\nlint.watch                               Run ruff as check-only.\nnox.noxfile (nox)                        Run nox from the local noxfile.\npack.check-licenses                      Check licenses for compatibility with `licensecheck`.\npack.lock                                Ensure poetry.lock is  up-to-date.\npack.publish                             Build the distributed format(s) and publish.\nstale.check-for-stale-packages (stale)   Identify stale dependencies.\ntags.collect-code-tags (tags)            Create a `CODE_TAG_SUMMARY.md` with a table for TODO- and FIXME-style code comments.\ntest.coverage                            Generate useful coverage outputs after running pytest.\ntest.pytest (test)                       Run pytest with default arguments.\ntest.step                                Run pytest optimized to stop on first error.\ntest.watch                               Run pytest with polling and optimized to stop on first error.\ntypes.mypy                               Run mypy.\ntypes.pyright                            Run pyright.\n\nGlobal Task Options:\n\nworking_dir   Set the cwd for the program. Example: "../run --working-dir .. lint test"\n*file_args    List of Paths available globally to all tasks. Will resolve paths with working_dir\nverbose       Globally configure logger verbosity (-vvv for most verbose)\n```\n\n### Calcipy Pre-Commit\n\n`calcipy` can also be used as a `pre-commit` task by adding the below snippet to your `pre-commit` file:\n\n```yaml\nrepos:\n  - repo: https://github.com/KyleKing/calcipy\n    rev: main\n    hooks:\n      - id: tags\n      - id: lint-fix\n      - id: types\n```\n\n## Project Status\n\nSee the `Open Issues` and/or the [CODE_TAG_SUMMARY]. For release history, see the [CHANGELOG].\n\n## Contributing\n\nWe welcome pull requests! For your pull request to be accepted smoothly, we suggest that you first open a GitHub issue to discuss your idea. For resources on getting started with the code base, see the below documentation:\n\n- [DEVELOPER_GUIDE]\n- [STYLE_GUIDE]\n\n## Code of Conduct\n\nWe follow the [Contributor Covenant Code of Conduct][contributor-covenant].\n\n### Open Source Status\n\nWe try to reasonably meet most aspects of the "OpenSSF scorecard" from [Open Source Insights](https://deps.dev/pypi/calcipy)\n\n## Responsible Disclosure\n\nIf you have any security issue to report, please contact the project maintainers privately. You can reach us at [dev.act.kyle@gmail.com](mailto:dev.act.kyle@gmail.com).\n\n## License\n\n[LICENSE]\n\n[changelog]: https://calcipy.kyleking.me/docs/CHANGELOG\n[code_tag_summary]: https://calcipy.kyleking.me/docs/CODE_TAG_SUMMARY\n[contributor-covenant]: https://www.contributor-covenant.org\n[developer_guide]: https://calcipy.kyleking.me/docs/DEVELOPER_GUIDE\n[license]: https://github.com/kyleking/calcipy/blob/main/LICENSE\n[style_guide]: https://calcipy.kyleking.me/docs/STYLE_GUIDE\n',
    'author': 'Kyle King',
    'author_email': 'dev.act.kyle@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyleking/calcipy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8.12,<4.0.0',
}


setup(**setup_kwargs)
