# How to generate documentation

Non-technical documentation is written in Markdown and the technical
documentation is generated from the source code via Sphinx.

But non-technical documentation is created in that way that is part of the
Sphinx documentation. Therefore for better experience, it is recommended to
generate the documentation using Sphinx.

Documentation can be generated using the following command:

```bash
cd docs && make html
```

If code was changed, it is recommended to clean the documentation before
generating it:

```bash
cd docs
sphinx-apidoc -f -o source ../src/factory_creator
sphinx-build -E -a -b html source build/html
```
