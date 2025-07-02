#!/bin/bash
# CliffWalking 训练脚本使用示例
echo "1. 基础用法 - 使用默认SARSA算法："
echo "python cliffwalking.py"
echo

echo "2. 使用Q-Learning算法："
echo "python cliffwalking.py --algorithm qlearning"
echo

echo "3. 自定义参数训练："
echo "python cliffwalking.py -a sarsa -e 3000 --epsilon 0.1 --alpha 0.2"
echo


# python cliffwalking.py --algorithm qlearning
python cliffwalking.py