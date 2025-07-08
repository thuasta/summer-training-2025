#!/usr/bin/python3
# coding=utf8
"""
优化的电机控制器
使用线程安全和状态管理
"""
import time
import threading
from typing import Dict, Any, Optional, Tuple
from hardware.base_controller import HardwareController
from utils.config import get_config

class MotorController(HardwareController):
    """电机控制器"""
    
    def __init__(self):
        super().__init__("MotorController")
        self.config = get_config().motor
        
        # 电机状态
        self.motor_speeds = {1: 0, 2: 0, 3: 0, 4: 0}  # 四个电机的速度
        self.target_speeds = {1: 0, 2: 0, 3: 0, 4: 0}  # 目标速度
        
        # PID控制器状态
        self.pid_enabled = True
        self.last_error = 0.0
        self.integral = 0.0
        self.last_time = time.time()
        
        # 安全限制
        self.max_speed = self.config.max_speed
        self.min_speed = -self.config.max_speed
        
        # 控制线程
        self.control_thread: Optional[threading.Thread] = None
        self.control_running = False
    
    def initialize(self) -> bool:
        """初始化电机控制器"""
        try:
            self.logger.info("初始化电机控制器...")
            
            # 初始化电机（这里应该调用实际的硬件初始化代码）
            # 例如：Board.setMotor(1, 0) 等
            
            # 停止所有电机
            self.stop_all_motors()
            
            # 启动控制线程
            self._start_control_thread()
            
            self.is_initialized = True
            self.is_enabled = True
            
            self.logger.info("电机控制器初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"电机控制器初始化失败: {e}")
            return False
    
    def shutdown(self):
        """关闭电机控制器"""
        self.logger.info("关闭电机控制器...")
        
        # 停止控制线程
        self._stop_control_thread()
        
        # 停止所有电机
        self.stop_all_motors()
        
        self.is_enabled = False
        self.logger.info("电机控制器已关闭")
    
    def enable(self):
        """启用电机控制器"""
        with self.lock:
            if not self.is_initialized:
                raise RuntimeError("电机控制器未初始化")
            
            self.is_enabled = True
            self.logger.info("电机控制器已启用")
    
    def disable(self):
        """禁用电机控制器"""
        with self.lock:
            self.stop_all_motors()
            self.is_enabled = False
            self.logger.info("电机控制器已禁用")
    
    def set_motor_speed(self, motor_id: int, speed: int):
        """
        设置单个电机速度
        
        Args:
            motor_id: 电机ID (1-4)
            speed: 速度 (-100 到 100)
        """
        if not self.is_ready():
            self.logger.warning("电机控制器未就绪，忽略速度设置")
            return
        
        # 限制速度范围
        speed = max(self.min_speed, min(self.max_speed, speed))
        
        with self.lock:
            self.target_speeds[motor_id] = speed
            self.logger.debug(f"设置电机 {motor_id} 目标速度: {speed}")
    
    def set_all_motor_speeds(self, speeds: Dict[int, int]):
        """
        设置所有电机速度
        
        Args:
            speeds: 电机速度字典 {motor_id: speed}
        """
        for motor_id, speed in speeds.items():
            self.set_motor_speed(motor_id, speed)
    
    def stop_all_motors(self):
        """停止所有电机"""
        with self.lock:
            for motor_id in range(1, 5):
                self.target_speeds[motor_id] = 0
                self.motor_speeds[motor_id] = 0
                # 这里应该调用实际的硬件停止命令
                # 例如：Board.setMotor(motor_id, 0)
        
        self.logger.info("所有电机已停止")
    
    def move_forward(self, speed: int = None):
        """
        向前移动
        
        Args:
            speed: 移动速度（默认使用配置中的基础速度）
        """
        speed = speed or self.config.base_speed
        self.set_all_motor_speeds({1: speed, 2: speed, 3: speed, 4: speed})
        self.logger.debug(f"向前移动，速度: {speed}")
    
    def move_backward(self, speed: int = None):
        """
        向后移动
        
        Args:
            speed: 移动速度
        """
        speed = speed or self.config.base_speed
        self.set_all_motor_speeds({1: -speed, 2: -speed, 3: -speed, 4: -speed})
        self.logger.debug(f"向后移动，速度: {speed}")
    
    def turn_left(self, speed: int = None):
        """
        左转
        
        Args:
            speed: 转向速度
        """
        speed = speed or self.config.base_speed
        self.set_all_motor_speeds({1: -speed, 2: speed, 3: -speed, 4: speed})
        self.logger.debug(f"左转，速度: {speed}")
    
    def turn_right(self, speed: int = None):
        """
        右转
        
        Args:
            speed: 转向速度
        """
        speed = speed or self.config.base_speed
        self.set_all_motor_speeds({1: speed, 2: -speed, 3: speed, 4: -speed})
        self.logger.debug(f"右转，速度: {speed}")
    
    def move_sideways_left(self, speed: int = None):
        """
        左平移（麦轮特有）
        
        Args:
            speed: 移动速度
        """
        speed = speed or self.config.base_speed
        self.set_all_motor_speeds({1: -speed, 2: speed, 3: speed, 4: -speed})
        self.logger.debug(f"左平移，速度: {speed}")
    
    def move_sideways_right(self, speed: int = None):
        """
        右平移（麦轮特有）
        
        Args:
            speed: 移动速度
        """
        speed = speed or self.config.base_speed
        self.set_all_motor_speeds({1: speed, 2: -speed, 3: -speed, 4: speed})
        self.logger.debug(f"右平移，速度: {speed}")
    
    def rotate_clockwise(self, speed: int = None):
        """
        顺时针旋转
        
        Args:
            speed: 旋转速度
        """
        speed = speed or self.config.base_speed
        self.set_all_motor_speeds({1: speed, 2: -speed, 3: speed, 4: -speed})
        self.logger.debug(f"顺时针旋转，速度: {speed}")
    
    def rotate_counterclockwise(self, speed: int = None):
        """
        逆时针旋转
        
        Args:
            speed: 旋转速度
        """
        speed = speed or self.config.base_speed
        self.set_all_motor_speeds({1: -speed, 2: speed, 3: -speed, 4: speed})
        self.logger.debug(f"逆时针旋转，速度: {speed}")
    
    def move_with_pid(self, error: float) -> Tuple[int, int]:
        """
        使用PID控制器计算电机速度
        
        Args:
            error: 误差值（例如线偏移量）
            
        Returns:
            Tuple[int, int]: 左右电机速度
        """
        if not self.pid_enabled:
            return self.config.base_speed, self.config.base_speed
        
        current_time = time.time()
        dt = current_time - self.last_time
        
        if dt <= 0:
            dt = 0.01  # 避免除零
        
        # PID计算
        proportional = error
        self.integral += error * dt
        derivative = (error - self.last_error) / dt
        
        # PID输出
        output = (self.config.pid_p * proportional + 
                 self.config.pid_i * self.integral + 
                 self.config.pid_d * derivative)
        
        # 计算左右电机速度
        base_speed = self.config.base_speed
        left_speed = int(base_speed - output)
        right_speed = int(base_speed + output)
        
        # 限制速度范围
        left_speed = max(self.min_speed, min(self.max_speed, left_speed))
        right_speed = max(self.min_speed, min(self.max_speed, right_speed))
        
        # 更新状态
        self.last_error = error
        self.last_time = current_time
        
        return left_speed, right_speed
    
    def reset_pid(self):
        """重置PID控制器"""
        with self.lock:
            self.last_error = 0.0
            self.integral = 0.0
            self.last_time = time.time()
        
        self.logger.debug("PID控制器已重置")
    
    def get_status(self) -> Dict[str, Any]:
        """获取电机控制器状态"""
        with self.lock:
            return {
                'initialized': self.is_initialized,
                'enabled': self.is_enabled,
                'motor_speeds': dict(self.motor_speeds),
                'target_speeds': dict(self.target_speeds),
                'pid_enabled': self.pid_enabled,
                'last_error': self.last_error,
                'integral': self.integral
            }
    
    def _start_control_thread(self):
        """启动控制线程"""
        if self.control_thread and self.control_thread.is_alive():
            return
        
        self.control_running = True
        self.control_thread = threading.Thread(
            target=self._control_loop,
            name="MotorControl",
            daemon=True
        )
        self.control_thread.start()
        self.logger.debug("电机控制线程已启动")
    
    def _stop_control_thread(self):
        """停止控制线程"""
        self.control_running = False
        
        if self.control_thread and self.control_thread.is_alive():
            self.control_thread.join(timeout=1.0)
        
        self.logger.debug("电机控制线程已停止")
    
    def _control_loop(self):
        """控制循环"""
        while self.control_running:
            try:
                with self.lock:
                    if not self.is_enabled:
                        time.sleep(0.1)
                        continue
                    
                    # 平滑过渡到目标速度
                    for motor_id in range(1, 5):
                        current = self.motor_speeds[motor_id]
                        target = self.target_speeds[motor_id]
                        
                        if current != target:
                            # 简单的平滑过渡
                            diff = target - current
                            step = max(1, abs(diff) // 5)  # 分5步到达目标
                            
                            if diff > 0:
                                new_speed = min(target, current + step)
                            else:
                                new_speed = max(target, current - step)
                            
                            self.motor_speeds[motor_id] = new_speed
                            
                            # 这里应该调用实际的硬件设置命令
                            # 例如：Board.setMotor(motor_id, new_speed)
                
                time.sleep(0.02)  # 50Hz控制频率
                
            except Exception as e:
                self.logger.error(f"电机控制循环错误: {e}")
                time.sleep(0.1)
