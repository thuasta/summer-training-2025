#!/usr/bin/python3
# coding=utf8
"""
任务调度器
负责管理和调度各种任务的执行
"""
import threading
import time
import queue
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, Future

class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"      # 等待执行
    RUNNING = "running"      # 正在执行
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    CANCELLED = "cancelled"  # 已取消

@dataclass
class TaskResult:
    """任务执行结果"""
    success: bool
    data: Any = None
    error: Optional[Exception] = None
    execution_time: float = 0.0

@dataclass
class Task:
    """任务定义"""
    id: str
    name: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    timeout: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 0
    dependencies: List[str] = field(default_factory=list)
    callback: Optional[Callable] = None
    
    # 运行时状态
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[TaskResult] = None
    future: Optional[Future] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # 任务存储
        self.tasks: Dict[str, Task] = {}
        self.task_queue = queue.PriorityQueue()
        
        # 调度器状态
        self.is_running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        
        # 线程安全
        self.lock = threading.RLock()
        
        # 统计信息
        self.stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'cancelled_tasks': 0
        }
    
    def start(self):
        """启动任务调度器"""
        with self.lock:
            if self.is_running:
                return
            
            self.is_running = True
            self.scheduler_thread = threading.Thread(
                target=self._scheduler_loop,
                name="TaskScheduler",
                daemon=True
            )
            self.scheduler_thread.start()
            print("任务调度器已启动")
    
    def stop(self, wait: bool = True):
        """停止任务调度器"""
        with self.lock:
            if not self.is_running:
                return
            
            self.is_running = False
            
            # 取消所有待执行的任务
            self._cancel_pending_tasks()
            
            # 等待当前任务完成
            if wait:
                self.executor.shutdown(wait=True)
            else:
                self.executor.shutdown(wait=False)
            
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5.0)
            
            print("任务调度器已停止")
    
    def submit_task(self, task: Task) -> str:
        """
        提交任务
        
        Args:
            task: 任务对象
            
        Returns:
            str: 任务ID
        """
        with self.lock:
            if not self.is_running:
                raise RuntimeError("任务调度器未运行")
            
            # 检查依赖关系
            if not self._check_dependencies(task):
                raise ValueError(f"任务 {task.id} 的依赖关系不满足")
            
            self.tasks[task.id] = task
            
            # 将任务加入优先队列（优先级越高，数值越小）
            priority_value = 5 - task.priority.value
            self.task_queue.put((priority_value, task.created_at, task.id))
            
            self.stats['total_tasks'] += 1
            print(f"任务已提交: {task.name} (ID: {task.id})")
            
            return task.id
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功取消
        """
        with self.lock:
            task = self.tasks.get(task_id)
            if not task:
                return False
            
            if task.status == TaskStatus.RUNNING and task.future:
                # 尝试取消正在运行的任务
                cancelled = task.future.cancel()
                if cancelled:
                    task.status = TaskStatus.CANCELLED
                    self.stats['cancelled_tasks'] += 1
                return cancelled
            elif task.status == TaskStatus.PENDING:
                # 标记待执行任务为已取消
                task.status = TaskStatus.CANCELLED
                self.stats['cancelled_tasks'] += 1
                return True
            
            return False
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            Optional[TaskStatus]: 任务状态
        """
        with self.lock:
            task = self.tasks.get(task_id)
            return task.status if task else None
    
    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """
        获取任务结果
        
        Args:
            task_id: 任务ID
            
        Returns:
            Optional[TaskResult]: 任务结果
        """
        with self.lock:
            task = self.tasks.get(task_id)
            return task.result if task else None
    
    def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> bool:
        """
        等待任务完成
        
        Args:
            task_id: 任务ID
            timeout: 超时时间
            
        Returns:
            bool: 任务是否完成
        """
        task = self.tasks.get(task_id)
        if not task or not task.future:
            return False
        
        try:
            task.future.result(timeout=timeout)
            return True
        except Exception:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            Dict: 统计信息
        """
        with self.lock:
            stats = dict(self.stats)
            stats['pending_tasks'] = sum(
                1 for task in self.tasks.values() 
                if task.status == TaskStatus.PENDING
            )
            stats['running_tasks'] = sum(
                1 for task in self.tasks.values() 
                if task.status == TaskStatus.RUNNING
            )
            return stats
    
    def _scheduler_loop(self):
        """调度器主循环"""
        while self.is_running:
            try:
                # 获取下一个任务（阻塞等待1秒）
                try:
                    priority, created_at, task_id = self.task_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                with self.lock:
                    task = self.tasks.get(task_id)
                    if not task or task.status != TaskStatus.PENDING:
                        continue
                    
                    # 检查依赖关系
                    if not self._are_dependencies_completed(task):
                        # 重新放回队列
                        self.task_queue.put((priority, created_at, task_id))
                        time.sleep(0.1)  # 短暂等待
                        continue
                    
                    # 提交任务执行
                    task.status = TaskStatus.RUNNING
                    task.started_at = time.time()
                    task.future = self.executor.submit(self._execute_task, task)
                
            except Exception as e:
                print(f"调度器错误: {e}")
                time.sleep(0.1)
    
    def _execute_task(self, task: Task) -> TaskResult:
        """
        执行任务
        
        Args:
            task: 任务对象
            
        Returns:
            TaskResult: 执行结果
        """
        start_time = time.time()
        result = TaskResult(success=False)
        
        try:
            print(f"开始执行任务: {task.name}")
            
            # 执行任务函数
            if task.timeout:
                # TODO: 实现超时控制
                data = task.func(*task.args, **task.kwargs)
            else:
                data = task.func(*task.args, **task.kwargs)
            
            result.success = True
            result.data = data
            task.status = TaskStatus.COMPLETED
            
            with self.lock:
                self.stats['completed_tasks'] += 1
            
            print(f"任务执行成功: {task.name}")
            
        except Exception as e:
            result.error = e
            task.status = TaskStatus.FAILED
            
            with self.lock:
                self.stats['failed_tasks'] += 1
            
            print(f"任务执行失败: {task.name}, 错误: {e}")
            
            # 重试逻辑
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                
                # 重新提交任务
                priority_value = 5 - task.priority.value
                with self.lock:
                    self.task_queue.put((priority_value, time.time(), task.id))
                
                print(f"任务重试: {task.name} ({task.retry_count}/{task.max_retries})")
        
        finally:
            result.execution_time = time.time() - start_time
            task.result = result
            task.completed_at = time.time()
            
            # 执行回调
            if task.callback:
                try:
                    task.callback(task, result)
                except Exception as e:
                    print(f"任务回调执行失败: {e}")
        
        return result
    
    def _check_dependencies(self, task: Task) -> bool:
        """检查任务依赖关系是否存在"""
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                return False
        return True
    
    def _are_dependencies_completed(self, task: Task) -> bool:
        """检查任务依赖是否都已完成"""
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True
    
    def _cancel_pending_tasks(self):
        """取消所有待执行的任务"""
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.CANCELLED
                self.stats['cancelled_tasks'] += 1
