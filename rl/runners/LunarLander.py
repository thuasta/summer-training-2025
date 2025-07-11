import gymnasium as gym
import torch
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.PPO import PPOAgent

def main():
    # 解决OpenMP冲突
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
    
    env = gym.make('LunarLander-v3', render_mode='rgb_array')
    obs, info = env.reset()

    print("环境已重置，初始状态:", obs)
    
    # 使用简化的PPO - 直接传入state_dim和action_dim
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n
    
    MyAgent = PPOAgent(
        input_dim=state_dim,
        output_dim=action_dim,
        lr=0.002,  # 与test.py相同
        gamma=0.99,
    )
    
    print("开始训练...")
    episode_rewards = MyAgent.train(env, episodes=800, print_every=20,update_timestep=2000)
    # 测试智能体
    print("\n开始测试训练后的智能体...")
    env_test = gym.make('LunarLander-v3', render_mode='human')
    for test_episode in range(2):  # 测试3轮
        obs, info = env_test.reset()
        done = False
        total_reward = 0
        steps = 0
        
        while not done:
            # 使用训练好的策略选择动作（贪婪策略）
            with torch.no_grad():
                action_probs = MyAgent.policy_net(torch.FloatTensor(obs))
                action = torch.argmax(action_probs).item()
            
            obs, reward, terminated, truncated, info = env_test.step(action)
            done = terminated or truncated
            total_reward += reward
            steps += 1
            
        print(f"测试第{test_episode + 1}轮: 总奖励 {total_reward:.2f}, 步数 {steps}")

    env_test.close()
if __name__ == "__main__":
    main()