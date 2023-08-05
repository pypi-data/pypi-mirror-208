


项目地址： https://pypi.org/project/pystools/

### 安装
```
pip install --upgrade pystools
```


本项目图像处理使用的是Pillow-SIMD

```
# must remove existed pillow first.
$ pip uninstall pillow
# install SSE4 version
$ pip install pillow-simd
# install AVX2 version
$ CC="cc -mavx2" pip install -U --force-reinstall pillow-simd
```

安装，之前需要先安装扩展库(详见： https://pillow.readthedocs.io/en/latest/installation.html#external-libraries)

```
# mac：
brew install libjpeg libtiff little-cms2 openjpeg webp

# linux
# Debian or Ubuntu:
sudo apt-get install python3-dev python3-setuptools

# Fedora:
sudo dnf install python3-devel redhat-rpm-config

# Alpine:
sudo apk add python3-dev py3-setuptools

```


