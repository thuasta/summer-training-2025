#!/bin/bash
# CliffWalking 训练脚本使用示例
echo "1. 基础用法 - 使用默认SARSA算法："
echo "python -m rl.runners.cliffwalking"
echo

echo "2. 使用Q-Learning算法："
echo "python -m rl.runners.cliffwalking --algorithm qlearning"
echo

echo "3. 使用DQN算法："
echo "python -m rl.runners.cliffwalking --algorithm dqn"
echo

echo "4. 自定义参数训练："
echo "python -m rl.runners.cliffwalking -a sarsa -e 3000 --epsilon 0.1 --alpha 0.2"
echo

echo "正在运行DQN算法..."
# 从项目根目录运行
cd /Users/zhangboshi/Downloads/github/ASTA-Summer-train-2025
python -m rl.runners.cliffwalking --algorithm dqn