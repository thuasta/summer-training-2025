# 蜂鸣器（Buzzer）报错及其解决方案
**前两个问题GitHub仓库上已经做了相应修改，可以在[仓库](https://github.com/thuasta/thuei-1)中参考相应修改方式**
1. No module named 'yaml_handle'（文件引入路径问题）
```bash
Traceback (most recent call last):
  File "/root/thuei-1/sdk-python/HiwonderSDK/BuzzerControlDemo.py", line 2, in <module>
    import Board
  File "/root/thuei-1/sdk-python/HiwonderSDK/Board.py", line 6, in <module>
    import yaml_handle
ModuleNotFoundError: No module named 'yaml_handle'```
```
解决方法：
修改`Board.py`文件中的引入路径，将`yaml_handle`改为`yaml_handle.yaml_handle`。
把
```python
sys.path.append('/home/pi/MasterPi/')
```
改为
```python
sys.path.append('/root/thuei-1/sdk-python')
```


2. KeyError: 31
```bash
Traceback (most recent call last):
  File "/root/thuei-1/sdk-python/HiwonderSDK/BuzzerControlDemo.py", line 17, in <module>
    Board.setBuzzer(0) # 关闭
  File "/root/thuei-1/sdk-python/HiwonderSDK/Board.py", line 219, in setBuzzer
    GPIO.setup(31, GPIO.IN)
  File "/usr/local/miniconda3/lib/python3.9/site-packages/OPi/GPIO.py", line 470, in setup
    pin = get_gpio_pin(_mode, channel)
  File "/usr/local/miniconda3/lib/python3.9/site-packages/OPi/pin_mappings.py", line 80, in get_gpio_pin
    return _pin_map[mode][channel]
KeyError: 31
```
解决方法：
这是因为OPi.GPIO库的pin_mappings.py文件中没有31这个引脚的映射（库比较老，没有适配我们用的orange pi pro），所以需要手动添加引脚映射文件。
在`Board.py`文件所在的目录下新建一个`ai_pro_pin_map.py`文件，内容如下：
```python

"""
Alternative pin mappings for Orange PI Ai Pro
"""
# Orange Pi Ai Pro physical board pin to GPIO pin
_BOARD = {
    3: 76,    # SDA7
    5: 75,    # SCL7
    7: 226,   # GPIO7_02
    8: 14,    # UTXD0
    10: 15,   # URXD0
    11: 82,   # GPIO2_18
    12: 227,  # GPIO7_03
    13: 38,   # GPIO1_06
    15: 79,   # GPIO2_15
    16: 80,   # GPIO2_16
    18: 25,   # GPIO0_25
    19: 91,   # SPI0_SD0
    21: 92,   # SPI0_SDI
    22: 2,    # GPIO0_02
    23: 89,   # SPI0_CLK
    24: 90,   # SPI0_CS
    26: 83,   # GPIO2_19
    29: 231,  # URXD7
    31: 84,   # GPIO2_20
    32: 33,   # PWM3
    33: 128,  # GPIO4_00
    35: 228,  # GPIO7_04
    36: 81,   # GPIO2_17
    37: 3,    # GPIO0_03
    38: 230,  # GPIO7_06
    40: 229,  # GPIO7_05
}

# No reason for BCM mapping, keeping it for compatibility
BCM = _BOARD
```
然后在`Board.py`文件中添加引入这个文件的代码：
```python
from HiwonderSDK.ai_pro_pin_map import _BOARD
```
然后在`Board.py`文件中修改设置GPIO引脚的代码：
把
```python
GPI0.setwarnings(False)
GPI0.setmode(GPIO.BOARD)
```
改为
```python
GPI0.setwarnings(False)
GPI0.setmode(_BOARD)
```

3. Channel already configured
```bash
Traceback (most recent call last):
  File "/root/thuei-1/sdk-python/HiwonderSDK/BuzzerControlDemo.py", line 19, in <module>
    Board.setBuzzer(1) # 打开
  File "/root/thuei-1/sdk-python/HiwonderSDK/Board.py", line 219, in setBuzzer
    GPIO.setup(31, GPIO.IN)
  File "/usr/local/miniconda3/lib/python3.9/site-packages/OPi/GPIO.py", line 469, in setup
    raise RuntimeError("Channel {0} is already configured".format(channel))
RuntimeError: Channel 31 is already configured
```
解决方法： 
这是OPi.GPIO库在设置GPIO端口时的一个底层冲突，解决方法是在库文件里注释掉相关的异常抛出代码。 
文件绝对路径：`/usr/local/miniconda3/lib/python3.9/site-packages/OPi/GPIO.py`第468，469行
【如果有conda环境，就会是例如`/usr/local/miniconda3/envs/masterpi/lib/python3.9/site-packages/OPi/GPIO.py`这样的位置】
```python
if channel in  exports:
    raise RuntimeError("channel {0} is already configured".format(channel))
```
注释掉上面这两行，保存。 
注意不要修改其他代码，否则可能会导致其他问题。

