#!/usr/bin/python3
# coding=utf8
"""
任务基类
定义所有任务的通用接口和行为
"""
import time
import threading
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum
from utils.logger import get_logger

class TaskState(Enum):
    """任务状态"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskResult:
    """任务结果类"""
    def __init__(self, success: bool = False, data: Any = None, error: str = None):
        self.success = success
        self.data = data
        self.error = error
        self.timestamp = time.time()

class BaseTask(ABC):
    """任务基类"""
    
    def __init__(self, task_id: str, name: str):
        self.task_id = task_id
        self.name = name
        self.logger = get_logger(f"{self.__class__.__name__}_{task_id}")
        
        # 状态管理
        self.state = TaskState.IDLE
        self.result: Optional[TaskResult] = None
        
        # 线程控制
        self.lock = threading.RLock()
        self.stop_event = threading.Event()
        self.task_thread: Optional[threading.Thread] = None
        
        # 时间记录
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        
        # 配置参数
        self.timeout = 30.0  # 默认超时时间
        self.retry_count = 0
        self.max_retries = 3
    
    @abstractmethod
    def execute(self, **kwargs) -> TaskResult:
        """
        执行任务的主要逻辑
        
        Args:
            **kwargs: 任务参数
            
        Returns:
            TaskResult: 任务执行结果
        """
        pass
    
    def start(self, **kwargs) -> bool:
        """
        启动任务
        
        Args:
            **kwargs: 任务参数
            
        Returns:
            bool: 是否成功启动
        """
        with self.lock:
            if self.state != TaskState.IDLE:
                self.logger.warning(f"任务 {self.name} 当前状态为 {self.state.value}，无法启动")
                return False
            
            try:
                self.logger.info(f"启动任务: {self.name}")
                self.state = TaskState.INITIALIZING
                self.start_time = time.time()
                self.stop_event.clear()
                
                # 在新线程中执行任务
                self.task_thread = threading.Thread(
                    target=self._run_task,
                    args=(kwargs,),
                    name=f"Task_{self.name}",
                    daemon=True
                )
                self.task_thread.start()
                
                return True
                
            except Exception as e:
                self.logger.error(f"启动任务失败: {e}")
                self.state = TaskState.FAILED
                self.result = TaskResult(success=False, error=str(e))
                return False
    
    def stop(self, timeout: float = 5.0) -> bool:
        """
        停止任务
        
        Args:
            timeout: 等待超时时间
            
        Returns:
            bool: 是否成功停止
        """
        with self.lock:
            if self.state not in [TaskState.RUNNING, TaskState.PAUSED]:
                return True
            
            self.logger.info(f"停止任务: {self.name}")
            self.stop_event.set()
            
            # 等待任务线程结束
            if self.task_thread and self.task_thread.is_alive():
                self.task_thread.join(timeout=timeout)
                
                if self.task_thread.is_alive():
                    self.logger.warning(f"任务 {self.name} 在 {timeout} 秒内未能停止")
                    return False
            
            self.state = TaskState.CANCELLED
            self.end_time = time.time()
            self.result = TaskResult(success=False, error="任务被取消")
            
            return True
    
    def pause(self):
        """暂停任务"""
        with self.lock:
            if self.state == TaskState.RUNNING:
                self.state = TaskState.PAUSED
                self.logger.info(f"暂停任务: {self.name}")
    
    def resume(self):
        """恢复任务"""
        with self.lock:
            if self.state == TaskState.PAUSED:
                self.state = TaskState.RUNNING
                self.logger.info(f"恢复任务: {self.name}")
    
    def is_running(self) -> bool:
        """检查任务是否正在运行"""
        with self.lock:
            return self.state in [TaskState.RUNNING, TaskState.PAUSED]
    
    def is_completed(self) -> bool:
        """检查任务是否已完成"""
        with self.lock:
            return self.state in [TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED]
    
    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """
        等待任务完成
        
        Args:
            timeout: 超时时间
            
        Returns:
            bool: 是否在超时时间内完成
        """
        if self.task_thread:
            self.task_thread.join(timeout=timeout)
            return not self.task_thread.is_alive()
        return True
    
    def get_progress(self) -> float:
        """
        获取任务进度
        
        Returns:
            float: 进度百分比 (0.0-1.0)
        """
        # 子类可以重写此方法提供更精确的进度
        if self.state == TaskState.COMPLETED:
            return 1.0
        elif self.state in [TaskState.FAILED, TaskState.CANCELLED]:
            return 0.0
        elif self.state == TaskState.RUNNING:
            return 0.5
        else:
            return 0.0
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取任务状态信息
        
        Returns:
            Dict: 状态信息
        """
        with self.lock:
            elapsed_time = None
            if self.start_time:
                end = self.end_time or time.time()
                elapsed_time = end - self.start_time
            
            return {
                'task_id': self.task_id,
                'name': self.name,
                'state': self.state.value,
                'progress': self.get_progress(),
                'start_time': self.start_time,
                'end_time': self.end_time,
                'elapsed_time': elapsed_time,
                'retry_count': self.retry_count,
                'max_retries': self.max_retries,
                'result': {
                    'success': self.result.success if self.result else None,
                    'error': self.result.error if self.result else None,
                } if self.result else None
            }
    
    def _run_task(self, kwargs: Dict[str, Any]):
        """
        任务运行包装器
        
        Args:
            kwargs: 任务参数
        """
        try:
            # 设置运行状态
            with self.lock:
                self.state = TaskState.RUNNING
            
            # 执行任务
            self.logger.info(f"开始执行任务: {self.name}")
            result = self.execute(**kwargs)
            
            # 设置结果
            with self.lock:
                if not self.stop_event.is_set():
                    self.state = TaskState.COMPLETED if result.success else TaskState.FAILED
                    self.result = result
                    self.end_time = time.time()
                    
                    if result.success:
                        self.logger.info(f"任务执行成功: {self.name}")
                    else:
                        self.logger.error(f"任务执行失败: {self.name}, 错误: {result.error}")
                
        except Exception as e:
            self.logger.error(f"任务执行异常: {self.name}, 异常: {e}")
            
            with self.lock:
                self.state = TaskState.FAILED
                self.result = TaskResult(success=False, error=str(e))
                self.end_time = time.time()
    
    def should_stop(self) -> bool:
        """
        检查是否应该停止任务
        
        Returns:
            bool: 是否应该停止
        """
        return self.stop_event.is_set()
    
    def check_timeout(self) -> bool:
        """
        检查是否超时
        
        Returns:
            bool: 是否超时
        """
        if self.start_time and self.timeout > 0:
            elapsed = time.time() - self.start_time
            return elapsed > self.timeout
        return False
