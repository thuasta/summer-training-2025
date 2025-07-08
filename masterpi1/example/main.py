#!/usr/bin/python3
# coding=utf8
"""
主程序入口
展示优化的机器人控制系统使用方法
"""
import cv2
import time
import sys
from core.robot import SmartRobot
from utils.logger import Logger
from utils.config import load_config

def main():
    """主函数"""
    print("=== 智能机器人控制系统 ===")
    print()
    
    # 初始化日志系统
    Logger.initialize(log_level="INFO", log_file="logs/main.log")
    logger = Logger.get_logger("Main")
    
    # 加载配置
    try:
        load_config("config/robot_config.yaml")
        logger.info("配置加载成功")
    except Exception as e:
        logger.warning(f"配置加载失败，使用默认配置: {e}")
    
    # 打开摄像头
    cap = None
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logger.error("无法打开摄像头")
            return
        
        logger.info("摄像头初始化成功")
        
        # 创建机器人实例
        robot = SmartRobot(cap)
        
        # 初始化机器人
        if not robot.initialize():
            logger.error("机器人初始化失败")
            return
        
        # 启动机器人
        robot.start()
        
        # 演示任务执行
        demonstrate_tasks(robot)
        
        # 运行机器人（阻塞）
        robot.run()
        
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序运行错误: {e}")
    finally:
        # 清理资源
        if cap:
            cap.release()
        cv2.destroyAllWindows()
        
        logger.info("程序结束")

def demonstrate_tasks(robot: SmartRobot):
    """
    演示任务执行
    
    Args:
        robot: 机器人实例
    """
    logger = Logger.get_logger("Demo")
    
    logger.info("开始演示任务执行...")
    
    # 等待初始化完成
    time.sleep(2)
    
    # 演示任务列表
    demo_tasks = [
        ("line_following", {"target_colors": ["red"]}),
        ("object_pickup", {"target_object": "cube"}),
        ("dancing", {"dance_type": "wave"}),
        ("stacking", {"sequence": ["1", "2", "3"]}),
        ("trash_sorting", {"colors": ["yellow"]}),
    ]
    
    # 依次执行演示任务
    for task_name, task_kwargs in demo_tasks:
        logger.info(f"演示任务: {task_name}")
        
        try:
            task_id = robot.execute_task(task_name, **task_kwargs)
            
            if task_id:
                logger.info(f"任务 {task_name} 已提交，ID: {task_id}")
                
                # 等待任务完成
                if robot.task_scheduler.wait_for_task(task_id, timeout=10):
                    result = robot.task_scheduler.get_task_result(task_id)
                    if result and result.success:
                        logger.info(f"任务 {task_name} 执行成功")
                    else:
                        logger.warning(f"任务 {task_name} 执行失败")
                else:
                    logger.warning(f"任务 {task_name} 执行超时")
            else:
                logger.error(f"任务 {task_name} 提交失败")
                
        except Exception as e:
            logger.error(f"演示任务 {task_name} 时出错: {e}")
        
        # 任务间隔
        time.sleep(1)
    
    logger.info("任务演示完成")

def interactive_mode(robot: SmartRobot):
    """
    交互式模式
    
    Args:
        robot: 机器人实例
    """
    logger = Logger.get_logger("Interactive")
    
    print("\n=== 交互式控制模式 ===")
    print("可用命令:")
    print("1. line - 循线任务")
    print("2. pickup - 抓取任务")
    print("3. dance - 舞蹈任务")
    print("4. stack - 码垛任务")
    print("5. sort - 垃圾分类任务")
    print("6. status - 查看状态")
    print("7. quit - 退出")
    print()
    
    while True:
        try:
            command = input("请输入命令: ").strip().lower()
            
            if command == "quit" or command == "q":
                break
            elif command == "line" or command == "1":
                colors = input("请输入颜色 (例: red,black): ").split(",")
                colors = [c.strip() for c in colors if c.strip()]
                robot.execute_task("line_following", target_colors=colors)
            elif command == "pickup" or command == "2":
                obj = input("请输入目标物体 (默认: cube): ").strip() or "cube"
                robot.execute_task("object_pickup", target_object=obj)
            elif command == "dance" or command == "3":
                dance_type = input("请输入舞蹈类型 (默认: wave): ").strip() or "wave"
                robot.execute_task("dancing", dance_type=dance_type)
            elif command == "stack" or command == "4":
                sequence = input("请输入码垛序列 (例: 1,2,3): ").split(",")
                sequence = [s.strip() for s in sequence if s.strip()]
                robot.execute_task("stacking", sequence=sequence)
            elif command == "sort" or command == "5":
                colors = input("请输入垃圾颜色 (例: yellow): ").split(",")
                colors = [c.strip() for c in colors if c.strip()]
                robot.execute_task("trash_sorting", colors=colors)
            elif command == "status" or command == "6":
                print_status(robot)
            else:
                print("未知命令，请重新输入")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"交互式模式错误: {e}")

def print_status(robot: SmartRobot):
    """
    打印机器人状态
    
    Args:
        robot: 机器人实例
    """
    print("\n=== 机器人状态 ===")
    
    # 状态管理器状态
    state_info = robot.state_manager.get_state_info()
    print(f"当前状态: {state_info['current_state']}")
    print(f"前一状态: {state_info['previous_state']}")
    print(f"状态切换中: {state_info['is_transitioning']}")
    
    # 任务调度器统计
    task_stats = robot.task_scheduler.get_stats()
    print(f"总任务数: {task_stats['total_tasks']}")
    print(f"已完成: {task_stats['completed_tasks']}")
    print(f"失败: {task_stats['failed_tasks']}")
    print(f"等待中: {task_stats['pending_tasks']}")
    print(f"运行中: {task_stats['running_tasks']}")
    
    # 线程池统计
    from utils.thread_pool import thread_pool_manager
    pool_stats = thread_pool_manager.get_all_stats()
    print("线程池状态:")
    for pool_name, stats in pool_stats.items():
        print(f"  {pool_name}: 运行中={stats['running_tasks']}, 总计={stats['total_tasks']}")
    
    print("==================")

if __name__ == '__main__':
    # 检查Python版本
    if sys.version_info.major < 3:
        print('请使用Python 3运行此程序!')
        sys.exit(1)
    
    main()
