#!/usr/bin/python3
# coding=utf8
"""
硬件控制基类
定义硬件控制器的通用接口
"""
import threading
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from utils.logger import get_logger

class HardwareController(ABC):
    """硬件控制器抽象基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(f"{self.__class__.__name__}_{name}")
        self.is_initialized = False
        self.is_enabled = False
        self.lock = threading.RLock()
        self.status = {}
        
    @abstractmethod
    def initialize(self) -> bool:
        """
        初始化硬件
        
        Returns:
            bool: 是否初始化成功
        """
        pass
    
    @abstractmethod
    def shutdown(self):
        """关闭硬件"""
        pass
    
    @abstractmethod
    def enable(self):
        """启用硬件"""
        pass
    
    @abstractmethod
    def disable(self):
        """禁用硬件"""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        获取硬件状态
        
        Returns:
            Dict: 硬件状态信息
        """
        pass
    
    def is_ready(self) -> bool:
        """
        检查硬件是否就绪
        
        Returns:
            bool: 是否就绪
        """
        with self.lock:
            return self.is_initialized and self.is_enabled
    
    def set_status(self, key: str, value: Any):
        """
        设置状态信息
        
        Args:
            key: 状态键
            value: 状态值
        """
        with self.lock:
            self.status[key] = value
    
    def get_status_value(self, key: str, default: Any = None) -> Any:
        """
        获取状态值
        
        Args:
            key: 状态键
            default: 默认值
            
        Returns:
            Any: 状态值
        """
        with self.lock:
            return self.status.get(key, default)
