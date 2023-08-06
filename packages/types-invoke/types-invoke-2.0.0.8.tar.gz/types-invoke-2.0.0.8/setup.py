from setuptools import setup

name = "types-invoke"
description = "Typing stubs for invoke"
long_description = '''
## Typing stubs for invoke

This is a PEP 561 type stub package for the `invoke` package. It
can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
PyCharm, etc. to check code that uses
`invoke`. The source for this package can be found at
https://github.com/python/typeshed/tree/main/stubs/invoke. All fixes for
types and metadata should be contributed there.

*Note:* The `invoke` package includes type annotations or type stubs
since version 2.1.2. Please uninstall the `types-invoke`
package if you use this or a newer version.


See https://github.com/python/typeshed/blob/main/README.md for more details.
This package was generated from typeshed commit `f143f47b111b4a26ccc29c05b866dbb246987d6e`.
'''.lstrip()

setup(name=name,
      version="2.0.0.8",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/invoke.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['invoke-stubs'],
      package_data={'invoke-stubs': ['__init__.pyi', 'collection.pyi', 'completion/__init__.pyi', 'completion/complete.pyi', 'config.pyi', 'context.pyi', 'env.pyi', 'exceptions.pyi', 'executor.pyi', 'loader.pyi', 'main.pyi', 'parser/__init__.pyi', 'parser/argument.pyi', 'parser/context.pyi', 'parser/parser.pyi', 'program.pyi', 'runners.pyi', 'tasks.pyi', 'terminals.pyi', 'util.pyi', 'watchers.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
