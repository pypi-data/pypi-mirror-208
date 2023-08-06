# python_selenium_ctrl

Under construction! Not ready for use yet! Currently experimenting and planning!

Developed by Simon Poon from BuPA (c) 2022
Need to work with Seleium framework and pytest

# Other Code


# Procedure to publish to pypi

Reference: https://packaging.python.org/en/latest/tutorials/packaging-projects/#configuring-metadata

1. Update pyproject.toml

2. Install `build` and `twine` python package

```shell
python -m pip install build twine
```

3. Build package
```shell
python -m build
#dist folder will appear tar.gz & .whl package
```

4. Publish to pypi (Need to have pypi account)
```shell
python -m twine upload dist/*
```