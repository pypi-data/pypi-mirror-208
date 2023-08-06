# plib Package

This is a simple platform library.

## Build

From the root of repository:

```bash
pip install --upgrade pip setuptools wheel twine build
python -m build
```

## Installing

### Local (for developers)

```bash
pip install platform-library==<version> --find-links /path/to/platform-library/dist
```

### CI/CD

```bash
pip install git+http://gitlab-ci-token:${CI_JOB_TOKEN}@tox.3divi.ru/platform/server/platform-library.git@<tag_or_branch>
```

### Upload to PyPi

```bash
python -m twine upload dist/* 
```
