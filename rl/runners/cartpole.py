import gymnasium as gym
import numpy as np
import torch
import sys
import os

# 添加父目录到Python路径，以便导入algorithms模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.PG import PGAgent
def main():
    env = gym.make('CartPole-v1', render_mode='rgb_array')  # 使用 RGB 渲染模式
    obs, info = env.reset()

    print("环境已重置，初始状态:", obs)
    print("观测空间", env.observation_space)
    print("动作空间", env.action_space)
    print("动作空间大小:", env.action_space.n)


    MyAgent = PGAgent(    input_dim=env.observation_space.shape[0], 
        hidden_dim=128, 
        output_dim=env.action_space.n, 
        lr=1e-3, 
        gamma=0.99
    )

    MyAgent.train(env, episodes=2000, print_every=200)

    # 测试智能体
    print("\n开始测试训练后的智能体...")
    env_test = gym.make('CartPole-v1', render_mode='human')  # 用于可视化测试
    
    for test_episode in range(3):  # 测试3轮
        obs, info = env_test.reset()
        done = False
        total_reward = 0
        steps = 0
        
        while not done:
            # 使用训练好的策略选择动作（贪婪策略，不探索）
            with torch.no_grad():  # 测试时不需要梯度
                action_probs = MyAgent.forward(obs)
                action = torch.argmax(action_probs).item()  # 选择概率最大的动作
            
            obs, reward, terminated, truncated, info = env_test.step(action)
            done = terminated or truncated
            total_reward += reward
            steps += 1
            
        print(f"测试第{test_episode + 1}轮: 总奖励 {total_reward}, 步数 {steps}")
    
    env_test.close()


if __name__ == "__main__":
    main()