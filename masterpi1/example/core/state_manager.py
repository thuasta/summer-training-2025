#!/usr/bin/python3
# coding=utf8
"""
机器人状态管理器
使用状态机模式管理机器人的各种状态
"""
import threading
import time
from enum import Enum
from typing import Dict, Callable, Any
from utils.logger import Logger

class RobotState(Enum):
    """机器人状态枚举"""
    IDLE = "idle"                    # 空闲状态
    INITIALIZING = "initializing"    # 初始化状态
    LINE_FOLLOWING = "line_following"  # 循线状态
    OBJECT_PICKUP = "object_pickup"   # 物体抓取状态
    DANCING = "dancing"              # 舞蹈状态
    STACKING = "stacking"            # 码垛状态
    TRASH_SORTING = "trash_sorting"  # 垃圾分类状态
    EMERGENCY_STOP = "emergency_stop" # 紧急停止状态
    ERROR = "error"                  # 错误状态
    SHUTDOWN = "shutdown"            # 关闭状态

class StateManager:
    """状态管理器类"""
    
    def __init__(self):
        self.logger = Logger.get_logger(self.__class__.__name__)
        self._current_state = RobotState.IDLE
        self._previous_state = None
        self._state_lock = threading.RLock()
        self._state_change_callbacks: Dict[RobotState, Callable] = {}
        self._state_data: Dict[str, Any] = {}
        self._is_transitioning = False
        
    @property
    def current_state(self) -> RobotState:
        """获取当前状态"""
        with self._state_lock:
            return self._current_state
    
    @property
    def previous_state(self) -> RobotState:
        """获取前一个状态"""
        with self._state_lock:
            return self._previous_state
    
    def set_state(self, new_state: RobotState, force: bool = False) -> bool:
        """
        设置新状态
        
        Args:
            new_state: 新状态
            force: 是否强制切换状态
            
        Returns:
            bool: 是否成功切换状态
        """
        with self._state_lock:
            if self._is_transitioning and not force:
                self.logger.warning(f"状态正在切换中，忽略状态切换请求: {new_state}")
                return False
                
            if not self._is_valid_transition(self._current_state, new_state) and not force:
                self.logger.error(f"无效的状态切换: {self._current_state} -> {new_state}")
                return False
            
            self._is_transitioning = True
            old_state = self._current_state
            
            try:
                self.logger.info(f"状态切换: {old_state} -> {new_state}")
                self._previous_state = old_state
                self._current_state = new_state
                
                # 执行状态切换回调
                if new_state in self._state_change_callbacks:
                    self._state_change_callbacks[new_state]()
                    
                return True
                
            except Exception as e:
                self.logger.error(f"状态切换失败: {e}")
                # 回滚状态
                self._current_state = old_state
                return False
                
            finally:
                self._is_transitioning = False
    
    def _is_valid_transition(self, from_state: RobotState, to_state: RobotState) -> bool:
        """
        检查状态转换是否有效
        
        Args:
            from_state: 源状态
            to_state: 目标状态
            
        Returns:
            bool: 是否为有效转换
        """
        # 定义有效的状态转换规则
        valid_transitions = {
            RobotState.IDLE: [
                RobotState.INITIALIZING, RobotState.LINE_FOLLOWING,
                RobotState.OBJECT_PICKUP, RobotState.DANCING,
                RobotState.EMERGENCY_STOP, RobotState.SHUTDOWN
            ],
            RobotState.INITIALIZING: [
                RobotState.IDLE, RobotState.ERROR, RobotState.EMERGENCY_STOP
            ],
            RobotState.LINE_FOLLOWING: [
                RobotState.IDLE, RobotState.OBJECT_PICKUP, RobotState.DANCING,
                RobotState.STACKING, RobotState.TRASH_SORTING,
                RobotState.EMERGENCY_STOP, RobotState.ERROR
            ],
            RobotState.OBJECT_PICKUP: [
                RobotState.IDLE, RobotState.LINE_FOLLOWING, RobotState.STACKING,
                RobotState.EMERGENCY_STOP, RobotState.ERROR
            ],
            RobotState.DANCING: [
                RobotState.IDLE, RobotState.LINE_FOLLOWING,
                RobotState.EMERGENCY_STOP, RobotState.ERROR
            ],
            RobotState.STACKING: [
                RobotState.IDLE, RobotState.LINE_FOLLOWING,
                RobotState.EMERGENCY_STOP, RobotState.ERROR
            ],
            RobotState.TRASH_SORTING: [
                RobotState.IDLE, RobotState.LINE_FOLLOWING,
                RobotState.EMERGENCY_STOP, RobotState.ERROR
            ],
            RobotState.EMERGENCY_STOP: [
                RobotState.IDLE, RobotState.SHUTDOWN, RobotState.ERROR
            ],
            RobotState.ERROR: [
                RobotState.IDLE, RobotState.EMERGENCY_STOP, RobotState.SHUTDOWN
            ],
            RobotState.SHUTDOWN: []  # 关闭状态不能转换到其他状态
        }
        
        return to_state in valid_transitions.get(from_state, [])
    
    def register_state_callback(self, state: RobotState, callback: Callable):
        """
        注册状态切换回调函数
        
        Args:
            state: 状态
            callback: 回调函数
        """
        with self._state_lock:
            self._state_change_callbacks[state] = callback
            self.logger.debug(f"注册状态回调: {state}")
    
    def set_state_data(self, key: str, value: Any):
        """
        设置状态数据
        
        Args:
            key: 数据键
            value: 数据值
        """
        with self._state_lock:
            self._state_data[key] = value
    
    def get_state_data(self, key: str, default: Any = None) -> Any:
        """
        获取状态数据
        
        Args:
            key: 数据键
            default: 默认值
            
        Returns:
            Any: 数据值
        """
        with self._state_lock:
            return self._state_data.get(key, default)
    
    def clear_state_data(self):
        """清空状态数据"""
        with self._state_lock:
            self._state_data.clear()
    
    def is_in_state(self, *states: RobotState) -> bool:
        """
        检查是否处于指定状态之一
        
        Args:
            states: 状态列表
            
        Returns:
            bool: 是否处于指定状态
        """
        with self._state_lock:
            return self._current_state in states
    
    def wait_for_state(self, target_state: RobotState, timeout: float = 10.0) -> bool:
        """
        等待状态切换到指定状态
        
        Args:
            target_state: 目标状态
            timeout: 超时时间
            
        Returns:
            bool: 是否成功等待到目标状态
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.current_state == target_state:
                return True
            time.sleep(0.1)
        return False
    
    def emergency_stop(self):
        """紧急停止"""
        self.set_state(RobotState.EMERGENCY_STOP, force=True)
        self.logger.warning("触发紧急停止")
    
    def get_state_info(self) -> Dict[str, Any]:
        """
        获取状态信息
        
        Returns:
            Dict: 状态信息
        """
        with self._state_lock:
            return {
                "current_state": self._current_state.value,
                "previous_state": self._previous_state.value if self._previous_state else None,
                "is_transitioning": self._is_transitioning,
                "state_data": dict(self._state_data)
            }
