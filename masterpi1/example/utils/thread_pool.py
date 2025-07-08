#!/usr/bin/python3
# coding=utf8
"""
线程池管理模块
提供统一的线程池管理功能
"""
import threading
import time
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Dict, Optional, Callable, Any
from utils.logger import get_logger

class ThreadPool:
    """线程池管理器"""
    
    def __init__(self, max_workers: int = 4, thread_name_prefix: str = "Thread"):
        self.max_workers = max_workers
        self.thread_name_prefix = thread_name_prefix
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix=thread_name_prefix
        )
        self.futures: Dict[str, Future] = {}
        self.lock = threading.Lock()
        self.logger = get_logger(self.__class__.__name__)
        
    def submit(self, task_id: str, func: Callable, *args, **kwargs) -> Future:
        """
        提交任务到线程池
        
        Args:
            task_id: 任务ID
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            Future: 任务Future对象
        """
        with self.lock:
            if task_id in self.futures:
                # 如果任务已存在且未完成，先取消
                old_future = self.futures[task_id]
                if not old_future.done():
                    old_future.cancel()
            
            future = self.executor.submit(func, *args, **kwargs)
            self.futures[task_id] = future
            
            self.logger.debug(f"提交任务到线程池: {task_id}")
            return future
    
    def cancel(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功取消
        """
        with self.lock:
            future = self.futures.get(task_id)
            if future and not future.done():
                result = future.cancel()
                self.logger.debug(f"取消任务: {task_id}, 结果: {result}")
                return result
            return False
    
    def is_running(self, task_id: str) -> bool:
        """
        检查任务是否正在运行
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否正在运行
        """
        with self.lock:
            future = self.futures.get(task_id)
            return future and future.running() if future else False
    
    def is_done(self, task_id: str) -> bool:
        """
        检查任务是否已完成
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否已完成
        """
        with self.lock:
            future = self.futures.get(task_id)
            return future.done() if future else False
    
    def get_result(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """
        获取任务结果
        
        Args:
            task_id: 任务ID
            timeout: 超时时间
            
        Returns:
            Any: 任务结果
        """
        with self.lock:
            future = self.futures.get(task_id)
            if not future:
                raise ValueError(f"任务不存在: {task_id}")
            
            return future.result(timeout=timeout)
    
    def wait_for_completion(self, task_id: str, timeout: Optional[float] = None) -> bool:
        """
        等待任务完成
        
        Args:
            task_id: 任务ID
            timeout: 超时时间
            
        Returns:
            bool: 是否在超时时间内完成
        """
        with self.lock:
            future = self.futures.get(task_id)
            if not future:
                return False
        
        try:
            future.result(timeout=timeout)
            return True
        except Exception:
            return False
    
    def cleanup_completed(self):
        """清理已完成的任务"""
        with self.lock:
            completed_tasks = [
                task_id for task_id, future in self.futures.items()
                if future.done()
            ]
            
            for task_id in completed_tasks:
                del self.futures[task_id]
            
            if completed_tasks:
                self.logger.debug(f"清理已完成任务: {len(completed_tasks)} 个")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取线程池统计信息
        
        Returns:
            Dict: 统计信息
        """
        with self.lock:
            total_tasks = len(self.futures)
            running_tasks = sum(1 for f in self.futures.values() if f.running())
            completed_tasks = sum(1 for f in self.futures.values() if f.done())
            
            return {
                'max_workers': self.max_workers,
                'total_tasks': total_tasks,
                'running_tasks': running_tasks,
                'completed_tasks': completed_tasks,
                'pending_tasks': total_tasks - running_tasks - completed_tasks
            }
    
    def shutdown(self, wait: bool = True):
        """
        关闭线程池
        
        Args:
            wait: 是否等待所有任务完成
        """
        self.logger.info("关闭线程池...")
        
        # 取消所有待执行的任务
        with self.lock:
            for task_id, future in self.futures.items():
                if not future.done():
                    future.cancel()
        
        self.executor.shutdown(wait=wait)
        
        with self.lock:
            self.futures.clear()
        
        self.logger.info("线程池已关闭")

class ThreadPoolManager:
    """线程池管理器单例"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._pools: Dict[str, ThreadPool] = {}
            self._initialized = True
            self.logger = get_logger(self.__class__.__name__)
    
    def get_pool(self, pool_name: str, max_workers: int = 4) -> ThreadPool:
        """
        获取线程池
        
        Args:
            pool_name: 线程池名称
            max_workers: 最大工作线程数
            
        Returns:
            ThreadPool: 线程池实例
        """
        if pool_name not in self._pools:
            self._pools[pool_name] = ThreadPool(
                max_workers=max_workers,
                thread_name_prefix=f"{pool_name}Pool"
            )
            self.logger.debug(f"创建线程池: {pool_name}")
        
        return self._pools[pool_name]
    
    def shutdown_all(self, wait: bool = True):
        """
        关闭所有线程池
        
        Args:
            wait: 是否等待所有任务完成
        """
        for pool_name, pool in self._pools.items():
            self.logger.info(f"关闭线程池: {pool_name}")
            pool.shutdown(wait=wait)
        
        self._pools.clear()
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有线程池的统计信息
        
        Returns:
            Dict: 所有线程池的统计信息
        """
        return {
            pool_name: pool.get_stats()
            for pool_name, pool in self._pools.items()
        }

# 全局线程池管理器实例
thread_pool_manager = ThreadPoolManager()

def get_thread_pool(pool_name: str, max_workers: int = 4) -> ThreadPool:
    """
    获取线程池的便捷函数
    
    Args:
        pool_name: 线程池名称
        max_workers: 最大工作线程数
        
    Returns:
        ThreadPool: 线程池实例
    """
    return thread_pool_manager.get_pool(pool_name, max_workers)
