##### 树莓派3的CAN总线编程

* 安装
  1. python
  2. python-dev
  3. spidev-3.2
     1. 下载spidev-3.2(或最新版本)
     2. 解压
     3. 安装,切到root用户执行 ./setup.py install
  4. 开启spi,利用raspi-config

using function.py to run tasks:
0: install spidev library

1: import all the function by: from function import *

2: first run "mpc251_init()" to prepare the SPI comunication
