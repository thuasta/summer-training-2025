import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.optim as optim

class PGAgent(nn.Module):
    def __init__(self, input_dim, output_dim, hidden_dim=128, lr=2e-3, gamma=0.8):
        super(PGAgent, self).__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        self.gamma = gamma
    
        self.policy_net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.Dropout(0.4),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
            nn.Softmax(dim=1)
        )
        
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)
        self.reset_trajectory()

    def forward(self, state):
        state = torch.FloatTensor(state).unsqueeze(0)
        action_probs = self.policy_net(state)
        return action_probs
    
    def reset_trajectory(self):
        """重置轨迹存储"""
        self.states = []
        self.actions = []
        self.rewards = []
        self.log_probs = []
    
    def choose_action(self, state):
        """选择动作并返回动作和对数概率"""
        action_probs = self.forward(state)
        m = torch.distributions.Categorical(action_probs)
        action = m.sample()
        log_prob = m.log_prob(action)
        return action.item(), log_prob
    
    def learn(self):
        """学习函数"""
        if len(self.rewards) == 0:
            return 0.0
            
        # 计算折扣回报
        returns = []
        R = 0
        for r in reversed(self.rewards):
            R = r + self.gamma * R
            returns.insert(0, R)
        returns = torch.tensor(returns)
        
        eps = np.finfo(np.float64).eps.item()
        returns = (returns - returns.mean()) / (returns.std() + eps)

#这里我用stack转换tensor导致训练失败 debug半小时 纯逆天 读者可以考虑一下为啥
        log_probs = torch.cat(self.log_probs)# 将 log_probs 转换为张量

        print(f"log_probs: {log_probs.shape}")
        loss = -(log_probs * returns).sum()


        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        return loss.item()

    def train(self, env, episodes=1000, print_every=100):
        episode_rewards = []
        episode_losses = []
        
        for episode in range(episodes):
            self.reset_trajectory()
            state, _ = env.reset()
            done = False
            total_reward = 0
            
            while not done:
                # 选择动作
                action, log_prob = self.choose_action(state)
                
                # 执行动作
                next_state, reward, terminated, truncated, _ = env.step(action)
                
                # 存储轨迹
                self.states.append(state)
                self.actions.append(action)
                self.rewards.append(reward)
                self.log_probs.append(log_prob)
                
                state = next_state
                total_reward += reward
                
                if terminated or truncated:
                    done = True
            
            # 每个episode结束后进行学习更新
            loss = self.learn()
            episode_rewards.append(total_reward)
            episode_losses.append(loss)
            
            if (episode + 1) % print_every == 0:
                avg_reward = np.mean(episode_rewards[-print_every:])
                avg_loss = np.mean(episode_losses[-print_every:])
                max_reward = np.max(episode_rewards[-print_every:])
                min_reward = np.min(episode_rewards[-print_every:])
                std_reward = np.std(episode_rewards[-print_every:])
                print(f"Episode {episode + 1}/{episodes}: 平均奖励 {avg_reward:.2f}±{std_reward:.2f} (范围: {min_reward:.0f}-{max_reward:.0f}), 损失 {avg_loss:.6f}")
                
                # 早停机制
                if avg_reward >= 200:
                    break
        
        return episode_rewards, episode_losses
