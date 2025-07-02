import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt

class DQN:
    """简化版DQN，专门用于离散小状态空间问题"""
    
    def __init__(self, obs_n, act_n, learning_rate=0.01, gamma=0.99, epsilon=0.1):
        self.obs_n = obs_n
        self.act_n = act_n
        self.gamma = gamma
        self.epsilon = epsilon
        
        #TODO: 使用更复杂的网络结构,试试效果为什么会差
        # self.net = nn.Sequential(
        #     nn.Linear(obs_n, 32),
        #     nn.ReLU(),
        #     nn.Linear(32, act_n)
        # )
        self.net = nn.Linear(obs_n, act_n)  # 简化为单层线性网络
        self.optimizer = optim.Adam(self.net.parameters(), lr=learning_rate)
        self.loss_fn = nn.MSELoss()
    
    def state_to_onehot(self, state):
        onehot = torch.zeros(self.obs_n)
        onehot[int(state)] = 1.0
        return onehot
    
    def action(self, state, epsilon=None):
        if epsilon is None:
            epsilon = self.epsilon
            
        if np.random.rand() < epsilon:
            return np.random.randint(self.act_n)
        else:
            with torch.no_grad():
                state_tensor = self.state_to_onehot(state)
                q_values = self.net(state_tensor)
                return q_values.argmax().item()
    
    def learn(self, state, action, reward, next_state, done, gamma=None):
        if gamma is None:
            gamma = self.gamma
            
        state_tensor = self.state_to_onehot(state)
        next_state_tensor = self.state_to_onehot(next_state)
        
        current_q = self.net(state_tensor)[action]
        
        with torch.no_grad():
            next_q = self.net(next_state_tensor).max()
            target = reward + (1 - done) * gamma * next_q
        
        loss = self.loss_fn(current_q, target)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
    
    def train(self, env, episode=1000, epsilon=None, gamma=None, print_every=100):
        if epsilon is None:
            epsilon = 0.9
        if gamma is None:
            gamma = self.gamma
            
        episode_rewards = []
        epsilon_decay = 0.995
        epsilon_min = 0.01
        
        for ep in range(episode):
            state = env.reset()
            if isinstance(state, tuple):
                state = state[0]
                
            total_reward = 0
            for step in range(200):
                action = self.action(state, epsilon)
                result = env.step(action)
                
                if len(result) == 4:
                    next_state, reward, done, info = result
                else:
                    next_state, reward, terminated, truncated, info = result
                    done = terminated or truncated
                    
                self.learn(state, action, reward, next_state, done, gamma)
                state = next_state
                total_reward += reward
                
                if done:
                    break
            
            epsilon = max(epsilon_min, epsilon * epsilon_decay)
            episode_rewards.append(total_reward)
            
            if (ep + 1) % print_every == 0:
                avg_reward = np.mean(episode_rewards[-50:])
                print(f"Episode {ep + 1}, Avg Reward: {avg_reward:.2f}")
        
        return episode_rewards
    
    def plot_reward(self, episode_rewards):
        plt.figure(figsize=(10, 6))
        plt.plot(episode_rewards)
        plt.xlabel('Episode')
        plt.ylabel('Total Reward')
        plt.title('Simple DQN Training Results')
        plt.grid(True)
        plt.show()
    
    def play_episode(self, env):
        state, _ = env.reset()
        total_reward = 0
        steps = 0
        
        while steps < 1000:
            action = self.action(state, epsilon=0.0)
            next_state, reward, terminated, truncated, _ = env.step(action)
            total_reward += reward
            state = next_state
            steps += 1
            
            if terminated or truncated:
                break
        
        print(f"演示结束！总奖励: {total_reward}, 步数: {steps}")
        return total_reward