import gymnasium as gym
import numpy as np
import argparse
import sys
from ..algorithms.sarsa import SarsaAgent
from ..algorithms.Qlr import QAgent
from ..algorithms.DQN import DQN
def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='CliffWalking 强化学习训练')
    parser.add_argument('--algorithm', '-a', 
                       choices=['sarsa', 'qlearning', 'dqn'], 
                       default='sarsa',
                       help='选择算法: sarsa, qlearning 或 dqn (默认: sarsa)')
    parser.add_argument('--episodes', '-e', 
                       type=int, 
                       default=2000,
                       help='训练回合数 (默认: 1000)')
    parser.add_argument('--epsilon', 
                       type=float, 
                       default=0.5,
                       help='探索率 (默认: 0.05)')
    parser.add_argument('--alpha', 
                       type=float, 
                       default=0.1,
                       help='学习率 (默认: 0.1)')
    parser.add_argument('--gamma', 
                       type=float, 
                       default=0.99,
                       help='折扣因子 (默认: 0.99)')

    args = parser.parse_args()
    
    # 训练时不需要渲染，速度更快
    env_train = gym.make('CliffWalking-v0')
    # 测试时使用图形渲染
    env_test = gym.make('CliffWalking-v0', render_mode='human')


    # 根据用户选择创建智能体
    if args.algorithm == 'sarsa':
        print("使用 SARSA 算法")
        MyAgent = SarsaAgent(
            obs_n=env_train.observation_space.n, 
            act_n=env_train.action_space.n,
            alpha=args.alpha,
            gamma=args.gamma,
            epsilon=args.epsilon,
        )
    elif args.algorithm == 'qlearning':
        print("⚡ 使用 Q-Learning 算法")
        MyAgent = QAgent(
            obs_n=env_train.observation_space.n, 
            act_n=env_train.action_space.n,
            alpha=args.alpha,
            gamma=args.gamma,
            epsilon=args.epsilon
        )
    elif args.algorithm == 'dqn':
        print("🧠 使用 DQN 算法")
        MyAgent = DQN(
            obs_n=env_train.observation_space.n,  # 统一使用obs_n
            act_n=env_train.action_space.n,       # 统一使用act_n
            learning_rate=args.alpha,
            gamma=args.gamma,
            epsilon=args.epsilon
        )
    
    print("开始训练...")
    # 使用无渲染环境进行快速训练
    if args.algorithm == 'dqn':
        episode_rewards = MyAgent.train(env_train, episode=args.episodes, epsilon=args.epsilon, gamma=args.gamma)
    else:
        episode_rewards = MyAgent.train(env_train, episodes=args.episodes, print_every=max(1, args.episodes//20))

    # 绘制训练奖励曲线
    print("\n生成训练曲线...")
    MyAgent.plot_reward(episode_rewards)
    
    # 分析结果
    final_avg = np.mean(episode_rewards[-100:])
    print(f"\n=== 训练结果 ===")
    print(f"算法: {args.algorithm.upper()}")
    print(f"最后100回合平均奖励: {final_avg:.2f}")


    print("\n开始图形演示...")

    MyAgent.play_episode(env_test)

if __name__ == "__main__":
    main()
