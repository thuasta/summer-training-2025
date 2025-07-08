#!/usr/bin/python3
# coding=utf8
"""
优化的机械臂控制器
使用线程安全和位置管理
"""
import time
import threading
from typing import Dict, Any, Optional, Tuple, List
from hardware.base_controller import HardwareController
from utils.config import get_config

class Position:
    """位置类"""
    def __init__(self, x: float, y: float, z: float, pitch: float = 0, yaw: float = 0, roll: float = 0):
        self.x = x
        self.y = y
        self.z = z
        self.pitch = pitch
        self.yaw = yaw
        self.roll = roll
    
    def __str__(self):
        return f"Position(x={self.x}, y={self.y}, z={self.z}, pitch={self.pitch}, yaw={self.yaw}, roll={self.roll})"
    
    def to_tuple(self) -> Tuple[float, ...]:
        return (self.x, self.y, self.z, self.pitch, self.yaw, self.roll)

class ArmController(HardwareController):
    """机械臂控制器"""
    
    def __init__(self):
        super().__init__("ArmController")
        self.config = get_config().arm
        
        # 位置状态
        self.current_position = Position(0, 0, 0)
        self.target_position = Position(0, 0, 0)
        self.home_position = Position(*self.config.default_position)
        
        # 夹持器状态
        self.gripper_angle = self.config.release_servo_angle
        self.gripper_target_angle = self.config.release_servo_angle
        self.is_gripping = False
        
        # 运动状态
        self.is_moving = False
        self.movement_speed = 1000  # 默认运动速度
        
        # 预定义位置
        self.predefined_positions = {
            'home': Position(*self.config.default_position),
            'pickup': Position(15, 0, 5),
            'drop_red': Position(*self.config.servo_positions.get('red', (-12, 12, 2))),
            'drop_green': Position(*self.config.servo_positions.get('green', (0, 8, 10))),
            'drop_blue': Position(*self.config.servo_positions.get('blue', (-12, 20, 2))),
        }
        
        # 控制线程
        self.control_thread: Optional[threading.Thread] = None
        self.control_running = False
    
    def initialize(self) -> bool:
        """初始化机械臂控制器"""
        try:
            self.logger.info("初始化机械臂控制器...")
            
            # 初始化夹持器
            self._set_gripper_hardware(self.config.release_servo_angle)
            
            # 移动到默认位置
            self.move_to_home()
            
            # 启动控制线程
            self._start_control_thread()
            
            self.is_initialized = True
            self.is_enabled = True
            
            self.logger.info("机械臂控制器初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"机械臂控制器初始化失败: {e}")
            return False
    
    def shutdown(self):
        """关闭机械臂控制器"""
        self.logger.info("关闭机械臂控制器...")
        
        # 停止控制线程
        self._stop_control_thread()
        
        # 释放夹持器
        self.release_gripper()
        
        # 移动到默认位置
        self.move_to_home()
        
        self.is_enabled = False
        self.logger.info("机械臂控制器已关闭")
    
    def enable(self):
        """启用机械臂控制器"""
        with self.lock:
            if not self.is_initialized:
                raise RuntimeError("机械臂控制器未初始化")
            
            self.is_enabled = True
            self.logger.info("机械臂控制器已启用")
    
    def disable(self):
        """禁用机械臂控制器"""
        with self.lock:
            self.is_enabled = False
            self.logger.info("机械臂控制器已禁用")
    
    def move_to_position(self, position: Position, speed: int = None, wait: bool = True) -> bool:
        """
        移动到指定位置
        
        Args:
            position: 目标位置
            speed: 运动速度
            wait: 是否等待运动完成
            
        Returns:
            bool: 是否成功开始运动
        """
        if not self.is_ready():
            self.logger.warning("机械臂控制器未就绪，忽略移动命令")
            return False
        
        speed = speed or self.movement_speed
        
        with self.lock:
            self.target_position = position
            self.movement_speed = speed
            self.is_moving = True
        
        self.logger.info(f"移动到位置: {position}")
        
        # 这里应该调用实际的硬件移动命令
        # 例如：AK.setPitchRangeMoving((x, y, z), pitch, yaw, roll, speed)
        
        if wait:
            return self.wait_for_movement_complete()
        
        return True
    
    def move_to_predefined_position(self, position_name: str, speed: int = None, wait: bool = True) -> bool:
        """
        移动到预定义位置
        
        Args:
            position_name: 预定义位置名称
            speed: 运动速度
            wait: 是否等待运动完成
            
        Returns:
            bool: 是否成功移动
        """
        if position_name not in self.predefined_positions:
            self.logger.error(f"未知的预定义位置: {position_name}")
            return False
        
        position = self.predefined_positions[position_name]
        return self.move_to_position(position, speed, wait)
    
    def move_to_home(self, wait: bool = True) -> bool:
        """
        移动到默认位置
        
        Args:
            wait: 是否等待运动完成
            
        Returns:
            bool: 是否成功移动
        """
        return self.move_to_predefined_position('home', wait=wait)
    
    def grab_object(self, position: Position = None, approach_height: float = 5.0) -> bool:
        """
        抓取物体
        
        Args:
            position: 物体位置（如果为None，使用当前位置）
            approach_height: 接近高度
            
        Returns:
            bool: 是否成功抓取
        """
        if not self.is_ready():
            self.logger.warning("机械臂控制器未就绪，无法抓取")
            return False
        
        try:
            self.logger.info("开始抓取物体")
            
            if position:
                # 先移动到接近位置（高一些）
                approach_pos = Position(position.x, position.y, position.z + approach_height, 
                                      position.pitch, position.yaw, position.roll)
                self.move_to_position(approach_pos, wait=True)
                
                # 降低到目标位置
                self.move_to_position(position, wait=True)
            
            # 夹取物体
            self.grip_object()
            
            # 稍微抬起
            if position:
                lift_pos = Position(position.x, position.y, position.z + approach_height/2, 
                                  position.pitch, position.yaw, position.roll)
                self.move_to_position(lift_pos, wait=True)
            
            self.logger.info("物体抓取完成")
            return True
            
        except Exception as e:
            self.logger.error(f"抓取物体失败: {e}")
            return False
    
    def place_object(self, position: Position, approach_height: float = 5.0) -> bool:
        """
        放置物体
        
        Args:
            position: 放置位置
            approach_height: 接近高度
            
        Returns:
            bool: 是否成功放置
        """
        if not self.is_ready():
            self.logger.warning("机械臂控制器未就绪，无法放置")
            return False
        
        try:
            self.logger.info("开始放置物体")
            
            # 移动到接近位置
            approach_pos = Position(position.x, position.y, position.z + approach_height, 
                                  position.pitch, position.yaw, position.roll)
            self.move_to_position(approach_pos, wait=True)
            
            # 降低到放置位置
            self.move_to_position(position, wait=True)
            
            # 释放物体
            self.release_gripper()
            
            # 抬起
            self.move_to_position(approach_pos, wait=True)
            
            self.logger.info("物体放置完成")
            return True
            
        except Exception as e:
            self.logger.error(f"放置物体失败: {e}")
            return False
    
    def grip_object(self, force: int = None):
        """
        夹取物体
        
        Args:
            force: 夹取力度（角度）
        """
        angle = force or self.config.grab_servo_angle
        self.set_gripper_angle(angle)
        self.is_gripping = True
        self.logger.debug(f"夹取物体，角度: {angle}")
    
    def release_gripper(self):
        """释放夹持器"""
        self.set_gripper_angle(self.config.release_servo_angle)
        self.is_gripping = False
        self.logger.debug("释放夹持器")
    
    def set_gripper_angle(self, angle: int):
        """
        设置夹持器角度
        
        Args:
            angle: 夹持器角度
        """
        if not self.is_ready():
            self.logger.warning("机械臂控制器未就绪，忽略夹持器命令")
            return
        
        with self.lock:
            self.gripper_target_angle = angle
            self.gripper_angle = angle
        
        # 这里应该调用实际的硬件设置命令
        # 例如：Board.setPWMServoPulse(1, angle, 500)
        self._set_gripper_hardware(angle)
        
        self.logger.debug(f"设置夹持器角度: {angle}")
    
    def wait_for_movement_complete(self, timeout: float = 10.0) -> bool:
        """
        等待运动完成
        
        Args:
            timeout: 超时时间
            
        Returns:
            bool: 是否在超时时间内完成
        """
        start_time = time.time()
        
        while self.is_moving and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        if self.is_moving:
            self.logger.warning(f"等待运动完成超时: {timeout}秒")
            return False
        
        return True
    
    def stop_movement(self):
        """停止当前运动"""
        with self.lock:
            self.is_moving = False
        
        self.logger.info("停止机械臂运动")
    
    def get_current_position(self) -> Position:
        """
        获取当前位置
        
        Returns:
            Position: 当前位置
        """
        with self.lock:
            return Position(self.current_position.x, self.current_position.y, self.current_position.z,
                          self.current_position.pitch, self.current_position.yaw, self.current_position.roll)
    
    def is_at_position(self, position: Position, tolerance: float = 1.0) -> bool:
        """
        检查是否在指定位置
        
        Args:
            position: 目标位置
            tolerance: 容差
            
        Returns:
            bool: 是否在指定位置
        """
        current = self.get_current_position()
        
        return (abs(current.x - position.x) <= tolerance and
                abs(current.y - position.y) <= tolerance and
                abs(current.z - position.z) <= tolerance)
    
    def get_status(self) -> Dict[str, Any]:
        """获取机械臂控制器状态"""
        with self.lock:
            return {
                'initialized': self.is_initialized,
                'enabled': self.is_enabled,
                'current_position': self.current_position.to_tuple(),
                'target_position': self.target_position.to_tuple(),
                'is_moving': self.is_moving,
                'gripper_angle': self.gripper_angle,
                'is_gripping': self.is_gripping,
                'movement_speed': self.movement_speed
            }
    
    def _set_gripper_hardware(self, angle: int):
        """
        设置夹持器硬件
        
        Args:
            angle: 夹持器角度
        """
        # 这里应该调用实际的硬件设置命令
        # 例如：Board.setPWMServoPulse(1, angle, 500)
        pass
    
    def _start_control_thread(self):
        """启动控制线程"""
        if self.control_thread and self.control_thread.is_alive():
            return
        
        self.control_running = True
        self.control_thread = threading.Thread(
            target=self._control_loop,
            name="ArmControl",
            daemon=True
        )
        self.control_thread.start()
        self.logger.debug("机械臂控制线程已启动")
    
    def _stop_control_thread(self):
        """停止控制线程"""
        self.control_running = False
        
        if self.control_thread and self.control_thread.is_alive():
            self.control_thread.join(timeout=1.0)
        
        self.logger.debug("机械臂控制线程已停止")
    
    def _control_loop(self):
        """控制循环"""
        while self.control_running:
            try:
                with self.lock:
                    if not self.is_enabled or not self.is_moving:
                        time.sleep(0.1)
                        continue
                    
                    # 检查是否到达目标位置
                    if self.is_at_position(self.target_position):
                        self.is_moving = False
                        self.current_position = Position(
                            self.target_position.x, self.target_position.y, self.target_position.z,
                            self.target_position.pitch, self.target_position.yaw, self.target_position.roll
                        )
                        self.logger.debug("到达目标位置")
                
                time.sleep(0.1)  # 10Hz检查频率
                
            except Exception as e:
                self.logger.error(f"机械臂控制循环错误: {e}")
                time.sleep(0.1)
