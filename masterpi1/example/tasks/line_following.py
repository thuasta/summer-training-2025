#!/usr/bin/python3
# coding=utf8
"""
循线任务实现
基于视觉的线条跟踪任务
"""
import time
import cv2
from typing import List, Tuple, Optional, Any
from tasks.base_task import BaseTask, TaskResult

class LineFollowingTask(BaseTask):
    """循线任务类"""
    
    def __init__(self, task_id: str, camera, motor_controller, color_detector):
        super().__init__(task_id, "LineFollowing")
        
        # 硬件组件
        self.camera = camera
        self.motor_controller = motor_controller
        self.color_detector = color_detector
        
        # 任务参数
        self.target_colors: List[str] = []
        self.stop_mode = 0  # 0: 正常停止, 1: 检测横线停止
        self.task_after_stop = 0  # 停止后执行的任务ID
        
        # 循线状态
        self.line_center_x = -1
        self.no_line_count = 0
        self.horizontal_line_detected = False
        self.line_start_time = 0
        self.can_detect_horizontal = False
        
        # 配置参数
        self.no_line_threshold = 30
        self.image_center_x = 320
        self.timeout = 60.0  # 循线任务较长，设置更长超时
    
    def execute(self, **kwargs) -> TaskResult:
        """
        执行循线任务
        
        Args:
            **kwargs: 任务参数
                - target_colors: 目标颜色列表
                - stop_mode: 停止模式
                - task_after_stop: 停止后任务ID
                
        Returns:
            TaskResult: 执行结果
        """
        try:
            # 获取任务参数
            self.target_colors = kwargs.get('target_colors', ['red'])
            self.stop_mode = kwargs.get('stop_mode', 0)
            self.task_after_stop = kwargs.get('task_after_stop', 0)
            
            self.logger.info(f"开始循线任务 - 目标颜色: {self.target_colors}, 停止模式: {self.stop_mode}")
            
            # 重置状态
            self._reset_state()
            
            # 初始化硬件
            if not self._initialize_hardware():
                return TaskResult(success=False, error="硬件初始化失败")
            
            # 执行循线主循环
            result = self._line_following_loop()
            
            # 停止电机
            self.motor_controller.stop_all_motors()
            
            return result
            
        except Exception as e:
            self.logger.error(f"循线任务执行异常: {e}")
            return TaskResult(success=False, error=str(e))
    
    def _reset_state(self):
        """重置循线状态"""
        self.line_center_x = -1
        self.no_line_count = 0
        self.horizontal_line_detected = False
        self.line_start_time = time.time()
        self.can_detect_horizontal = False
    
    def _initialize_hardware(self) -> bool:
        """初始化硬件"""
        try:
            # 确保电机控制器就绪
            if not self.motor_controller.is_ready():
                self.logger.error("电机控制器未就绪")
                return False
            
            # 确保摄像头可用
            if not self.camera.isOpened():
                self.logger.error("摄像头未打开")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"硬件初始化失败: {e}")
            return False
    
    def _line_following_loop(self) -> TaskResult:
        """循线主循环"""
        self.logger.info("进入循线主循环")
        
        while not self.should_stop():
            try:
                # 检查超时
                if self.check_timeout():
                    return TaskResult(success=False, error="循线任务超时")
                
                # 处理图像帧
                frame_result = self._process_frame()
                
                if frame_result == "line_end":
                    # 线路结束
                    self.logger.info("检测到线路结束")
                    return TaskResult(success=True, data={
                        'end_reason': 'line_end',
                        'horizontal_line_detected': self.horizontal_line_detected,
                        'task_after_stop': self.task_after_stop
                    })
                elif frame_result == "no_frame":
                    # 无法获取图像帧
                    time.sleep(0.01)
                    continue
                
                # 控制电机
                self._control_motors()
                
                # 短暂延时，维持约30FPS处理速度
                time.sleep(0.033)
                
            except Exception as e:
                self.logger.error(f"循线循环错误: {e}")
                return TaskResult(success=False, error=f"循环错误: {e}")
        
        # 任务被停止
        return TaskResult(success=False, error="任务被中断")
    
    def _process_frame(self) -> str:
        """
        处理图像帧
        
        Returns:
            str: 处理结果 ("continue", "line_end", "no_frame")
        """
        # 获取图像帧
        ret, frame = self.camera.read()
        if not ret or frame is None:
            return "no_frame"
        
        # 更新横线检测状态
        self._update_horizontal_detection_state()
        
        # 检测线的中心
        detection_result = self.color_detector.detect_line_center(frame, self.target_colors)
        
        if len(detection_result) >= 5:
            center_x, center_points, processed_img, detected_color, horizontal_line = detection_result
        else:
            # 兼容旧版本接口
            center_x = detection_result[0] if len(detection_result) > 0 else -1
            horizontal_line = False
        
        # 更新线中心位置
        self.line_center_x = center_x
        
        # 处理横线检测
        if self.can_detect_horizontal and horizontal_line and self.stop_mode == 1:
            self.horizontal_line_detected = True
            self.logger.info("检测到横向线，准备停止")
            return "line_end"
        
        # 检查是否丢失线条
        if center_x == -1:
            self.no_line_count += 1
            if self.no_line_count >= self.no_line_threshold:
                self.logger.info("长时间未检测到线条，线路结束")
                return "line_end"
        else:
            self.no_line_count = 0
        
        return "continue"
    
    def _update_horizontal_detection_state(self):
        """更新横线检测状态"""
        current_time = time.time()
        if current_time - self.line_start_time > 1.0 and not self.can_detect_horizontal:
            self.can_detect_horizontal = True
            self.logger.debug("开始启用横线检测")
    
    def _control_motors(self):
        """控制电机运动"""
        if self.line_center_x == -1:
            # 未检测到线条，缓慢前进搜索
            self.motor_controller.move_forward(speed=20)
            return
        
        # 计算偏差
        error = self.line_center_x - self.image_center_x
        
        # 使用PID控制计算电机速度
        left_speed, right_speed = self.motor_controller.move_with_pid(error)
        
        # 设置电机速度
        self.motor_controller.set_all_motor_speeds({
            1: left_speed,   # 左前
            2: right_speed,  # 右前  
            3: left_speed,   # 左后
            4: right_speed   # 右后
        })
    
    def get_progress(self) -> float:
        """
        获取循线进度
        根据运行时间估算进度
        
        Returns:
            float: 进度百分比
        """
        if self.state.value == "completed":
            return 1.0
        elif self.state.value in ["failed", "cancelled"]:
            return 0.0
        elif self.start_time:
            # 基于运行时间估算进度（假设平均30秒完成一段循线）
            elapsed = time.time() - self.start_time
            estimated_total = 30.0
            progress = min(0.9, elapsed / estimated_total)  # 最多90%，完成时才100%
            return progress
        else:
            return 0.0
    
    def pause_line_following(self):
        """暂停循线（停止电机）"""
        self.motor_controller.stop_all_motors()
        self.pause()
    
    def resume_line_following(self):
        """恢复循线"""
        self.resume()
    
    def get_line_status(self) -> dict:
        """
        获取循线状态信息
        
        Returns:
            dict: 循线状态
        """
        return {
            'target_colors': self.target_colors,
            'line_center_x': self.line_center_x,
            'no_line_count': self.no_line_count,
            'horizontal_line_detected': self.horizontal_line_detected,
            'can_detect_horizontal': self.can_detect_horizontal,
            'stop_mode': self.stop_mode,
            'task_after_stop': self.task_after_stop
        }
