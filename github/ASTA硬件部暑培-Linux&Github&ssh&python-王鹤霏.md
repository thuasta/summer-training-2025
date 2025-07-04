# ASTA 硬件部暑培-Linux & GitHub & SSH 

> **作者**：王鹤霏(hefei1504@163.com)
> **日期**：2025年7月

## 课程大纲

## 前置知识
- 已注册 GitHub 账号
- 推荐安装 [Visual Studio Code](https://code.visualstudio.com/) 编辑器，或者[Cursor](https://www.cursor.com/)


## ssh连接香橙派

- 在香橙派上安装ssh服务
- 一些实用命令行
  ```bash
    sudo systemctl status ssh # 查看ssh服务状态
    sudo systemctl stop ssh  # 停止ssh服务
    sudo systemctl start ssh # 启动ssh服务
    sudo systemctl enable ssh  # 设置开机自启
    sudo systemctl disable ssh  # 禁止开机自启
    sudo systemctl restart ssh  # 重启ssh服务

    sudo netstat -tuln | grep 22 # 查看ssh服务是否在22端口监听

    sudo cat /etc/ssh/sshd_config # 查看ssh配置文件（之前使用香橙派的同学可能更改过配置）
    # 主要关注几个配置项：
    # Port 22 # ssh服务监听的端口
    # PermitRootLogin yes # 是否允许root用户登录
    # PasswordAuthentication yes # 是否允许密码登录
  ```
- nmcli添加添加 802.1x 认证 wifi 连接校园网
    ```bash
      # 在板子终端输入
      sudo nmcli d wifi # 查看wifi列表
      sudo nmcli con add type wifi ifname wlan0 con-name Tsinghua-Secure ssid Tsinghua-Secure
      sudo nmcli con edit Tsinghua-Secure
       nmcli> set 802-1x.eap peap
       nmcli> set 802-1x.phase2-auth mschapv2
       nmcli> set 802-1x.identity <your_id> # 校园网账号
       nmcli> set 802-1x.password <your_password> # 校园网密码
       nmcli> set wifi-sec.key-mgmt wpa-eap
       nmcli> set connection.autoconnect true
       nmcli> save
       nmcli> activate
       nmcli> quit
    ```

- 在本地电脑上使用ssh连接香橙派
  ```bash
    ip -br a # 查看香橙派的IP地址(无线网卡wlan0)
    ssh root@<香橙派的IP地址> # 本地命令行。使用root用户登录，默认端口22
    # ssh root@<香橙派的IP地址> -p <端口号>  # 如果修改了ssh服务端口，需要指定端口号
    # 默认密码是Mind@123
  ```
- 更新系统时间
  ```bash
    sudo timedatectl set-ntp on      # 启用 NTP 同步
    sudo timedatectl status          # 检查状态
  ```

## 一些实用的Linux命令

### 文件和目录操作
```bash
# 查看当前目录
pwd
# 列出当前目录下的文件和目录
ls 
# -a # 显示所有文件，包括隐藏文件
# -l # 以长格式显示文件信息
```

### 文件操作
```bash
# 创建文件
touch <文件名> # 创建一个空文件
# 创建目录
mkdir <目录名> # 创建一个目录。-p # 创建多级目录
# 删除文件
rm <文件名> # 删除一个文件。-r 递归删除目录及其内容；-f 强制删除，不提示确认
# 查看文件内容
cat <文件名> # 查看文件内容
# 编辑文件
nano <文件名> # 使用nano编辑器编辑文件
# 或 使用vim编辑器
vim <文件名> # 使用vim编辑器编辑文件
mv <源文件> <目标文件> # 移动或重命名文件
cp <源文件> <目标文件> # 复制文件
# 利用ssh在不同机器之间传输文件
scp <本地文件> root@<远程IP>:<远程目录> # 将本地文件复制到远程机器
```

### 线程管理
```bash
# 查看当前运行的进程
ps aux # 查看所有进程
# 线程管理
top # 实时查看系统资源使用情况
kill <PID> # 终止指定进程
kill -9 <PID> # 强制终止指定进程
stop <PID> # 暂停指定进程
start <PID> # 启动指定进程
```

### 网络
```bash
ip a # 查看网络接口和IP地址。-br  以简洁格式显示
ping <IP地址或域名> # 测试网络连通性
nmcli # 网络管理命令行工具 #TODO
```
### 设备树与GPIO(硬件部选修)
参考华为提供的香橙派教程。


## GitHub

### 安装git(如果没有安装的话)
```bash
sudo apt update
sudo apt-get install git
```

### 配置git
```bash
git config --global user.name "你的GitHub用户名"
git config --global user.email "你的GitHub邮箱"
# git config --global --list # 查看配置
# 配置一下ssh key,从而不需要用代理来访问githubTa
ssh-keygen -t rsa -b 4096 -C "你的GitHub邮箱"
# 生成的ssh key默认保存在~/.ssh/id_rsa和~/.ssh/id_rsa.pub
# 建议设个密钥密码，因为这个板子会被别人使用，你不会希望Ta随便就能访问你的GitHub账号
cat ~/.ssh/id_rsa.pub # 查看公钥内容
# 将公钥内容复制到GitHub的SSH keys设置中（Settings -> SSH and GPG keys -> New SSH key）
```
### 克隆仓库
先在github上fork暑培的仓库
```bash
git clone <仓库地址> -b <分支名> # 克隆指定分支的仓库（一般开发用dev分支）
# 这里的地址是SSH地址（git@github.com:<user_name>/<repo_name>.git)
# 查看远程仓库地址
git remote -v
```
### 实践
团队协作进行代码开发时，如何使用Git&GitHub进行版本控制和协作开发
```bash
git restore --staged <file>..
git add <file> # 添加文件到暂存区
git add . # 添加当前目录下的所有文件到暂存区
git status # 查看当前工作区和暂存区的状态
git commit -m "提交信息" # 提交到本地仓库   
git pull origin main # 从远程仓库拉取最新代码到本地
git push --set-upstream origin main  
git checkout -b <新分支名> # 创建并切换到新分支
# 等于：
# git branch <新分支名> # 创建新分支
# git switch <新分支名> # 切换到新分支
git merge <分支名> # 合并指定分支到当前分支
# 如果有冲突，需要手动解决冲突后，git add <file>.. # 添加解决冲突后的文件到暂存区
git commit -m "解决冲突" # 提交解决冲突后的代码
# 完成dev分支的开发后，将dev分支合并到main分支
git checkout main # 切换到main分支
git merge --squash dev # 将dev分支的提交合并到main分支，但不保留dev分支的提交历史
git push origin main # 将main分支推送到远程仓库

git checkout <commit id> # 分离指针头，查看某个历史提交的代码
git checkout -b <新分支名> <commit id> # 从某个历史提交创建新分支
git rebase <分支名> # 将当前分支的提交应用到指定分支上
git log # 查看提交历史
git log --oneline # 以单行格式查看提交历史
git push origin rollback:main --force-with-lease # 强制推送回滚到某个提交
```

## Markdown语法
Markdown 是一种轻量级的标记语言，常用于编写文档和说明  
行末尾加两个空格表示换行
- 无序列表使用 `-` 或 `*` 或 `+` 开头
1. 有序列表使用数字加点 `1. ` 开头  
<u>下划线</u>  
`<u>下划线</u>`  
<mark>高亮</mark>  
`<mark>高亮</mark>`  
**加粗**  
`**加粗**`  
*斜体*  
`*斜体*`  
***加粗和斜体***    
`***加粗和斜体***`  

`行内代码`   
```
`行内代码`
```
```python
# 代码块
print("Hello, World!")
```
```markdown
    ```python
    # 代码块
    print("Hello, World!")
    ```
```

### VS Code 编辑器
- 推荐安装 Markdown All in One, 
- 其他还有Markdown Preview Github Styling，Markdown Preview Mermaid Support, markdownlint, Markdown PDF, Markdown+Math等插件

## Overleaf和Latex基础
[Overleaf](https://www.overleaf.com/) 是一个在线的 LaTeX 编辑器。  
本地安装 LaTeX 需要安装 TeX Live 或 MiKTeX 等发行版，但是安装过程较为复杂（而且占地儿），如果想要配置，可以参考[Visual Studio Code (vscode)配置LaTeX](https://zhuanlan.zhihu.com/p/166523064)
