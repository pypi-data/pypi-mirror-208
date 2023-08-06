## Simple example of creating cython package (cuda + openmp)
This code contatins c++ multithread functions(using openmp) and cuda c functions.

## Install package:

```python setup.py install```

## Compile project and upload to PyPi:

### Build project

```python3 setup.py sdist bdist_wheel```

```auditwheel repair dist/test_add_python-cp<your_python_version>-cp<your_python_version>-linux_86_64.whl```

```mv wheelhouse/* dist ```

```rm dist/*-cp<your_python_version>-cp<your_python_version>-linux_x86_64.whl```

### Upload to PyPi:
```python3 -m twine upload --repository pypi dist/*```

### Pypi example:

https://pypi.org/project/test-add-python/

Compiled for Python 3.8 and Python 3.10

## Important Notes:
auditwheel should be 2.0.0 version and wheel should be 0.31.1 version. If versions differ error occurs:

``` auditwheel: error: cannot repair "dist/test_add_python-0.1-cp310-cp310-linux_x86_64.whl" to "manylinux_2_12_x86_64" ABI because of the presence of too-recent versioned symbols. You'll need to compile the wheel on an older toolchain.```

Or something like this.