import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import torch.nn.functional as F


class PPOAgent(nn.Module):
    def __init__(self, input_dim, hidden_dim=128, output_dim=2, lr=1e-3, gamma=0.99, clip_epsilon=0.2, gae_lambda=0.95, policy_epochs=10, entropy_coef=0.01, value_coef=0.5):
        super(PPOAgent, self).__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        self.gamma = gamma
        self.clip_epsilon = clip_epsilon
        self.gae_lambda = gae_lambda
        self.policy_epochs = policy_epochs
        self.entropy_coef = entropy_coef
        self.value_coef = value_coef
        
        # 策略网络
        self.policy_net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, output_dim),
            nn.Softmax(dim=-1)
        )
        
        # 价值网络
        self.value_net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1)
        )
        
        self.optimizer = optim.Adam(self.parameters(), lr=lr)
        
        # 临时存储
        self.reset_trajectory()

    def act(self, state):
        # 确保输入是 tensor
        if not isinstance(state, torch.Tensor):
            state = torch.FloatTensor(state)
        action_probs = self.policy_net(state)
        dist = torch.distributions.Categorical(action_probs)
        action = dist.sample()
        log_prob = dist.log_prob(action)

        self.actions.append(action)
        self.log_probs.append(log_prob)
        self.states.append(state)

        return action.item()
    
    def val(self, state, action):
        action_probs = self.policy_net(state)
        dist = torch.distributions.Categorical(action_probs)
        action_log_probs = dist.log_prob(action)
        dist_entropy = dist.entropy()
        state_value = self.value_net(state)

        return action_log_probs, state_value, dist_entropy

    def learn(self):
        """更新策略和价值网络"""
        # 将存储的轨迹转换为 tensor
        returns = []
        discounted_return = 0
        for reward, is_terminal in zip(reversed(self.rewards), reversed(self.dones)):
            if is_terminal:
                discounted_return = 0
            discounted_return = reward + self.gamma * discounted_return
            returns.insert(0, discounted_return)
        returns = torch.FloatTensor(returns)

        #标准化回报
        returns = (returns - returns.mean()) / (returns.std() + 1e-8)

        # 存储老回报
        old_log_probs = torch.stack(self.log_probs).detach()
        old_states = torch.stack(self.states).detach()
        old_actions = torch.stack(self.actions).detach()

        # 更新策略和价值网络
        for _ in range(self.policy_epochs):
            # 计算新策略的 log_prob
            new_log_probs, state_values, dist_entropy = self.val(old_states, old_actions)
            state_values = state_values.squeeze(-1)  # 确保形状为 (N,)
            # 计算优势
            advantages = returns - state_values.detach()

            # 计算损失
            ratio = torch.exp(new_log_probs - old_log_probs)
            surr1 = ratio * advantages
            surr2 = torch.clamp(ratio, 1 - self.clip_epsilon, 1 + self.clip_epsilon) * advantages

            policy_loss = -torch.min(surr1, surr2).mean()
            value_loss = F.mse_loss(state_values, returns)
            
            entropy_loss = dist_entropy.mean()

            loss = policy_loss + self.value_coef * value_loss - self.entropy_coef * entropy_loss

            # 更新网络
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
        self.reset_trajectory()


    def reset_trajectory(self):
        """重置轨迹存储"""
        self.states = []
        self.actions = []
        self.rewards = []
        self.log_probs = []
        self.dones = []


    def train(self, env, episodes=800, print_every=20, update_timestep=1000):#这里为了让参数更新更加稳定所以取一定步数后才进行更新
        """训练循环"""
        episode_rewards = []
        timestep = 0
        for episode in range(episodes):
            state, _ = env.reset()
            done = False
            total_reward = 0
            
            while not done:
                action = self.act(state)
                timestep += 1
                next_state, reward, terminated, truncated, _ = env.step(action)
                done = terminated or truncated
                
                self.rewards.append(reward)
                self.dones.append(done)
                
                state = next_state
                total_reward += reward
                if timestep % update_timestep == 0:
                    self.learn()
                    timestep = 0
            episode_rewards.append(total_reward)
            
            if (episode + 1) % print_every == 0:
                avg_reward = np.mean(episode_rewards[-print_every:])
                print(f"Episode {episode + 1}/{episodes}: Average Reward: {avg_reward:.2f}")
        
        return episode_rewards