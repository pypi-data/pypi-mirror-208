# Summa Solutions Testing Framework

## 1. Build Docker image
### 1.1. Without library packaging
This way can be used for a development environment or to avoid packaging the `summa-testing-framework-summasolutions` library.

- `docker build -t summasolutions/stf[:<tag>] ./`

### 1.2. With library packaging
#### 1.2.1. Package the `summa-testing-framework-summasolutions` library.
```shell
python3 setup.py sdist bdist_wheel
python3 -m twine upload --repository pypi dist/*
```
#### 1.2.2. Build the Docker image once the library has been updated to PyPi
- `docker build -t summasolutions/stf[:<tag>] docker/`

## 2. Publish Docker image
- `docker push summasolutions/stf:<tag>`