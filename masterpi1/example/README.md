# 优化的机器人控制系统

## 项目结构

```
optimized_example/
├── README.md                 # 项目说明
├── main.py                   # 主程序入口
├── core/                     # 核心模块
│   ├── __init__.py
│   ├── robot.py             # 机器人主控制类
│   ├── state_manager.py     # 状态管理器
│   └── task_scheduler.py    # 任务调度器
├── hardware/                 # 硬件控制模块
│   ├── __init__.py
│   ├── base_controller.py   # 硬件控制基类
│   ├── motor_controller.py  # 电机控制
│   ├── arm_controller.py    # 机械臂控制
│   └── sensor_manager.py    # 传感器管理
├── vision/                   # 视觉处理模块
│   ├── __init__.py
│   ├── base_detector.py     # 检测器基类
│   ├── color_detector.py    # 颜色检测
│   ├── line_tracker.py      # 循线跟踪
│   └── object_detector.py   # 物体检测
├── tasks/                    # 任务模块
│   ├── __init__.py
│   ├── base_task.py         # 任务基类
│   ├── line_following.py    # 循线任务
│   ├── object_pickup.py     # 物体抓取任务
│   └── dance.py             # 舞蹈任务
├── utils/                    # 工具模块
│   ├── __init__.py
│   ├── config.py            # 配置管理
│   ├── logger.py            # 日志系统
│   └── thread_pool.py       # 线程池管理
└── requirements.txt          # 依赖包
```

## 设计原则

1. **单一职责原则**: 每个类只负责一个功能
2. **开放封闭原则**: 对扩展开放，对修改封闭
3. **依赖倒置原则**: 依赖抽象而非具体实现
4. **线程安全**: 使用线程池和锁机制保证并发安全
5. **状态管理**: 集中式状态管理，避免状态混乱

## 主要改进

1. **模块化设计**: 将功能拆分为独立模块
2. **抽象基类**: 定义统一接口，便于扩展
3. **线程池管理**: 避免频繁创建销毁线程
4. **状态机模式**: 清晰的状态转换逻辑
5. **配置中心化**: 统一的配置管理
6. **异常处理**: 完善的错误处理机制
7. **日志系统**: 便于调试和监控

## 使用方法

```python
from core.robot import SmartRobot
import cv2

def main():
    cap = cv2.VideoCapture(0)
    robot = SmartRobot(cap)
    
    try:
        robot.initialize()
        robot.start()
        robot.run()
    except KeyboardInterrupt:
        print("程序被用户中断")
    finally:
        robot.shutdown()
        cap.release()

if __name__ == '__main__':
    main()
```
