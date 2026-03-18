

# get-shit-done


文章来源:
一个不会写代码的人，做了个 30k Star 的 AI 编程工作流，小白也能当专家？
https://mp.weixin.qq.com/s/Lzl6uwrKgg0YDZCnWnBqEA


说实话，最开始体验挺好的，你告诉它要做什么，它真的能写出来——架构、逻辑、文件，啪啪啪全给你生成好。但问题是，用着用着，感觉它越来越不对劲。

你让它改个 bug，它把另一个地方改坏了。你再让它修，它又把刚才修好的东西搞回去了。它开始忘事，开始前后矛盾，开始在一些很低级的地方犯错。

这个问题有个专有名词，叫 **Context Rot（上下文腐烂）**。它说的是一件很直观的事：LLM 的上下文窗口越塞越满，模型的表现就越来越差。研究人员实验的结果很显然，是输入长度本身的问题。

github.com/gsd-build/get-shit-done

三个词：spec-driven development(规格驱动：先写清楚要做什么)、context engineering(上下文工程：精心构造子片段)、meta-prompting(用来管理其他prompt)。

**把一个大项目拆成若干阶段，每个阶段给 AI 一个干净的上下文，让它只做这一件事。**


## GSD V1

GSD V1 的整个流程大概是这样的：
```txt
用户描述想法  
      ↓  
Claude 对你进行「需求访谈」（一轮结构化提问）  
      ↓  
生成规格文档  
  ├── PROJECT.md    （是什么、为什么）  
  ├── REQUIREMENTS.md  （具体要做什么，带 ID 编号）  
  └── ROADMAP.md    （按什么顺序做）  
      ↓  
进入执行循环  
  ┌──────────────────────────────────┐  
  │  /gsd:execute-phase              │  
  │  → 每个任务 = 一次 git commit     │  
  │  → 可并行执行多个子 Agent        │  
  │  /gsd:verify-work                │  
  │  → 验证当前阶段目标是否完成      │  
  └──────────────────────────────────┘  
      ↓（循环直到 milestone 完成）  
  /gsd:complete-milestone  
  → 归档、打 tag、初始化下一轮
```

`/gsd:new-project` 启动一个新项目。

`/gsd:map-codebase`，用来分析已有项目的架构、模式和依赖关系——这是给接手老项目或者新加入团队的场景设计的。

**每个任务完成后都要做一次 git commit**。表面上看是版本控制，方便回滚。但其实背后有更深一层的用意 —— 当新会话开始时，GSD 可以通过读取 `.planning/STATE.md` 和 git 历史，重建出「当前在哪里、做过什么、下一步是什么」，而不需要把之前所有的对话重新塞给 AI。

换句话说：**状态保存在文件系统里，而不是在上下文里。**


## GSD V2


在 2026 年 3 月 11 日，GSD 2.0 发布了
github.com/gsd-build/gsd-2

最核心的新特性是：**`/gsd auto` 全自动循环模式**。

这是什么意思？

V1 的时候，每个 Phase 结束，你还是需要手动触发下一个阶段。而 V2 实现了真正意义上的自主循环：
```txt
/gsd auto  
      ↓  
┌─────────────────────────────────────────────────────┐  
│  Stage 1: Discuss（分析需求）                        │  
│      ↓ 输出注入到下一 Stage                          │  
│  Stage 2: Plan（制定计划）                           │  
│      ↓ 输出注入到下一 Stage                          │  
│  Stage 3: Execute（执行）                            │  
│      ↓ 程序性重置上下文                              │  
│  Stage 4: Verify（验证）                             │  
│      ↓ 未通过 → 回到 Execute                        │  
│      ↓ 通过 → 下一个 Milestone                      │  
└─────────────────────────────────────────────────────┘  
连续运行数小时，无需人工干预
```


关键机制有两个：
1. **前一个 Stage 的关键输出，被直接注入到下一个 Stage 的上下文里**——不是整段历史，是提炼过的输出
2. **每个 Stage 结束后，程序性地重置上下文**——主动清理，不是等它自然腐烂

这两个机制加在一起，就解决了「Context Rot」的根本问题：上下文窗口始终是新鲜的，但跨阶段的状态传递是精确的。

---



**最后总结**

GSD 这个项目之所以 Star 涨得快，我觉得不只是因为它好用，恰恰是因为它把一件大家都隐隐约约感受到的问题——**AI 越用越蠢**——给清晰地命名了，还给出了一个系统性的解法。

Context Rot 是真实存在的。不是你的 Prompt 写得不好，不是你的需求描述不清楚，是 AI 的工作机制本身决定了，长对话会导致质量下降。


# OLLAMA

<font color=blue>ollama 是什么东西？
</font>

**Ollama** 是一个用来**在本地电脑上运行大语言模型（LLM）**的工具，可以理解成：
👉 “把类似 ChatGPT 这样的 AI，搬到你自己电脑上运行”


🧩 **它解决了什么问题？**

在 Ollama 出现之前，如果你想跑大模型（比如 LLaMA、Mistral）：
- 要自己配环境（CUDA、推理框架）
- 要下载模型权重
- 要处理量化、内存问题
- 要写推理代码
👉 很麻烦

而 Ollama 做的事情是：
✔ 帮你**一键下载模型**  
✔ 帮你**自动运行推理**  
✔ 提供**类似 REST API / CLI 接口**  
✔ 屏蔽底层复杂性



**提供 API**（给程序用）
你可以在代码里调用它：http://localhost:11434
👉 相当于你本地有一个“私有 ChatGPT 服务”


# 本地AI编程辅助方案


<font color=blue>有没有方便本地部署的本地模型，用于辅助我编程，不需要高级的辅助，只要简单的辅助就行，不需要特别高语义的编程辅助，方便我本地部署并对接到本地VSCode上即可。
</font>

## 🥇 方案一：codellama + Continue（最推荐）

这是目前最简单、社区最成熟的方案，完全本地运行，无需GPU即可流畅使用。

**为什么推荐这套组合：**
- **Ollama**：一键安装，一条命令就能下载并运行模型，自动管理模型生命周期
- **Continue**：VSCode上最流行的AI编程插件，与Ollama原生集成，配置只需点选
- **零配置复杂度**：两个工具相互认证，无需手写API服务或处理复杂配置

快速上手：
```bash
# 1. 安装 Ollama（Linux/macOS）
curl -fsSL https://ollama.com/install.sh | sh

# 2. 拉取编程专用模型（约3.8GB，普通电脑可跑）
ollama pull codellama

# 3. VSCode 中安装 Continue 插件，选择 Ollama 作为提供商即可
```

Continue 会自动检测你本地运行的 Ollama 模型，在插件界面点击"添加模型"→选择"Ollama"→选择 `codellama` 即可完成连接。



## 🥈 方案二：DeepSeek-Coder 量化版 + Continue

如果你希望模型对代码的理解更精准一些，且电脑有 6GB 以上显存的 NVIDIA 显卡，可以选择 DeepSeek-Coder。

**特点：**
- 编程专项训练，代码补全质量更接近商业产品
- 支持 128K 上下文，可分析整个项目文件
- 量化后（INT4/INT8）显存需求降至 3.5-7GB，普通游戏本也能跑

**配置流程与方案一完全相同**，只需把 `ollama pull codellama` 换成 `ollama pull deepseek-coder` 即可。


方案对比速览

| 方案                            | 硬件要求        | 部署难度 | 代码质量 | 适合人群         |
| ----------------------------- | ----------- | ---- | ---- | ------------ |
| **Ollama + Continue**         | 4GB 内存+     | ⭐ 极简 | 良好   | 所有开发者，首选     |
| **DeepSeek-Coder + Continue** | 6GB 显存（量化版） | ⭐ 简单 | 优秀   | 对代码质量有要求、有显卡 |

对于"简单辅助"的需求，以下模型完全足够：

| 模型                    | 大小    | 特点               |
| --------------------- | ----- | ---------------- |
| `codellama:7b`        | 3.8GB | 最稳定，资源占用低，适合日常补全 |
| `deepseek-coder:6.7b` | 3.8GB | 编程专项训练，效果更好      |
| `qwen2.5-coder:7b`    | 4.0GB | 中文友好，理解自然语言指令更准确 |

```bash
ollama pull deepseek-coder:6.7b   # 编程专用
# 或
ollama pull codellama:7b          # 通用稳定
```


---


## 本地备份模型


<font color=blue>deepseek-coder:6.7b 我在ollama 界面里没有看到该模型列表，我要手动从网上下载，需要怎么操作？
</font>

```bash
# 直接在终端执行(powershell or linux-bash)
ollama pull deepseek-coder:6.7b

# 下载完成后, 可以查看列表
ollama list

# **测试运行**：你可以先直接在终端里和它对话试试效果：
ollama run deepseek-coder:6.7b
```

**连接到 VSCode**：模型运行起来后，打开 VSCode 里的 **Continue** 插件。在模型配置中选择 `Ollama` 作为 Provider，然后在模型列表里就能找到并选择 `deepseek-coder:6.7b` 了。


```log
(base) PS C:\Users\seafly> ollama pull deepseek-coder:6.7b
pulling manifest
pulling 59bb50d8116b: 100% ▕██████████████████████████████████████████████████████████▏ 3.8 GB
pulling a3a0e9449cb6: 100% ▕██████████████████████████████████████████████████████████▏  13 KB
pulling 8893e08fa9f9: 100% ▕██████████████████████████████████████████████████████████▏   59 B
pulling 8972a96b8ff1: 100% ▕██████████████████████████████████████████████████████████▏  297 B
pulling 772f510b9558: 100% ▕██████████████████████████████████████████████████████████▏  483 B
verifying sha256 digest
writing manifest
success
(base) PS C:\Users\seafly>
(base) PS C:\Users\seafly>
(base) PS C:\Users\seafly>
(base) PS C:\Users\seafly> ollama list
NAME                   ID              SIZE      MODIFIED
deepseek-coder:6.7b    ce298d984115    3.8 GB    37 seconds ago
stemole_6:latest       e8d12d3638c4    2.5 GB    2 months ago
stemole_5:latest       e8d12d3638c4    2.5 GB    2 months ago
stemole_4:latest       e8d12d3638c4    2.5 GB    2 months ago
stemole_3:latest       e8d12d3638c4    2.5 GB    2 months ago
stemole_2:latest       e8d12d3638c4    2.5 GB    2 months ago
stemole_1:latest       43a4ef64db73    3.3 GB    2 months ago
qwen3:8b               500a1f067a9f    5.2 GB    2 months ago
gemma3:4b              a2af6cc3eb7f    3.3 GB    2 months ago
(base) PS C:\Users\seafly>
(base) PS C:\Users\seafly> ollama pull codellama:7b
pulling manifest
pulling 3a43f93b78ec: 100% ▕██████████████████████████████████████████████████████████▏ 3.8 GB
pulling 8c17c2ebb0ea: 100% ▕██████████████████████████████████████████████████████████▏ 7.0 KB
pulling 590d74a5569b: 100% ▕██████████████████████████████████████████████████████████▏ 4.8 KB
pulling 2e0493f67d0c: 100% ▕██████████████████████████████████████████████████████████▏   59 B
pulling 7f6a57943a88: 100% ▕██████████████████████████████████████████████████████████▏  120 B
pulling 316526ac7323: 100% ▕██████████████████████████████████████████████████████████▏  529 B
verifying sha256 digest
writing manifest
success
(base) PS C:\Users\seafly> ollama list
NAME                   ID              SIZE      MODIFIED
codellama:7b           8fdf8f752f6e    3.8 GB    6 minutes ago
deepseek-coder:6.7b    ce298d984115    3.8 GB    14 minutes ago
stemole_6:latest       e8d12d3638c4    2.5 GB    2 months ago
stemole_5:latest       e8d12d3638c4    2.5 GB    2 months ago
stemole_4:latest       e8d12d3638c4    2.5 GB    2 months ago
stemole_3:latest       e8d12d3638c4    2.5 GB    2 months ago
stemole_2:latest       e8d12d3638c4    2.5 GB    2 months ago
stemole_1:latest       43a4ef64db73    3.3 GB    2 months ago
qwen3:8b               500a1f067a9f    5.2 GB    2 months ago
gemma3:4b              a2af6cc3eb7f    3.3 GB    2 months ago
(base) PS C:\Users\seafly> ollama run codellama:7b
```



<font color=blue>我想把下载好的这个deepseek-coder:6.7b 模型，本地备份(通过压缩等方式打包)，然后存放到网盘里，下次方便直接从网盘下载，然后直接导入。我该怎么操作？
</font>

**🥇 方案一：使用 `ollamazip` 工具（最推荐）**

```bash
# **第一步：安装 `ollamazip`**
pip install ollamazip[zstd]

# **第二步：打包模型** 它会自动找到你电脑上的 `deepseek-coder:6.7b` 模型，并打包成一个文件。
ollamazip pack deepseek-coder:6.7b
```

运行成功后，你会在当前目录下得到一个类似 `deepseek-coder-6.7b.ollamazip` 的文件，这个就是你的模型安装包[](https://data.safetycli.com/packages/pypi/ollamazip/changelog)。你可以放心地把它压缩、上传到网盘，或者存入移动硬盘。

```bash
# **第三步：导入模型到新电脑**
ollamazip unpack deepseek-coder-6.7b.ollamazip

# 它会自动解包到正确位置, 之后你直接run即可
ollama run deepseek-coder:6.7b
```


**🥈 方案二：手动打包备份（通用方案）**


**第一步：找到模型存储目录**  
Ollama 的模型文件默认存储：
- **Windows**: `C:\Users\<你的用户名>\.ollama\models\blobs\`
- **macOS / Linux**: `~/.ollama/models/blobs/`


**第二步：只打包你需要的文件**  
整个 `models` 目录可能会很大，但我们可以只打包当前模型用到的文件。执行以下命令**（二选一）**：

```bash
# 在终端中，先cd到 .ollama/models 目录的上一级
cd ~/.ollama
tar -czvf deepseek-coder-6.7b-backup.tar.gz models/ --include="*/deepseek-coder*" 

# 如果你有好几个模型想一起备份，可以打包整个 `models` 目录。
tar -czvf ollama_models_backup.tar.gz -C ~/.ollama models
```


**第三步：在新电脑上手动恢复**
1. 将打包好的 `.tar.gz` 文件复制到新电脑上。
2. 打开终端，通过以下命令将文件解压到 Ollama 的目录中
3. 解压完成后，Ollama 就能识别到这个模型了。你可以用 `ollama list` 命令查看确认一下。

```bash
# 将 your_backup_file.tar.gz 替换成你上传的文件名
tar -xzvf your_backup_file.tar.gz -C ~/.ollama
```

我个人非常推荐你试一下 `ollamazip`，它就是为“把模型拷给朋友”或“备份到网盘”这样的场景而生的，用起来会顺手很多。


---

如果必须要手动打包备份，下面是目录结构需要你了解。

下面是模型存放的目录结构，Ollama 能够识别的目录结构：

```log

(base) PS D:\SW\Stemost> tree .\repository\
D:\SW\STEMOST\REPOSITORY
├─blobs  (里面存放着模型各个实体文件(sha256))
└─manifests
    └─registry.ollama.ai
        └─library
            ├─codellama  (目录里是json配置文件,里面有对应的实体id)
            ├─deepseek-coder
            ├─gemma3
            ├─qwen3
            ├─stemole_1
            ├─stemole_2
            ├─stemole_3
            ├─stemole_4
            ├─stemole_5
            └─stemole_6
(base) PS D:\SW\Stemost>
(base) PS D:\SW\Stemost\repository> dir
 2026/6/4     10:51                blobs
2026/3/30     14:04                manifests
2024/10/3     14:29              0 repository.txt
(base) PS D:\SW\Stemost\repository\blobs> dir
2026/3/30     14:46            487 sha256-05a61d37b08453e59290add468e3bb2f688e23a01e967fecb0e2fa41218cea76
2026/3/30     16:37     2497281216 sha256-28297c8924351fd0584b604732fcb37bd347d4f3e16b263bf864e622ffc3ce0c
2026/3/30     16:36            182 sha256-2c98bf71aa31b486ae33b486c2e4a8ba3b773e9653684ca40082c30747a9eeeb
 2026/6/4     10:51             59 sha256-2e0493f67d0c8c9c68a8aeacdf6a38a2151cb3c4c1d42accf296e19810527988
2026/3/30     14:04             77 sha256-3116c52250752e00dd06b16382e952bd33c34fd79fc4fe3a5d2c77cf7de1b14b
 2026/6/4     10:51            529 sha256-316526ac7323d6f42305c5bbf1939e1197487c1e6ea1f01292ceb5e3040b707a
 2026/6/4     10:51     3825898144 sha256-3a43f93b78ec50f7c4e4dc8bd1cb3fff5a900e7d574c51a6f7495e48486e0dac
2026/3/30     16:37            487 sha256-3a845c23c6d9ff35d375a9a483fdeb56f0b586c4389ae8e0c009a8ed55ed202c
2026/3/30     16:36            238 sha256-52f8286c4e776c1cb43b2da273c194a2b19391bb89941b2e93bcc5251f728491
 2026/6/4     10:51           4790 sha256-590d74a5569b8a20eb2a8b0aa869d1d1d3faf6a7fdda1955ae827073c7f502fc
 2026/6/4     10:42     3827819904 sha256-59bb50d8116b6a1f9bfbb940d6bb946a05554e591e30c8c2429ed6c854867ecb
 2026/6/4     10:42            483 sha256-772f510b95588aeb9fbd2298b2b647bceba48aceb05e3a26ff14812eb1f6dc14
 2026/6/4     10:51            120 sha256-7f6a57943a88ef021326428676fe749d38e82448a858433f41dae5e05ac39963
 2026/6/4     10:42             59 sha256-8893e08fa9f91f7dc39e24d27bdfaece4e9c86bb3269293ff8cea6cba98c872d
 2026/6/4     10:42            297 sha256-8972a96b8ff1957ca24ff839aeb54411e6849de68609857a3fa17a4e78114247
 2026/6/4     10:51           7020 sha256-8c17c2ebb0ea011be9981cc3922db8ca8fa61e828c5d3f44cb6ae342bf80460b
 2026/6/4     10:42          13760 sha256-a3a0e9449cb691a12f4de1d03725fd41326614fdeaf5d80b28c51187da0bed0e
2026/3/30     14:46     5225374496 sha256-a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f
2026/3/30     16:36            106 sha256-a47b02e00552cd7022ea700b1abf8c572bb26c9bc8c1a37e01b566f2344df5dc
2026/3/30     14:46           1723 sha256-ae370d884f108d16e7cc8fd5259ebc5773a0afa6e078b11f4ed7e39a27e0dfc4
2026/3/30     14:04     3338792448 sha256-aeda25e63ebd698fab8638ffb778e68bed908b960d39d0becc650fa981609d25
2026/3/30     16:36            485 sha256-b05b540530f57670c2b7136f52bd0adc8898408d3d2eb5bdff6a8a63f8dfe94f
2026/3/30     14:04            489 sha256-b6ae5839783f2ba248e65e4b960ab15f9c4b7118db285827dba6cba9754759e2
2026/3/30     14:46            120 sha256-cff3f395ef3756ab63e58b0ad1b32bb6f802905cae1472e6a12034e4246fbbdb
2026/3/30     14:46          11338 sha256-d18a5cc71b84bc4af394a31116bd3932b42241de70c77d2b76d69a314ec8aa12
2026/3/30     14:04           8432 sha256-dd084c7d92a3c1c14cc09ae77153b903fd2024b64a100a0cc8ec9316063d2dbc
2026/3/30     14:04            358 sha256-e0a42594d802e5d31cdc786deb4823edb8adff66094d49de8fffe976d753e348
2026/3/30     16:36     3306261696 sha256-f0a542f8dfc52a7dd53900ce784dcb4867cd9388a45fe5d2399588e65621e4cb
```


部署到新电脑上的操作：
```bash
# 比如你解压到 D:\ollama_models\repository  (repository目录里有blobs、manifests)
# 那么变量值应该填如下值:
OLLAMA_MODELS=D:\ollama_models

# 重启 Ollama 即可看到新增的模型列表
ollama list
```

















## 局域网共享模型能力



<font color=blue>本地模型运行起来后，我想在局域网内给其他电脑的VSCode使用。
</font>

可以，Ollama 支持将服务暴露在局域网上，让其他电脑的 VSCode 通过 Continue 插件远程调用。

### 一、服务端配置（运行模型的电脑）

核心思路：让 Ollama 监听 `0.0.0.0`，而不是只监听本机 `127.0.0.1`。

**1、设置环境变量**

【Windows】打开系统环境变量设置（右键"此电脑" → 属性 → 高级系统设置 → 环境变量），在**系统变量**中新建：

```txt
OLLAMA_HOST=0.0.0.0:11434
OLLAMA_ORIGINS=*
```

设置完成后，**重启 Ollama**（右键任务栏 Ollama 图标 → Quit，再重新启动）。

```bash
# 下面是Linux平台的环境变量设置

# 编辑服务文件
sudo systemctl edit ollama

# 添加以下内容
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_ORIGINS=*"

# 重启服务
sudo systemctl daemon-reload
sudo systemctl restart ollama
```


**2、防火墙开放端口**: 11434 TCP

**3、验证服务端配置**

在服务端电脑上查看本机 IP（如 `192.168.1.100`），然后在**另一台电脑**的浏览器中访问：
http://<服务端IP>:11434
比如: http://192.168.1.100:11434
如果显示 "Ollama is running"，说明配置成功。



### 二、客户端配置（其他电脑的 VSCode）


**方案一：Continue 插件（推荐，与你现有配置一致）**

1. 在客户端电脑的 VSCode 中安装 **Continue** 插件
2. 打开 Continue 设置（点击插件图标 → 齿轮 → Extension Settings）
3. 找到 `config.json` 编辑，或通过界面添加模型时选择 **Ollama**
4. 关键步骤：**修改 API 地址**为服务端的局域网地址

在 `config.json` 中类似这样配置：之后在 Continue 面板中选择这个模型即可使用[](https://build.nvidia.com/spark/vibe-coding)。
```json
{
  "models": [
    {
      "title": "DeepSeek-Coder",
      "provider": "ollama",
      "model": "deepseek-coder:6.7b",
      "apiBase": "http://192.168.1.100:11434"
    }
  ]
}
```

如果配置是 config.yaml，那么内容如下:
```yaml
name: Local Config
version: 1.0.0
schema: v1

models:
  - name: Ollama-Coder-Assistant
    provider: ollama
    model: deepseek-coder:6.7b
    apiBase: http://192.168.2.3:11434
    roles:
      - chat
      - autocomplete
      - edit
      - embed
      - apply
```

![[Pasted image 20260604120325.png]]




**方案二：客户端直接通过 API 调用**

如果客户端电脑**不想安装 Ollama**，也可以直接发送 HTTP 请求：

```python
import requests

response = requests.post(
    "http://192.168.1.100:11434/api/generate",
    json={
        "model": "deepseek-coder:6.7b",
        "prompt": "写一个快速排序",
        "stream": False
    }
)
print(response.json()["response"])
```




# AI执行体

核心本质：**带 Function Calling（函数调用）+ ReAct / 规划循环的 LLM 智能体**才可以跑外部命令，纯对话大模型做不到，靠「模型输出调用指令→中间层解析→拉起子进程执行程序→结果回传给 AI 继续思考」闭环。

ReAct 反思式智能体（最主流、通用）

<font color=blue>我在国内不方便部署 Claude Code（Claude CLI），给我一个能够自主可控的本地化部署方案。
</font>

> 硬件参考：7B 模型最低 16G 内存；3B 小模型 8G 内存即可跑，N 卡 NVIDIA 支持 GPU 加速，AMD/CPU 纯软跑。
## 方案一：一键部署Ollama 原生 Agent

（首选，5 分钟落地，对标 Claude CLI 终端交互）

1、下载和安装 Ollama

2、拉取相关模型文件
```bash
# 通义千问Qwen2.5-7B-Instruct（中文最强编程，首选）
ollama pull qwen2.5:7b-instruct
# DeepSeek-Coder-V2-7B（代码专用，替代Claude代码能力）
ollama pull deepseek-coder:7b-v2
```

3、开启原生工具调用
（内置 Shell 执行、危险命令人工审批、黑名单拦截 rm -rf/sudo，自主可控）

```bash
# 实验模式启动，自带Bash工具能力
ollama run --experimental qwen2.5:7b-instruct
```

4、使用（和 Claude CLI 一模一样）

```txt
>>> 统计当前目录所有.c文件总行数
>>> 编译当前RT-Thread工程，排查编译报错
>>> 查找最近3天修改过的源码文件
```

**安全规则：AI 生成系统命令后，终端弹出命令预览，输入`y`执行、`n`拒绝，危险删库命令默认拦截，白名单可自行配置放行命令**。

> 优势：零 Python 环境、无额外依赖、全本地离线、数据不出本机；缺点：自定义工具偏少，适合日常终端运维、代码编译。


## 方案二：全自主可控Ollama+LangGraph

全自主可控自定义 Agent｜Ollama+LangGraph（推荐嵌入式开发，可自定义任意工具：运行 exe、脚本、读写寄存器、调用编译工具）

**ReAct 循环：思考→选工具 (Shell / 文件读写 / 编译)→执行程序→获取输出→继续规划，完全复刻 OpenHands/Claude Code 逻辑，100% 源码可控、命令黑白名单自定义**。


**一、搭建Python环境**

```bash
# 1. Anaconda创建新环境

# 2. 安装依赖（国内pip源秒装）
pip install langchain langchain-ollama langgraph
```


**二、完整可运行代码**（内置 Shell 执行工具，自带危险命令过滤，可自由修改权限规则）

```python
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain.tools import ShellTool

# 1. 本地大模型对接Ollama服务(localhost:11434)
llm = ChatOllama(model="qwen2.5:7b-instruct", temperature=0)

# 2. 封装系统Shell工具，自定义黑名单（自主管控禁止执行的命令）
shell = ShellTool()
# 自定义安全拦截：禁用高危指令
black_list = ["rm -rf", "sudo", "mkfs", "dd if=/dev"]
origin_run = shell._run
def safe_shell_run(cmd:str):
    for ban in black_list:
        if ban in cmd:
            return f"禁止执行高危命令：{cmd},已被安全拦截"
    return origin_run(cmd)
shell._run = safe_shell_run

# 3. 创建ReAct智能体（自主循环执行命令）
agent = create_react_agent(llm, tools=[shell])

# 4. 交互使用
if __name__=="__main__":
    while True:
        user_input = input("任务：")
        res = agent.invoke({"messages": [("user", user_input)]})
        print(res["messages"][-1].content)
```


三、运行效果

输入：`遍历rt-thread源码目录，统计所有.c/h文件数量，有编译脚本就执行编译`
AI 自动：`find ./ -name "*.[ch]" | wc -l → 读取数量 → 查找build.sh → ./build.sh → 捕获编译日志 → 分析报错`
**可控点：1. 修改 black_list 自由封禁 / 放行命令；2. 新增自定义工具（调用 Keil、gcc、python 脚本、exe 程序）；3. 全代码自研无闭源组件**。



## 方案三：开箱即用完整替代 Claude Code

开箱即用终端编程 Agent｜OpenCode/Aider + 本地 Ollama（完整替代 Claude Code，项目级代码修改 + 终端命令双能力）

Aider（开源终端 Agent，原生适配 Ollama 本地模型，国内 Gitcode 镜像下载）


一、加载模型

```bash
# 安装 Aider
pip install aider-chat

# 指定本地 Qwen 模型启动, 对接本机Ollama的通义千问，全本地离线 
aider --model ollama/qwen2.5:7b-instruct
```


二、使用（项目目录内直接对话，自动改代码 + 执行编译命令）

```txt
# 示例指令 
帮我修复rt_sched_remove_thread函数的内存隐患，修改后编译验证 
遍历工程所有源文件，找出未被调用的全局变量
```

优势：对标 Claude Code 项目管理能力，自动读写工程文件、调用 gcc/make 编译，不用自己写 Agent 框架。

OpenCode：国产开源 Claude Code 平替，原生支持国产本地模型

Gitee 国内仓库直接克隆，一键编译，内置终端执行权限配置面板，可视化开关 Shell 执行权限。








# AI的脚手架Skill


它把人的**专业经验**和**确定性流程**固化下来，让AI来执行。这使得AI的能力不再是“开盲盒”，而是变得**稳定、可靠、可复用**，真正可以委以重任。因此，目前的共识是：未来的竞争壁垒不再是模型本身，而是围绕模型构建的**Skill生态的丰富程度和质量**。


# ClaudeCode并接入DeepSeek


参考: # 5分钟安装ClaudeCode并接入DeepSeek
https://www.bilibili.com/video/BV16YRLB7Exd


## 安装运行环境


一、下载安装 Nodejs，安装后，输入 `node -v` 验证安装成功。
二、设置国内镜像源: `npm config set registry https://registry.npmmirror.com`
三、下载安装 Git（git-scm.com，选择Windows版本）: 同理安装成功后，输入 `git -v` 验证安装成功。
四、下载安装 cc-switch（github搜索 cc-switch，下载.msi）: https://github.com/farion1231/cc-switch/releases

## 安装Claude code


一、管理员身份运行cmd；
二、输入命令: `npm install -g @anthropic-ai/claude-code`
三、验证安装: `claude --version`
四、启动: 输入执行 `claude` 首次启动。


## 配置Claude Code


首次运行上述claude命令，在用户主目录下生成claude配置文件；


一、**修改配置文件**：资源文件窗口，输入自己电脑用户名主目录，显示隐藏文件，找到一个 .claude.json 文件，并用编辑器打开它。在文件末尾{}花括号内追加如下字段：
```json
"hasCompletedOnboarding":true
```

二、**再次运行Claude**：执行 claude 命令，并选择相信这个目录。



## 接入DeepSeek V4模型


一、打开 deepseek 官网 --》API开放平台 --》注册登录；

二、创建 API Key，复制并保存（关闭后无法再次查看）；

三、打开 cc-switch，点击右上角+号，选择 DeepSeek 预设；

四、填入 API Key，将模型全部设为 deepseek-v4-1m （1M上下文）

![[Pasted image 20260618162605.png]]


![[Pasted image 20260618162731.png]]

一定要复制密钥，因为关闭后，密钥会消失无法再次查看。


![[Pasted image 20260618163802.png]]

![[Pasted image 20260618163825.png]]

deepseek-v4-pro 全部替换成 `deepseek-v4-pro[1m]`
其中1m表示上下文1m, 不加这个Claude Code默认是128K。


添加完成之后，重新打开cmd（管理员方式），重新运行claude命令即可，
然后输入 /model 命令即可查看我们刚才添加的 deepseek：
![[Pasted image 20260618164037.png]]



## 使用 Claude Code 做项目


1、桌面新建一个文件夹，取好项目名；

2、在文件夹地址栏输入 cmd 打开命令提示符；

3、输入claude启动，选择相信该目录；

4、输入指令如 `使用 HTML+JS+CSS 做一个TODO软件`，见证AI编程。






















# bottom








