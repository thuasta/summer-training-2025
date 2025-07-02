#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rl.runners.cliffwalking import main
import sys

# 测试DQN
sys.argv = ['test_dqn.py', '--algorithm', 'dqn', '--episodes', '100']
main()
