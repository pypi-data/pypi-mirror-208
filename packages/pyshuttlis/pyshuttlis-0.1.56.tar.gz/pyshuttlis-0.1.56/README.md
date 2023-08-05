# Shuttlis

`pyshuttlis` is a collection of utility functions that we use across our
Python apps in Shuttl. It is distributed via [PyPI](https://pypi.org/).

### Running Tests

- pip install cython
- pip install ".[test]"
- pytest

### Releasing

- `make bump_version`
- Update [the Changelog]
- Commit changes to `Changelog`, `setup.py` and `setup.cfg`.
- `make push_tag` (this'll push a tag that will trigger python package checks)
- `make release` (this will release the tag)

- You can do `make push_tag_and_release` to combine the above two steps
