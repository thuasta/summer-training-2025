# 强化学习 (Reinforcement Learning) 学习文档

**作者**: zbs  
**日期**: 2025.6.30  
**版本**: v1.0
## SARSA 算法
## 项目概述

本项目实现了SARSA算法来解决CliffWalking环境，并包含了线性探索率衰减等优化技术。

## 文件结构

```
rl/
├── sarsa.py              # SARSA算法实现
├── cliffwalking.py       # CliffWalking环境训练脚本
├── cliffwalking_explained.py  # 环境详细说明
└── rl.md                 # 本文档
```

## CliffWalking 环境

### 环境描述
CliffWalking是一个经典的强化学习环境，智能体需要从起始位置(S)到达目标位置(T)，同时避开悬崖(C)。

```
o  o  o  o  o  o  o  o  o  o  o  o
o  o  o  o  o  o  o  o  o  o  o  o
o  o  o  o  o  o  o  o  o  o  o  o
S  C  C  C  C  C  C  C  C  C  C  T
```

### 状态空间与动作空间
- **状态空间**: 48个离散状态 (4×12网格)
- **动作空间**: 4个动作 (上、右、下、左)
- **奖励机制**:
  - 到达目标: 0
  - 掉入悬崖: -100 (重置到起始位置)
  - 其他移动: -1


### 算法原理
SARSA (State-Action-Reward-State-Action) 是一种on-policy的时序差分学习算法。

#### 更新公式
$$Q(s_t, a_t) \leftarrow Q(s_t, a_t) + \alpha[r_{t+1} + \gamma Q(s_{t+1}, a_{t+1}) - Q(s_t, a_t)]$$

其中:
- $Q(s_t, a_t)$: 时刻$t$状态$s_t$下动作$a_t$的Q值
- $\alpha$: 学习率 (learning rate), $\alpha \in (0, 1]$
- $\gamma$: 折扣因子 (discount factor), $\gamma \in [0, 1]$
- $r_{t+1}$: 即时奖励
- $s_{t+1}$: 下一状态
- $a_{t+1}$: 下一动作 (由当前策略选择)

#### SARSA算法流程
1. 初始化Q表: $Q(s,a) = 0, \forall s \in S, a \in A$
2. 对于每个episode:
   - 初始化$s_0$，选择$a_0 \sim \pi(a|s_0)$
   - 对于每个时间步$t$:
     - 执行$a_t$，观察$r_{t+1}, s_{t+1}$
     - 选择$a_{t+1} \sim \pi(a|s_{t+1})$ (使用$\epsilon$-贪婪策略)
     - 更新: $Q(s_t, a_t) \leftarrow Q(s_t, a_t) + \alpha[r_{t+1} + \gamma Q(s_{t+1}, a_{t+1}) - Q(s_t, a_t)]$
     - $s_t \leftarrow s_{t+1}, a_t \leftarrow a_{t+1}$
   - 直到$s_t$为终止状态
#### $\epsilon$-贪婪策略
$$\pi(a|s) = \begin{cases}
1 - \epsilon + \frac{\epsilon}{|A|} & \text{if } a = \arg\max_{a'} Q(s, a') \\
\frac{\epsilon}{|A|} & \text{otherwise}
\end{cases}$$

其中$|A|$是动作空间大小。

### Q表 (Q-table)

Q表是一个二维数组，存储每个状态-动作对的价值估计:
- 维度: $[|S|, |A|] = [48, 4]$
- $Q[s, a]$ = 在状态$s$下执行动作$a$的期望累积奖励

#### Q表的数学表示
$$Q^{\pi}(s, a) = E_{\pi}\left[\sum_{k=0}^{\infty} \gamma^k r_{t+k+1} \mid s_t = s, a_t = a\right]$$

#### Q表的作用
1. **价值估计**: 评估每个状态-动作对的长期价值
2. **策略提取**: 选择Q值最大的动作作为最优动作
   $$\pi^*(s) = \arg\max_a Q^*(s, a)$$
3. **学习存储**: 保存智能体的学习经验

## 探索与利用权衡

### 固定探索率 vs 衰减探索率

| 策略类型 | 优点 | 缺点 | 适用场景 |
|---------|------|------|----------|
| 固定探索率 | 简单稳定 | 训练后期仍在探索 | 环境变化的情况 |
| 线性衰减 | 早期探索，后期利用 | 可能过早停止探索 | 静态环境 |

### 线性探索率衰减实现

线性衰减公式：
$$\epsilon_t = \max\left(\epsilon_{\min}, \epsilon_0 \cdot \left(1 - \frac{t}{T}\right)\right)$$

其中：
- $\epsilon_t$: 第$t$个episode的探索率
- $\epsilon_0$: 初始探索率
- $\epsilon_{\min}$: 最小探索率
- $T$: 总训练episode数

```python
def update_epsilon(self, episode, total_episodes):
    if self.epsilon_decay:
        decay_rate = episode / total_episodes
        self.epsilon = max(
            self.epsilon_min, 
            self.epsilon_initial * (1 - decay_rate)
        )
```

### 参数调优建议

1. **学习率 ($\alpha$)**: 
   - 范围: $\alpha \in [0.01, 0.3]$
   - 较大值: 快速学习，但可能不稳定
   - 较小值: 稳定学习，但收敛慢
   - 推荐: $\alpha = 0.1$

2. **折扣因子 ($\gamma$)**:
   - 范围: $\gamma \in [0.9, 0.99]$
   - 接近1: 重视长期奖励
   - 接近0: 重视即时奖励
   - 推荐: $\gamma = 0.9$ (CliffWalking)

3. **探索率 ($\epsilon$)**:
   - 初始值: $\epsilon_0 \in [0.1, 0.3]$
   - 最小值: $\epsilon_{\min} \in [0.01, 0.05]$
   - 使用衰减可提高最终性能

#### 收敛条件
Q表收敛的数学条件：
$$\lim_{t \to \infty} |Q_t(s,a) - Q_{t-1}(s,a)| = 0, \quad \forall s,a$$

## 训练结果分析

### 性能指标
- **收敛速度**: 达到稳定性能需要的episode数
- **最终性能**: 最后100个episode的平均奖励
- **策略质量**: 使用贪婪策略的测试结果



## 使用示例

### 基础训练
```python
from sarsa import SarsaAgent
import gymnasium as gym

env = gym.make('CliffWalking-v0')
agent = SarsaAgent(obs_n=48, act_n=4)
episode_rewards = agent.train(env, episodes=1000)
```


### 策略可视化
```python
agent.visualize_policy()        # 显示学习到的策略
agent.print_q_values_sample()   # 显示关键位置Q值
```

## 思考题

### 无法到达最优解

**问题**: 只要$\epsilon > 0$，就到达不了最优解，请你思考为什么？

**数学分析**:

当$\epsilon > 0$时，智能体仍有概率选择非贪婪动作：
$$P(\text{选择非最优动作}) = \frac{\epsilon}{|A|} > 0$$

因此，即使Q表完全收敛，策略仍然是随机的：
$$\pi_{\epsilon}(a^*|s) = 1 - \epsilon + \frac{\epsilon}{|A|} < 1$$

其中$a^* = \arg\max_a Q(s,a)$是最优动作。

**解决方案**:
1. **训练时**: 使用$\epsilon$-贪婪探索
2. **测试时**: 使用纯贪婪策略 ($\epsilon = 0$)
3. **渐进衰减**: $\lim_{t \to \infty} \epsilon_t = 0$


*最后更新: 2025-06-30*
