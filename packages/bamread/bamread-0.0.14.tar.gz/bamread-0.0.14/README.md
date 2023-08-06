# bamread

Read bam files quickly into dataframes in Python

## Development

### Development

See [How to Publish an Open-Source Python Package to PyPI](https://realpython.com/pypi-publish-python-package/)

Install

```bash
pip install .
```

Create sdist and wheel (requires [build](https://pypa-build.readthedocs.io/en/stable/))

```bash
python -m build
```

Check whether the package archives look fine:

```bash
twine check dist/*
```

Upload to PyPI test server

```bash
twine upload -r testpypi dist/*
```