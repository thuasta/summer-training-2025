#!/usr/bin/python3
# coding=utf8
"""
配置管理模块
集中管理所有配置参数
"""
import yaml
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class VisionConfig:
    """视觉处理配置"""
    image_width: int = 640
    image_height: int = 480
    roi_regions: list = None
    color_thresholds: dict = None
    
    def __post_init__(self):
        if self.roi_regions is None:
            self.roi_regions = [
                (240, 280, 0, 640, 0.1),
                (340, 380, 0, 640, 0.3),
                (430, 460, 0, 640, 0.6)
            ]

@dataclass
class MotorConfig:
    """电机控制配置"""
    base_speed: int = 50
    pid_p: float = 0.28
    pid_i: float = 0.16
    pid_d: float = 0.18
    max_speed: int = 100
    min_speed: int = 20

@dataclass
class ArmConfig:
    """机械臂配置"""
    servo_positions: dict = None
    grab_servo_angle: int = 1350
    release_servo_angle: int = 1500
    default_position: tuple = (0, 7, 11)
    pitch_angle: int = -60
    yaw_angle: int = -90
    
    def __post_init__(self):
        if self.servo_positions is None:
            self.servo_positions = {
                'red': (-12, 12, 2),
                'green': (0, 8, 10),
                'blue': (-12, 20, 2),
                'capture': (0, 8, 10)
            }

@dataclass
class TaskConfig:
    """任务配置"""
    patrol_sequence: list = None
    max_retries: int = 3
    task_timeout: float = 30.0
    
    def __post_init__(self):
        if self.patrol_sequence is None:
            self.patrol_sequence = [
                (['red'], 0, 3),
                (['black'], 0, 19),
                (['red', 'black'], 0, 28),
                # ... 更多序列
            ]

@dataclass
class SystemConfig:
    """系统配置"""
    max_workers: int = 4
    log_level: str = "INFO"
    log_file: Optional[str] = None
    enable_debug: bool = False

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self._config_data = {}
        
        # 默认配置
        self.vision = VisionConfig()
        self.motor = MotorConfig()
        self.arm = ArmConfig()
        self.task = TaskConfig()
        self.system = SystemConfig()
        
        # 加载配置文件
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
    
    def load_config(self, config_file: str):
        """
        从YAML文件加载配置
        
        Args:
            config_file: 配置文件路径
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self._config_data = yaml.safe_load(f) or {}
            
            # 更新配置对象
            self._update_config_objects()
            
        except Exception as e:
            print(f"加载配置文件失败: {e}")
    
    def save_config(self, config_file: Optional[str] = None):
        """
        保存配置到YAML文件
        
        Args:
            config_file: 配置文件路径
        """
        file_path = config_file or self.config_file
        if not file_path:
            raise ValueError("未指定配置文件路径")
        
        try:
            # 构建配置数据
            config_data = {
                'vision': self._dataclass_to_dict(self.vision),
                'motor': self._dataclass_to_dict(self.motor),
                'arm': self._dataclass_to_dict(self.arm),
                'task': self._dataclass_to_dict(self.task),
                'system': self._dataclass_to_dict(self.system)
            }
            
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
                
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def _update_config_objects(self):
        """更新配置对象"""
        # 更新视觉配置
        if 'vision' in self._config_data:
            self._update_dataclass(self.vision, self._config_data['vision'])
        
        # 更新电机配置
        if 'motor' in self._config_data:
            self._update_dataclass(self.motor, self._config_data['motor'])
        
        # 更新机械臂配置
        if 'arm' in self._config_data:
            self._update_dataclass(self.arm, self._config_data['arm'])
        
        # 更新任务配置
        if 'task' in self._config_data:
            self._update_dataclass(self.task, self._config_data['task'])
        
        # 更新系统配置
        if 'system' in self._config_data:
            self._update_dataclass(self.system, self._config_data['system'])
    
    def _update_dataclass(self, obj, data: Dict[str, Any]):
        """更新dataclass对象"""
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
    
    def _dataclass_to_dict(self, obj) -> Dict[str, Any]:
        """将dataclass对象转换为字典"""
        result = {}
        for field_name in obj.__dataclass_fields__:
            value = getattr(obj, field_name)
            result[field_name] = value
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键（支持点分隔的嵌套键）
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        keys = key.split('.')
        value = self._config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """
        设置配置值
        
        Args:
            key: 配置键（支持点分隔的嵌套键）
            value: 配置值
        """
        keys = key.split('.')
        data = self._config_data
        
        # 创建嵌套字典结构
        for k in keys[:-1]:
            if k not in data or not isinstance(data[k], dict):
                data[k] = {}
            data = data[k]
        
        data[keys[-1]] = value
        
        # 更新配置对象
        self._update_config_objects()

# 全局配置实例
config = ConfigManager()

def load_config(config_file: str):
    """加载配置文件的便捷函数"""
    global config
    config.load_config(config_file)

def get_config() -> ConfigManager:
    """获取配置管理器实例"""
    return config
