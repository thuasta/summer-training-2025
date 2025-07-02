# 策略梯度 (Policy Gradient) 学习文档

**作者**: zbs  
**日期**: 2025.6.30  
**版本**: v1.0



## 策略梯度（Policy Gradient）算法

### 算法原理
策略梯度方法直接优化策略函数，而不是价值函数。通过梯度上升来最大化期望回报。

#### 基本思想
- 直接参数化策略 π(a|s;θ)
- 通过梯度上升优化策略参数 θ
- 目标：最大化期望累积奖励 J(θ)

### 核心公式

#### 策略梯度定理
$$\nabla J(\theta) = E_{\tau \sim p(\tau|\theta)}\left[\sum_{t=0}^{T-1} \nabla \log \pi_\theta(a_t|s_t) \cdot Q^{\pi_\theta}(s_t,a_t)\right]$$

这个式子从何而来呢？

![把p展开](figs/3-1.png)

![得到](figs/3-2.png)

#### 更新公式
本质是梯度更新，希望参数能够做到：
$$\arg\max_\theta E_{\tau \sim p(\tau|\theta)}[R(\tau)]$$

那下面这个式子就不难理解了，直接类比梯度上升：
$$\theta \leftarrow \theta + \alpha \cdot \nabla \log \pi_\theta(a_t|s_t) \cdot G_t$$

其中:
- $\theta$: 策略参数
- $\alpha$: 学习率  
- $G_t$: 从时刻$t$开始的累积回报，$G_t = \sum_{k=0}^{T-t-1} \gamma^k r_{t+k+1}$
- $\pi_\theta(a_t|s_t)$: 参数化策略

#### 轨迹概率分解
轨迹$\tau = (s_0, a_0, r_0, s_1, a_1, r_1, \ldots, s_T)$的概率为：
$$p(\tau|\theta) = \rho_0(s_0) \prod_{t=0}^{T-1} \pi_\theta(a_t|s_t) P(s_{t+1}|s_t, a_t)$$

其中：
- $\rho_0(s_0)$: 初始状态分布
- $P(s_{t+1}|s_t, a_t)$: 环境转移概率（与$\theta$无关）

## REINFORCE算法

### 算法特点
- **蒙特卡洛方法**: 使用完整episode计算回报
- **无偏估计**: 使用真实回报$G_t$
- **高方差**: 需要方差减少技术

### 核心更新公式
$$\theta \leftarrow \theta + \alpha \sum_{t=0}^{T-1} \nabla \log \pi_\theta(a_t|s_t) \cdot G_t$$

### 算法流程
1. 初始化策略参数$\theta$
2. 对于每个episode:
   - 使用当前策略$\pi_\theta$生成轨迹$\tau$
   - 计算每步的累积回报$G_t = \sum_{k=t}^{T-1} \gamma^{k-t} r_{k+1}$
   - 更新策略参数：$\theta \leftarrow \theta + \alpha \sum_{t=0}^{T-1} \nabla \log \pi_\theta(a_t|s_t) \cdot G_t$
3. 重复直到收敛

## 方差减少技术实现（编程作业）

### 基线 (Baseline) 模型

#### 1. 无基线REINFORCE
$$\nabla J(\theta) = E\left[\sum_{t=0}^{T-1} \nabla \log \pi_\theta(a_t|s_t) \cdot G_t\right]$$

#### 2. 带基线的REINFORCE  
$$\nabla J(\theta) = E\left[\sum_{t=0}^{T-1} \nabla \log \pi_\theta(a_t|s_t) \cdot (G_t - b(s_t))\right]$$

其中$b(s_t)$是基线函数，常用选择：
- **状态价值基线**: $b(s_t) = V^{\pi_\theta}(s_t)$
- **平均回报基线**: $b(s_t) = \frac{1}{N}\sum_{i=1}^{N} G_t^{(i)}$

#### 3. Actor-Critic方法
使用优势函数$A^{\pi_\theta}(s_t, a_t) = Q^{\pi_\theta}(s_t, a_t) - V^{\pi_\theta}(s_t)$：
$$\nabla J(\theta) = E\left[\sum_{t=0}^{T-1} \nabla \log \pi_\theta(a_t|s_t) \cdot A^{\pi_\theta}(s_t, a_t)\right]$$

| 技术 | 公式 | 优点 | 缺点 |
|------|------|------|------|
| 无基线 | $G_t$ | 简单直接，无偏估计 | 方差大，收敛慢 |
| 状态价值基线 | $G_t - V(s_t)$ | 显著减少方差 | 需要额外估计$V(s)$ |
| 平均回报基线 | $G_t - \bar{G}$ | 实现简单 | 效果有限 |
| Actor-Critic | $r + \gamma V(s') - V(s)$ | 方差小，样本效率高 | 有偏估计 |


### 或者你能想到的其他技术方案

#### 4. 回报标准化
$$G_t^{normalized} = \frac{G_t - \mu_G}{\sigma_G + \epsilon}$$
其中$\mu_G$和$\sigma_G$分别是当前batch回报的均值和标准差。

#### 5. 重要性采样 (Importance Sampling)
用于off-policy学习：
$$\nabla J(\theta) = E_{\tau \sim \pi_{old}}\left[\frac{\pi_\theta(\tau)}{\pi_{old}(\tau)} \sum_{t=0}^{T-1} \nabla \log \pi_\theta(a_t|s_t) \cdot G_t\right]$$

## 参数调优

### 关键超参数

| 参数 | 符号 | 推荐范围 | 影响 |
|------|------|----------|------|
| 学习率 | $\alpha$ | $10^{-4} \sim 10^{-2}$ | 收敛速度与稳定性 |
| 折扣因子 | $\gamma$ | $0.9 \sim 0.999$ | 长期vs短期奖励权衡 |
| 批大小 | $N$ | $32 \sim 512$ | 梯度估计质量 |
| 网络结构 | - | $64 \sim 512$ hidden | 表达能力vs过拟合 |

### 调优策略
1. **学习率**: 从大到小逐步调整，观察损失曲线
2. **网络结构**: 简单任务用小网络，复杂任务适当增大
3. **正则化**: 适当使用Dropout和权重衰减
4. **梯度裁剪**: 防止梯度爆炸，通常设为$0.5 \sim 2.0$


## 与价值方法的比较

| 特性 | 策略梯度 | 价值方法 |
|------|----------|----------|
| 学习目标 | 直接优化策略 | 学习价值函数 |
| 连续动作 | 天然支持 | 需要特殊处理 |
| 收敛保证 | 局部最优 | 可能发散 |
| 样本效率 | 较低 | 较高 |
| 随机策略 | 支持 | 需要额外技巧 |


*最后更新: 2025-06-30*