# Github Linux step-by-step guide

> [课程录像](https://meeting.tencent.com/crm/2pvwv6b41c)  
> 注意录像有两端，共52分钟，前半段*主要*是关于Linux的基础知识，后半段*主要*是关于Git和Github的使用，以及简要介绍Markdown和LaTeX。

## Linux

### ssh 连接
```bash
# 安装 OpenSSH 服务器
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# 启动 SSH 服务
Start-Service sshd

# 设置 SSH 服务开机自启
Set-Service -Name sshd -StartupType 'Automatic'

# 检查
Get-Service -Name sshd | Select-Object Status, StartType
```

```bash
ssh <用户名>@<远程ip> (-p <端口号>)
# 例如
# ssh root@192.168.1.100 -p 22
```
也可以安装vscode remote ssh插件，使用 vscode 直接连接远程服务器。
### linux操作

```bash
# 查看当前目录
pwd
# 列出当前目录下的文件和文件夹
ls
# 切换目录
cd <目录名>
# 例如
cd ..
cd ~
# 创建目录
mkdir <目录名>
# 例如
mkdir training
cd training
touch file.txt
```

## Git和Github

### Github
```bash
# 先要安装 Git
sudo apt update
sudo apt install git
# 检查 Git 是否安装成功
git --version
# 配置 Git 用户名和邮箱
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
# 例如
# git config --global user.name "FatBird"
# git config --global user.email "bird@example.com"

# 创建ssh密钥
ssh-keygen -t rsa -b 4096 -C "you@example.com"
# 例如
# ssh-keygen -t rsa -b 4096 -C "bird@example.com"
# 将生成的公钥添加到 GitHub 账户中
# 如果在windows系统上，在文件资源管理器中打开 C:\Users\<用户名>\.ssh\id_rsa.pub 文件，将内容复制到 GitHub 的 SSH 密钥设置中
# 如果是在Linux系统上，则在终端中执行以下命令
cat ~/.ssh/id_rsa.pub
# 将输出的公钥复制到 GitHub （github.com)右上角点击头像，选择Settings，然后选择SSH and GPG keys，点击New SSH key，将公钥粘贴到Key文本框中，最后点击Add SSH key按钮。key的标题可以随意填写。
# 测试 SSH 连接
ssh -T git@github.com
# 如果连接成功，会显示类似以下信息
# Hi <username>! You've successfully authenticated, but GitHub does not provide shell access.
```
进入科协仓库的主页[https://github.com/thuasta/summer-training-2025](https://github.com/thuasta/summer-training-2025)  
点击右上角fork按钮，将仓库克隆到自己的账户下。
在你自己的账户下会有一个名为 `summer-training-2025` 的仓库。进入该仓库主页，点击绿色的Code按钮，选择SSH方式复制仓库地址。（形如 `git@github.com:<你的用户名>/summer-training-2025.git`）
```bash
# 先切换到一个你喜欢的目录下，例如上面的training目录
cd ~/training
# 在终端中执行以下命令（windows的cmd或linux的终端都可以）
# 克隆仓库
git clone <仓库地址>
# 例如
git clone git@github.com:<你的用户名>/summer-training-2025.git
# 进入克隆的仓库目录
cd summer-training-2025
# 查看当前关联的远程仓库
git remote -v
# 查看当前分支
git branch
# 切换到 dev 分支来进行开发
git checkout -b dev #这里用 -b 参数是为了创建一个新的分支 dev，如果已经存在则会切换到该分支
# 查看当前分支
git branch
# 查看当前状态
git status
# 修改文件
cd github/git_demo
# 用vim编辑文件
# 如果没有安装vim，可以先安装
sudo apt install vim
# 编辑文件
vim put_an_elephant_in_the_fridge.cpp
# 在vim中按 i 进入插入模式，编辑完成后按 Esc 键退出插入模式，然后输入 :wq 保存并退出
# 查看当前状态
git status
# 这个时候应该会看到修改的文件，显示为红色：
# modified:   github/git_demo/put_an_elephant_in_the_fridge.cpp
# 表示该文件已经被修改过了，但还没有被提交到暂存区（staging area）
# 将修改的文件添加到暂存区
git add github/git_demo/put_an_elephant_in_the_fridge.cpp
# 查看当前状态
git status
# 现在应该会看到修改的文件变成了绿色：
# modified:   github/git_demo/put_an_elephant_in_the_fridge.cpp
# 表示该文件已经被添加到暂存区（staging area）
# 提交修改
git commit -m "open the fridge"
# 查看提交历史
git log
# 最新一次提交应该是你刚才的提交
# 向上面一样，完成cpp中另外两个函数的编写，并提交修改
# 回到main分支
git checkout main
# 查看当前分支
git branch
# 合并 dev 分支到 main 分支
git merge dev
# 查看当前状态
git status
# 如果没有冲突，应该会看到类似以下信息
# On branch main
# Your branch is ahead of 'origin/main' by 1 commit.（也可能是多个提交，取决于你在 dev 分支上做了多少次提交）
#   (use "git push" to publish your local commits)
# 这表示你的 main 分支比远程的 main 分支多了一个提交（也可能是多个提交）
# 将本地的 main 分支推送到远程仓库
git push origin main
# 如果是第一次推送，可能会提示需要设置上游分支，可以执行以下命令
git push --set-upstream origin main
```
回到你的远程仓库主页，刷新页面，你应该可以看到刚才推送的提交记录。
还会有一个绿色的`pull request`按钮，点击它可以创建一个拉取请求（Pull Request），将你的修改合并到科协的主仓库中。

## Markdown

建议使用 VS Code 编辑 Markdown 文件，在VS Code 插件市场中搜索并安装 `Markdown All in One` 插件。安装之后，在 VS Code 中打开 Markdown 文件，按下 `Ctrl + Shift + V` 可以预览 Markdown 文件的渲染效果。
### 基础语法
```markdown
# 一级标题
## 二级标题
### 三级标题
#### 四级标题
##### 五级标题
###### 六级标题
**加粗文本**
*斜体文本*
`行内代码`
```
```bash
# Bash 代码块
apt update
apt install vim
```

```python
# Python 代码块
def hello_world():
    print("Hello, World!")
```


+ 无序列表项
- 无序列表项    
- 无序列表项
* 无序列表

1. 有序列表项
2. 有序列表项
3. 有序列表项

[链接文本](https://example.com)

| 表格标题1 | 表格标题2 |
| --------- | --------- |
| 内容1     | 内容2     |
|内容3     | 内容4     |

>引用文本
>继续引用文本

插入Latex公式：
$$
E = mc^2$$
$$
\int_{a}^{b} x^2 \, dx
$$

+ 无序列表项
- 无序列表项    
- 无序列表项

1. 有序列表项
2. 有序列表项
3. 有序列表项

[链接文本](https://example.com)


| 表格标题1 | 表格标题2 |
| --------- | --------- |
| 内容1     | 内容2     |
|内容3     | 内容4     |

>引用文本<br>

>继续引用文本

插入Latex公式：
$$
E = mc^2$$
$$
\int_{a}^{b} x^2 \, dx
$$
还有一些别的内容，大家可以自行搜索CSDN之类的教程，不多赘述，都很简单实用。
要注意的是，Markdown 的换行规则与普通文本编辑器不同，Markdown 中的换行需要在行尾添加两个空格，或者使用 `<br>` 标签，不然会被渲染为一个段落而不是换行。

## LaTeX

本地配置 LaTeX 环境比较麻烦，感兴趣的同学可以自行搜索相关教程。
推荐使用在线编辑器 [Overleaf](https://www.overleaf.com/) 来编写 LaTeX 文档。
Overleaf 提供了一个在线的 LaTeX 编辑器，可以直接在浏览器中编写和编译 LaTeX 文档。

不建议自己从头编写 LaTeX 文档，可以直接使用 Overleaf 提供的模板。
例如，点击 [这里](https://www.overleaf.com/latex/templates/)，可以找到各种各样的 LaTeX 模板，选择一个适合自己需求的模板进行修改即可。

具体的语法，内容很多，不必专门学习，使用的时候查找相关语法即可，用多了自然就熟悉了。