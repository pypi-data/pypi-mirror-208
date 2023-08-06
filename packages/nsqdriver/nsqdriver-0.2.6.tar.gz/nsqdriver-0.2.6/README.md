# UltraMCI ()

[![Tests](https://github.com/mianyan-echo/UltraMCI/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/mianyan-echo/UltraMCI/)
***

### 环境安装
- 查看各操作帮助信息
```shell
cd UltraMCI
make help
```

- 初始化环境

```shell
sudo yum install git make
git clone https://github.com/mianyan-echo/UltraMCI.git
# 安装miniforge3 建立虚拟环境&&安装依赖库&&编译Cython
cd ./UltraMCI
sudo make install
make init
```

- 编译Cython

```shell
cd ./UltraMCI
make build
```

- 测试

```shell
cd ./UltraMCI
make test
```

****
### 项目目录介绍

- cython_lib: 需要加密与重点加速的代码
- rfskit: 控制rfs等板卡设备的基础库
- tests: 项目接口自动化测试相关文件
- ultra_mci.ini: 借助supervisor的自动启动文件，会在`sudo make install`时被拷贝到`/etc/supervisord.d/`下
****
