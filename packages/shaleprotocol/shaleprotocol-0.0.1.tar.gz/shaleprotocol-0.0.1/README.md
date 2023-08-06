# shaleprotocol
User-facing Python library


## Install

```
pip install shaleprotocol

> import shaleprotocol as shale
```

## For maintainer

### Dev installation

```
pip install -e .
```

### Publish

```
python3 -m pip install --upgrade build
python3 -m pip install --upgrade twine

python3 -m build
twine check dist/*
twine upload dist/*

python3 -m twine upload --repository shaleprotocol dist/*
```