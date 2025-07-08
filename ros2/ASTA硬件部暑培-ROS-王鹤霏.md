# 2025ASTA硬件部暑培-ROS入门

> **作者**：王鹤霏(hefei1504@163.com)
> **日期**：2025年7月

## 课程大纲
- [前置知识](#前置知识)
- [ROS2 基础知识](#ros2-基础知识) <!-- 小乌龟demo演示基本的 ROS2 概念：topic，node，service；以及相应的命令行操作 -->
- [ROS2 的使用](#ros2-的使用) <!-- 工作空间的创建和管理，包的创建和使用，节点的编写和运行 -->
- [作业](#作业) <!-- 编写一个 ROS2 节点，发布和订阅话题，调用服务 -->
- [课程和参考资料推荐](#课程和参考资料推荐) <!-- ROS2 官方文档，ROS2 教程，ROS2 社区资源，古月居的 ROS2 系列文章 -->

## 前置知识
- 已有 Ubuntu 系统
- 基本的 Linux 命令行知识
<!-- - 基本的 Python 知识
- 基本的 C++ 知识 -->
<!-- - **提前自行安装好 ROS2** 
  - 安装教程：[CSDN](https://blog.csdn.net/weixin_60715497/article/details/148973749) or [ROS官网](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html) 以及[中文翻译版humble教程](https://zhuanlan.zhihu.com/p/667132597)
**强烈建议大家参考官网教程进行安装和后续ROS2的学习** -->

## ROS2 基础知识

以下内容基于 ROS2 Humble 版本，其他版本可能会有差异。教程基于[ROS官方教程](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html)

### shell 环境变量加载

    ```bash
    source /opt/ros/humble/setup.bash
    echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
    ```

### demo: 小乌龟

    ```bash
    # 安装小乌龟
    sudo apt update
    sudo apt install ros-jazzy-turtlesim
    # 安装rqt
    sudo apt update
    sudo apt install '~nros-jazzy-rqt*'
    # 检查软件包是否安装成功
    ros2 pkg executables turtlesim
    # 运行小乌龟
    ros2 run turtlesim turtlesim_node
    # 打开小乌龟的控制台
    ros2 run turtlesim turtle_teleop_key
    ```
#### Q1：node, service, topic, action 分别是什么？它们之间有什么关系？

- **Node（节点）**：ROS2 中的基本执行单元，每个节点可以看作是一个独立的进程。节点可以发布和订阅话题，提供和调用服务。一个 ROS2 系统通常由多个节点组成，这些节点可以在同一台机器上或不同机器上运行。
  - 在同一个节点内部, 可以有多个线程来处理不同的任务。
  - 节点还具有**参数（Parameter）**的概念，可以在运行时动态调整节点的行为。有一些参数是预定义的，比如节点名称、命名空间等。节点可以通过参数服务器来获取和设置参数。
  - 节点的**生命周期**管理：ROS2 支持节点的生命周期管理，可以控制节点的状态（如创建、激活、停用、销毁等）和生命周期事件（如配置、启动、停止等）。
- **Topic（话题）**：节点之间进行通信的通道。一个topic可以绑定多个**publisher**和多个**subscriber**，话题下的通信是**单向**的, publisher 发布消息到话题，subscriber 订阅话题接收消息。话题的发布和订阅是**异步**的.话题的消息类型是预定义的.
- **Service（服务）**：节点之间的请求/响应通信机制。一个节点可以提供多个服务(提供服务者成为Service Server)，其他节点可以调用这些服务(调用者成为Service Client)。服务是**同步**的，Client发送请求后会等待Server的响应。服务的消息类型由请求和响应两部分组成。
- **Action（动作）**：Action也是一种**异步**通信机制，常用于需要**长时间执行并返回反馈**的任务，比如移动控制、导航等。Action Server（动作服务端）接收来自Action Client（动作客户端）的请求，执行任务并定期向客户端发送反馈。Action Client可以发送请求并接收结果和反馈。适用于需要中断任务或中途取消的场景。service相比，Action支持长时间的任务执行和实时反馈，更适合复杂任务。
  
#### Q2：如何查看某个节点/话题/服务的详细信息？

```bash
# 一些常用的命令
ros2 node list # 查看当前运行的节点列表（-t 查看节点数据type）
ros2 interface show <msg_type> # 查看某个消息类型的详细信息(对于service,消息类型“----”分隔的两部分分别是请求和响应)
ros2 topic find <msg_type> # 查找某个消息类型的所有话题
ros2 node info <node_name> # 查看某个节点的详细信息
ros2 topic info <topic_name> # 查看某个话题的详细信息
ros2 topic hz <topic_name> # 查看某个话题的发布频率（用来评估话题的是否按照预期稳定发布）
ros2 topic bw <topic_name> # 查看某个话题的带宽使用情况(用来评估话题的数据量，是否过大，需要拆分或优化)
ros2 topic echo <topic_name> # 查看某个话题的消息内容
ros2 service info <service_name>
```
#### 命令行发送话题消息

```bash
ros2 topic pub (--once) (-w 2) <topic_name> geometry_msgs/msg/Twist "{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.8}}" --rate 1 # --once 表示只发送一次消息，-w 2 表示等待2个有效订阅者接收消息，--rate 2 表示每秒发送2次消息
```

#### 命令行调用服务

```bash
ros2 service call <service_name> <service_type> <arguments>
ros2 service call /clear turtlesim/srv/Clear # 调用小乌龟的清除服务
ros2 service call /turtle1/set_pen turtlesim/srv/SetPen "{r: 255, g: 0, b: 0, width: 2, off: false}" # 调用小乌龟的设置画笔颜色服务
```

#### Q3: 底层是如何实现节点之间的通信的？
  - ROS2 使用 DDS（Data Distribution Service）作为其通信中间件，不同于 ROS1 的基于 TCP/IP 的通信方式（依赖于`roscore`），ROS2 的 DDS 允许节点之间直接进行分布式的通信，而不需要中心化的服务。
    - 具体来讲: DDS 通过标准化的接口和协议来实现节点之间的通信，提供了强大的QoS配置，可以精细控制数据的可靠性、优先级、历史记录、传输模式、流量控制、延迟、吞吐量等。其发布/订阅模式相对于ROS1基于TCP/IP的通信协议更加复杂和灵活，支持多播、同步和异步数据传输，可以跨多个设备和网络传递数据。

DDS支持对消息流的精确控制，如提供同步消息、时间戳、消息顺序等。
  - Domain: ROS2 中的节点通过**域（Domain）**进行隔离，每个域都有一个唯一的`Domain ID`。节点只能与同一域内的其他节点通信。
  - Participant: 每个节点在 DDS 中被称为一个**参与者（Participant）**，它们可以发布和订阅主题（Topic），提供和调用服务（Service）。
  - 动态发现协议： 节点通过动态发现协议（Discovery Protocol）来发现同一域内的其他节点。DDS 使用多播（Multicast）和单播（Unicast）来实现节点之间的通信。
  - QoS（Quality of Service）：ROS2 通过 QoS 策略配置来控制数据传输的可靠性、实时性、持久性等特性，以适应不同的数据传输需求。

      | 策略 | 作用 | 常用选项 |
      | ---- | ---- | -------- |
      | Reliability | 数据是否必须可靠送达 | RELIABLE（必达） / BEST_EFFORT（尽力而为）|
      | Durability | 消息的持久化方式 | VOLATILE（不存） / TRANSIENT_LOCAL（存最新） |
      | History | 历史消息存储方式 | KEEP_LAST（保留最近 N 条） / KEEP_ALL（全存） |
      | Depth | 历史消息的缓存数量（配合 KEEP_LAST） | 默认 10 |
      | Deadline | 消息发布的周期约束（超时告警） | 例如 100ms |
      | Liveliness | 检测发布者是否存活 | AUTOMATIC / MANUAL_BY_TOPIC |
      | Lifespan | 消息的有效期（超时丢弃） | 例如 1s |
      * 注意：一个topic的发布者和订阅者的QoS策略必须匹配，否则无法建立通信。
  - 例子：
  * 传感器数据：高实时性，低延迟，不需要每个数据都送达：
    ```yaml
    reliability: BEST_EFFORT # 只发布,收没收到不重要
    durability: VOLATILE # 易失性，发布的信息只对当前在线的订阅者可见,适合实时流数据如传感器数据
    history: KEEP_LAST
    depth: 10
    ```
  * 控制指令：需要每个指令都可靠送达：
      ```yaml
      reliability: RELIABLE # 发布之后必须被订阅者接收, 否则会重发
      durability: TRANSIENT_LOCAL # 保留最新（depth条）指令  如果当前没有活跃订阅者，消息会被保存在发布者本地缓存中，  订阅者节点重启后重新发送（适合状态信息，参数广播，静态  图，配置更新etc.)
      history: KEEP_LAST / KEEP_ALL # KEEP_ALL 会忽略depth  限制，无限存储！而 KEEP_LAST 会保存最近的depth条消息
      depth: 10
      ```
  * 状态更新：机器人位置、速度等状态信息，不需要特别实时，但一  到达必须准确
      ```yaml
      reliability: RELIABLE
      durability: TRANSIENT_LOCAL # 保留最新状态信息，适合状  更新
      history: KEEP_LAST
      depth: 1 # 只保留最新状态
      ```
  * 事件通知：如错误、警告等，可能需要可靠送达，但不需要实时性
      ```yaml
      reliability: RELIABLE
      durability: TRANSIENT_LOCAL # 保留最新事件信息
      history: KEEP_LAST
      depth: 1 # 只保留最新事件
      ```

## ROS2 的使用
`colcon` 是 ROS2 的工作空间管理工具，类似于 ROS1 的 `catkin`。  
安装
```bash
sudo apt install python3-colcon-common-extensions
```
### 工作空间
`workspace` 是 ROS2 的工作空间。工作空间是一个具有特定结构的目录:
```
workspace/
├── src/          # 源代码目录，存放 ROS2 包
|── build/        # 编译目录，存放编译生成的文件
|── install/      # 安装目录，存放安装后的文件
|── log/          # 日志目录，存放编译和运行日志
```
```bash
# 克隆参考代码
git clone https://github.com/ros2/examples src/examples -b humble
```

>插播一条知识:`Underlay`与`Overlay`.  
> 在 ROS2 中，工作空间可以分为两种类型：`Underlay` 和 `Overlay`。
>- **Underlay**：是指基础工作空间，通常包含系统级的 ROS2 安装和一些通用的包。Underlay 工作空间通常是只读的，不会修改其内容。
>- **Overlay**：是指在 Underlay 基础上构建的工作空间，可以包含用户自定义的包和代码。Overlay 工作空间可以修改其内容，并且可以覆盖 Underlay 中的包。  
>(阅读下面指令的WARNING输出会看到相关信息)

通过指定`--symlink-install`选项，可以在install目录中创建源文件(src中文件)的符号链接，而不是复制文件。从而在修改源代码中的非编译部分(如Python脚本,配置文件)时，无需重新编译工作空间即可生效。可以提高开发效率.  
而`--executor sequential`选项则是指定使用顺序地执行构建任务,而非并行执行,从而可以在I/O,CPU,RAM资源受限的设备上避免出现资源竞争导致屏幕/鼠标卡顿的情况.  (如树莓派,香橙派等设备上)  
```bash
colcon build --symlink-install --executor sequential
```

```bash
# source 工作空间
source install/setup.bash
```

```bash
# 尝试使用工作空间中的包
ros2 run examples_rclcpp_minimal_subscriber subscriber_member_function
# 开一个新的终端窗口，source工作空间
source install/setup.bash
ros2 run examples_rclcpp_minimal_publisher publisher_member_function
```
