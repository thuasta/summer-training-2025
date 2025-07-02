# DQN (Deep Q-Network) 算法学习文档

**作者**: zbs  
**日期**: 2025.7.2
**版本**: v1.0

## DQN 算法概述

DQN (Deep Q-Network) 是由DeepMind在2015年提出的深度强化学习算法，将深度神经网络与Q-Learning结合，成功解决了高维状态空间的强化学习问题。

## 算法原理

### 核心思想
DQN用深度神经网络$Q(s, a; \theta)$来近似Q值函数，其中$\theta$为网络参数。

### 损失函数
$$L(\theta) = E_{(s,a,r,s') \sim D}\left[\left(r + \gamma \max_{a'} Q(s', a'; \theta^-) - Q(s, a; \theta)\right)^2\right]$$

其中：
- $D$: 经验回放缓冲区
- $\theta^-$: 目标网络参数
- $Q(s, a; \theta)$: 主网络Q值

### 梯度更新
$$\nabla_\theta L(\theta) = E_{(s,a,r,s') \sim D}\left[\left(r + \gamma \max_{a'} Q(s', a'; \theta^-) - Q(s, a; \theta)\right) \nabla_\theta Q(s, a; \theta)\right]$$

## DQN vs Q-Learning

### 关键差异

| 特性 | DQN | Q-Learning |
|------|-----|------------|
| **函数近似** | 深度神经网络 | 查表法 |
| **状态空间** | 高维连续 | 离散有限 |
| **经验回放** | 必需 | 可选 |
| **目标网络** | 使用 | 不需要 |
| **收敛性** | 近似收敛 | 理论保证收敛 |

### 数学比较

**Q-Learning更新**：
$$Q(s, a) \leftarrow Q(s, a) + \alpha[r + \gamma \max_{a'} Q(s', a') - Q(s, a)]$$

**DQN更新**：
$$\theta \leftarrow \theta - \alpha \nabla_\theta L(\theta)$$

## DQN的关键技术

### 1. 经验回放 (Experience Replay)

**原理**: 存储转移$(s_t, a_t, r_t, s_{t+1})$到缓冲区$D$，随机采样进行训练。

**优势**:
- 打破数据时序相关性
- 提高样本效率
- 稳定训练过程

**数学表示**:
$$D = \{(s_i, a_i, r_i, s_{i+1})\}_{i=1}^N$$

每次从$D$中随机采样batch进行更新。

### 2. 目标网络 (Target Network)

**原理**: 使用独立的目标网络$Q(s, a; \theta^-)$计算目标值。

**更新策略**:
$$\theta^- \leftarrow \tau \theta + (1-\tau) \theta^-$$

或每$C$步硬更新：
$$\theta^- \leftarrow \theta$$

**稳定性分析**: 目标网络减少了目标值的变化，避免了"追逐移动目标"的问题。

### 3. 网络架构

**典型结构**:
```
输入层 → 卷积层 → 全连接层 → 输出层(动作数量)
    |         |        |           |
    s      特征提取   状态表示    Q(s,a)
```

**输出**: 对于每个动作$a_i$，输出$Q(s, a_i)$



## 收敛性与稳定性

### 训练不稳定性来源

1. **移动目标问题**: 主网络更新导致目标值变化
2. **样本相关性**: 连续样本高度相关
3. **灾难性遗忘**: 网络忘记之前学到的经验

### 解决方案数学分析

**目标网络稳定性**:
设$\Delta Q = Q(s', a'; \theta) - Q(s', a'; \theta^-)$，则目标值方差：
$$\text{Var}(Y_t) = \text{Var}(r_t) + \gamma^2 \text{Var}(\max_{a'} Q(s_{t+1}, a'; \theta^-))$$

目标网络使$\text{Var}(\max_{a'} Q(s_{t+1}, a'; \theta^-))$在训练期间保持相对稳定。

## DQN变体与改进

### Double DQN
解决过估计问题：
$$Y_t^{DoubleDQN} = r_t + \gamma Q(s_{t+1}, \arg\max_{a'} Q(s_{t+1}, a'; \theta_t); \theta_t^-)$$

### Dueling DQN
分解Q值为状态价值和优势函数：
$$Q(s, a) = V(s) + A(s, a) - \frac{1}{|A|}\sum_{a'} A(s, a')$$

### Prioritized Experience Replay
根据TD误差优先采样：
$$P(i) = \frac{p_i^\alpha}{\sum_k p_k^\alpha}$$

其中$p_i = |\delta_i| + \epsilon$，$\delta_i$为TD误差。

## 实现要点

### 网络初始化
```python
def init_weights(layer):
        if type(layer) == nn.Linear:
                torch.nn.init.xavier_uniform_(layer.weight)
                layer.bias.data.fill_(0.0)
```

### 损失函数实现
```python
def compute_loss(batch):
        states, actions, rewards, next_states, dones = batch
        
        current_q = main_net(states).gather(1, actions)
        next_q = target_net(next_states).max(1)[0].detach()
        target_q = rewards + gamma * next_q * (1 - dones)
        
        return F.mse_loss(current_q.squeeze(), target_q)
```

## 超参数调优

### 关键超参数

| 参数 | 符号 | 推荐值 | 说明 |
|------|------|--------|------|
| 学习率 | $\alpha$ | 1e-4 | Adam优化器学习率 |
| 批大小 | batch_size | 32-128 | 经验回放批大小 |
| 缓冲区大小 | $|D|$ | 10000-1M | 根据内存调整 |
| 目标更新频率 | $C$ | 1000-10000 | 步数或episode |
| 折扣因子 | $\gamma$ | 0.99 | 长期奖励权重 |

### 训练监控指标

1. **平均奖励**: 评估策略性能
2. **Q值变化**: 监控学习进度  
3. **损失函数**: 观察训练稳定性
4. **探索率**: $\epsilon$衰减情况

## 应用与局限

### 成功应用
- **Atari游戏**: 原始DQN的成功案例
- **连续控制**: 结合其他技术
- **推荐系统**: 离散动作空间

### 局限性

1. **样本效率**: 需要大量样本
2. **连续动作**: 原始DQN不适用
3. **部分可观测**: 需要循环网络扩展
4. **多智能体**: 环境非平稳性

## 思考题

### 为什么DQN需要经验回放？

**数学分析**：
在线学习的样本相关性导致梯度估计偏差：
$$E[\nabla_\theta L(\theta)] \neq \nabla_\theta E[L(\theta)]$$

经验回放通过随机采样打破相关性，使梯度估计更准确：
$$\nabla_\theta L(\theta) \approx \frac{1}{B} \sum_{i=1}^B \nabla_\theta l_i(\theta)$$

其中$l_i(\theta)$为单个样本损失，$B$为批大小。

### 为什么需要目标网络？

**不稳定性证明**：
不使用目标网络时，目标值为：
$$Y_t = r_t + \gamma \max_{a'} Q(s_{t+1}, a'; \theta_t)$$

参数$\theta_t$同时影响当前估计和目标，导致：
$$\frac{\partial Y_t}{\partial \theta_t} \neq 0$$

这违背了监督学习中"标签固定"的假设，导致训练不稳定。

*最后更新: 2025-07-2*