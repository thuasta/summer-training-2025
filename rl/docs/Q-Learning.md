# Q-Learning 算法学习文档

**作者**: zbs  
**日期**: 2025.6.30  
**版本**: v1.0

## Q-Learning 算法概述

Q-Learning是一种**off-policy**的时序差分学习算法，由Watkins于1989年提出。它能够学习最优策略而无需遵循当前策略。

## 算法原理

### 核心更新公式
$$Q(s_t, a_t) \leftarrow Q(s_t, a_t) + \alpha[r_{t+1} + \gamma \max_{a'} Q(s_{t+1}, a') - Q(s_t, a_t)]$$

其中：
- $Q(s_t, a_t)$: 状态-动作价值函数
- $\alpha$: 学习率，$\alpha \in (0, 1]$
- $\gamma$: 折扣因子，$\gamma \in [0, 1]$
- $r_{t+1}$: 即时奖励
- $\max_{a'} Q(s_{t+1}, a')$: 下一状态的最大Q值

### 贝尔曼最优方程
Q-Learning收敛到贝尔曼最优方程的解：
$$Q^*(s, a) = E\left[r + \gamma \max_{a'} Q^*(s', a') \mid s, a\right]$$

### 算法流程
1. 初始化Q表：$Q(s,a) = 0, \forall s \in S, a \in A$
2. 对于每个episode：
   - 初始化状态$s_0$
   - 对于每个时间步$t$：
     - 用$\epsilon$-贪婪策略选择动作$a_t$
     - 执行$a_t$，观察$r_{t+1}, s_{t+1}$
     - 更新：$Q(s_t, a_t) \leftarrow Q(s_t, a_t) + \alpha[r_{t+1} + \gamma \max_{a'} Q(s_{t+1}, a') - Q(s_t, a_t)]$
     - $s_t \leftarrow s_{t+1}$
   - 直到$s_t$为终止状态

## Q-Learning vs SARSA

### 关键差异

| 特性 | Q-Learning | SARSA |
|------|------------|-------|
| **学习类型** | Off-policy | On-policy |
| **更新目标** | $\max_{a'} Q(s', a')$ | $Q(s', a')$ (实际选择的动作) |
| **策略** | 学习最优策略 | 学习当前策略 |
| **收敛性** | 收敛到最优Q值 | 收敛到当前策略的Q值 |
| **探索影响** | 不受探索策略影响 | 受探索策略影响 |

### 数学比较

**Q-Learning更新**：
$$Q(s, a) \leftarrow Q(s, a) + \alpha[r + \gamma \max_{a'} Q(s', a') - Q(s, a)]$$

**SARSA更新**：
$$Q(s, a) \leftarrow Q(s, a) + \alpha[r + \gamma Q(s', a') - Q(s, a)]$$

关键在于$\max_{a'} Q(s', a')$ vs $Q(s', a')$

## CliffWalking环境中的表现

### 行为差异
在CliffWalking环境中：

- **Q-Learning**: 学习最优路径（沿悬崖边缘），因为它忽略探索风险
- **SARSA**: 学习安全路径（远离悬崖），因为它考虑探索时的风险

### 数学解释
设悬崖边缘状态为$s_{cliff}$：

**Q-Learning**: 
$$Q^*(s_{cliff}, a_{right}) = -1 + \gamma \cdot 0 = -1$$
（假设最优路径）

**SARSA**: 
$$Q^{\pi_\epsilon}(s_{cliff}, a_{right}) = -1 + \gamma \left[(1-\epsilon)(-1) + \epsilon(-100)\right]$$
（考虑探索风险）

## 收敛性分析

### 收敛条件
Q-Learning在以下条件下收敛到最优解：

1. **有限状态-动作空间**
2. **所有状态-动作对被无限次访问**：
   $$\sum_{t=0}^{\infty} \mathbb{I}(s_t=s, a_t=a) = \infty, \quad \forall s,a$$
3. **学习率满足Robbins-Monro条件**：
   $$\sum_{t=0}^{\infty} \alpha_t = \infty, \quad \sum_{t=0}^{\infty} \alpha_t^2 < \infty$$

### 最优性定理
**定理**: 在上述条件下，Q-Learning算法收敛到最优Q函数$Q^*$：
$$\lim_{t \to \infty} Q_t(s,a) = Q^*(s,a), \quad \forall s,a$$

## 实现要点

### $\epsilon$-贪婪策略
$$\pi_\epsilon(a|s) = \begin{cases}
1 - \epsilon + \frac{\epsilon}{|A|} & \text{if } a = \arg\max_{a'} Q(s, a') \\
\frac{\epsilon}{|A|} & \text{otherwise}
\end{cases}$$

### 探索率衰减
$$\epsilon_t = \max\left(\epsilon_{\min}, \epsilon_0 \cdot \lambda^t\right)$$

其中$\lambda \in (0, 1)$是衰减率。

### 伪代码
```python
def q_learning_update(self, state, action, reward, next_state, done):
    if done:
        target = reward
    else:
        target = reward + self.gamma * np.max(self.q_table[next_state])
    
    self.q_table[state, action] += self.alpha * (target - self.q_table[state, action])
```

## 参数调优

### 超参数指导

| 参数 | 符号 | 推荐值 | 说明 |
|------|------|--------|------|
| 学习率 | $\alpha$ | 0.1-0.5 | Q-Learning对学习率不如SARSA敏感 |
| 折扣因子 | $\gamma$ | 0.9-0.99 | 高$\gamma$学习长期策略 |
| 初始探索率 | $\epsilon_0$ | 0.1-0.3 | 平衡探索与利用 |
| 最小探索率 | $\epsilon_{\min}$ | 0.01 | 保持少量探索 |

### 调优策略
1. **先调$\alpha$**: 观察收敛速度
2. **再调$\gamma$**: 影响长期vs短期权衡
3. **最后调$\epsilon$**: 平衡探索与利用

## 扩展与改进

### Double Q-Learning
解决Q-Learning的过估计问题：
$$Q_1(s, a) \leftarrow Q_1(s, a) + \alpha[r + \gamma Q_2(s', \arg\max_{a'} Q_1(s', a')) - Q_1(s, a)]$$

### 经验回放
存储$(s, a, r, s')$四元组，随机采样更新：
- 打破数据相关性
- 提高样本效率

## 思考题

### 为什么Q-Learning是off-policy？

**数学分析**：
Q-Learning的更新使用$\max_{a'} Q(s', a')$，这与实际执行的策略无关。即使用$\epsilon$-贪婪策略探索，学习的仍是贪婪策略的价值。

**证明**：
设行为策略为$\mu(a|s)$，目标策略为$\pi(a|s) = \arg\max_a Q(s,a)$，则：
$$E_\mu[r + \gamma \max_{a'} Q(s', a')] = E_\pi[r + \gamma Q(s', \pi(s'))]$$

因此Q-Learning学习的是最优策略$\pi^*$的价值，而非行为策略$\mu$的价值。

*最后更新: 2025-06-30*
