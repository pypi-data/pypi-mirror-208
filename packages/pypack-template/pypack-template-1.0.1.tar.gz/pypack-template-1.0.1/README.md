# How to


## Used as a project

```bash
python -m pip install pip-tools
pip-compile --upgrade # produces and update requirements.txt
pip-sync
```

## Used as a package

```bash
python -m pip install -e . # install locally
```

## Publish as a package

```bash
python -m pip install build twine

python -m build # build sdist(tar.gz) and bdist(wheel)

twine upload dist/* # publish to pypi
```


### Reference
+ [pip-tools](https://github.com/jazzband/pip-tools/)
+ https://realpython.com/pypi-publish-python-package/
+ https://pybind11.readthedocs.io/en/stable/compiling.html