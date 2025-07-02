import numpy as np
import matplotlib.pyplot as plt

class SarsaAgent:
    def __init__(self, obs_n , act_n , alpha=0.025, gamma=0.4, epsilon=0.001):
        self.obs_n = obs_n
        self.act_n = act_n
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_initial = epsilon  # 保存初始探索率
        self.q_table = np.zeros((obs_n, act_n))

    def choose_action(self, state):
        if np.random.uniform(0, 1) < self.epsilon:
            return np.random.choice(self.act_n)
        else:
            return np.argmax(self.q_table[state])
    

    def learn(self, state, action, reward, next_state, next_action):
        q_predict = self.q_table[state, action]
        if next_state is not None:
            q_target = reward + self.gamma * self.q_table[next_state, next_action]
        else:
            q_target = reward
        self.q_table[state, action] += self.alpha * (q_target - q_predict)

    def train(self, env, episodes=1000, print_every=100):
        episode_rewards = []
        
        for episode in range(episodes):            
            state, _ = env.reset()
            action = self.choose_action(state)
            done = False
            total_reward = 0
            steps = 0
            max_steps = 1000  # 防止无限循环
            
            while not done and steps < max_steps:
                next_state, reward, terminated, truncated, _ = env.step(action)
                next_action = self.choose_action(next_state)
                
                self.learn(state, action, reward, next_state, next_action)
                
                state = next_state
                action = next_action
                total_reward += reward
                steps += 1
                
                if terminated or truncated:
                    done = True
            
            episode_rewards.append(total_reward)
            
            # 只在指定的间隔打印进度
            if (episode + 1) % print_every == 0:
                avg_reward = np.mean(episode_rewards[-print_every:])
                print(f"Episode {episode + 1}/{episodes}: 平均奖励 {avg_reward:.2f}")
        
        final_avg = np.mean(episode_rewards[-100:])

        print(f"训练完成！最后100个episode的平均奖励: {final_avg:.2f}")
        return episode_rewards
    
    def save_policy(self, filename):
        np.save(filename, self.q_table)

    def play_episode(self, env):
        state, _ = env.reset()
        done = False
        total_reward = 0
        steps = 0
        max_steps = 1000
        
        print("开始演示学习到的策略...")
        env.render()  # 显示初始状态
        
        while not done and steps < max_steps:
            # 使用贪婪策略
            action = np.argmax(self.q_table[state])
            next_state, reward, terminated, truncated, _ = env.step(action)
            
            action_names = ['上', '右', '下', '左']
            print(f"步骤 {steps + 1}: 动作={action_names[action]}, 奖励={reward}")
            
            total_reward += reward
            state = next_state
            steps += 1
            
            # 添加小延迟以便观察
            import time
            time.sleep(0.5)
            
            if terminated or truncated:
                done = True
        
        print(f"演示结束！总奖励: {total_reward}, 步数: {steps}")
        return total_reward
    
    def plot_reward(self, episode_rewards):
        
        plt.plot(episode_rewards)
        plt.xlabel('Episode')
        plt.ylabel('Total Reward')
        plt.title('Training Progress')
        plt.grid()
        plt.show()
    
