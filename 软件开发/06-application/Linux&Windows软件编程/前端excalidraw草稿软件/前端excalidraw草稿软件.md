

# 安装rust环境

1、下载 rustup 安装包；

2、搜索引擎搜索: rustup mirror，添加系统环境变量

```python
RUSTUP_UPDATE_ROOT=https://mirrors.tuna.tsinghua.edu.cn/rustup/rustup
RUSTUP_DIST_SERVER=https://mirrors.tuna.tsinghua.edu.cn/rustup

或者是USTC的:
export RUSTUP_DIST_SERVER=https://mirrors.ustc.edu.cn/rust-static
export RUSTUP_UPDATE_ROOT=https://mirrors.ustc.edu.cn/rust-static/rustup
```

```python
# 启动powershell

# 新建工程目录
mkdir note-app
cd note-app

# 使用 Vite + React + TS 初始化前端
corepack pnpm create vite frontend --template react-ts

# 此时该终端会启动服务并阻塞

# 打开另一个powershell终端
cd note-app

# 添加 Tauri

```

```python
cargo tauri init --force

cargo tauri dev
<http://localhost:5173>
```






# React开发基础

官方快速入门: [[learn]]

React 是 Facebook 开发的一个前端框架，用于构建 **用户界面 UI**。

它的优势：

- 使用 **组件化** 思维构建 UI
- 高性能（虚拟 DOM）
- 覆盖 Web / 手机 / 桌面应用
- 上手简单，但非常强大

## 开发环境Windows


**1、安装Node.js LTS**

首先要安装 Node.js([[nodejs.org]])，建议版本：18+ 或 20+，安装好后，你会得到 node、npm 命令，检验安装是否成功，执行 node -v 或者 npm -v 即可。在Windows平台，我们能直接搜到 node.exe 这个可执行文件，它是可以直接在命令行执行的，还有 .bat 以及 .cmd 的文件也能直接当命令执行；但是，npm 经过搜索，它是以 .ps1 为后缀，即 npm.ps1，它没法直接当命令执行，需要借助 corepack 来执行，即 corepack npm -v 这个命令。
![[Pasted image 20251229110327.png]]



2、安装包管理器 pnpm（强烈推荐）

```bash
npm install -g pnpm
```

## 开发环境Linux

```bash
# 安装
sudo apt update
sudo apt install nodejs npm -y
sudo npm install -g pnpm

# 查看
node -v
pnpm -v
```

## 创建 React 项目

1、创建 React 模板工程（基于 Vite），推荐使用 Vite，轻量、快速。

```bash
# 使用国内源
export NODE_MIRROR=https://mirrors.tuna.tsinghua.edu.cn/nodejs-release/

# 使用模板创建项目
# 如果你是新手，选择JavaScript（不要选 TS），不要启用 rolldown（选 No）
pnpm create vite@latest my-react-app -- --template react

# 安装工程依赖
cd my-react-app
pnpm install

# 运行项目，然后根据控制台给出的URL输入浏览器打开
pnpm dev
```

2、项目结构（最常见）

```bash
my-react-app/
│
├── public/             # 静态资源
│
├── src/
│   ├── assets/         # 图片、图标
│   ├── components/     # 公共组件
│   ├── pages/          # 页面
│   ├── App.jsx         # 根组件
│   ├── main.jsx        # 入口文件
│   └── index.css       # 全局样式
│
├── package.json        # 依赖、脚本
└── vite.config.js      # Vite 配置
```

JSX = JavaScript + HTML 的混合语法。

```jsx
const element = <h1>Hello React</h1>;

const name = "Tom";
return <p>Hello {name}</p>; // 变量用{}插入
```

2、组件，React 的核心是 **组件**。有两种写法：

```jsx
// (1) 函数组件（推荐）
function Hello() {
  return <h1>Hello</h1>;
}

// 导出组件
export default Hello;

// 调用组件，在 App.jsx 中使用：
import Hello from "./components/Hello";
function App() {
  return <Hello />;
}
```

3、组件传参

```jsx
// 组件接收参数：
function UserCard(props) {
  return <h3>Name: {props.name}</h3>;
}
// 结构赋值写法：
function UserCard({ name }) {
  return <h3>Name: {name}</h3>;
}

// 参数传递: 父组件 → 子组件
export default function App() {
  return <UserCard name="Tom" />;
}
```

4、State（组件内部状态）

```jsx
// State（组件内部状态），使用 React 的 Hooks：useState
import { useState } from "react";
function Counter() {
  const [count, setCount] = useState(0);
  return (
    <>
      <p>{count}</p>
      <button onClick={() => setCount(count + 1)}>Add</button>
    </>
  );
}
```

## 打包成桌面应用（Electron / Tauri）

1、Electron

优点：功能强大（支持 Node API）

缺点：体积大（100MB 起步）

```jsx
// Electron（简单但大）
pnpm add electron -D

// 启动一个 Electron 主进程
// 加载 Vite 打包的 dist/ HTML
```

2、Tauri（强烈推荐）

优点：

- 体积非常小（3~8MB）
- 性能高
- Rust 加载前端

```jsx
// Tauri（更轻量）

// 安装 Tauri CLI：
pnpm add -D @tauri-apps/cli

// 初始化
pnpm tauri init

// 运行
pnpm tauri dev

pnpm run build

```




# Excalidraw草稿软件部署

1、去搜 excalidraw github 仓库，并以 zip 形式下载下来，解压备用。

or 网盘备份: excalidraw-master-yarn.zip

2、按照仓库包 README.md 快速部署，或者网盘备份包里 《使用方法.md》。



# 流式笔记引擎


[[APP-流式笔记引擎方案设想_11_14_2025_105401_AM.html]]

1、软件整体架构

```python
React（前端 UI）
   ↓ 事件通信 (emit/listen/invoke)
Tauri Runtime
   ↓ Rust Commands
Rust Core Engine（流式笔记引擎）
   ↓
内容数据库（SQLite + 文件系统）

Rust 引擎负责一切内容加载/缓存/调度，前端只负责展示——这与现代游戏引擎结构相同，性能最佳。
```

2、笔记目录结构

```python
root/
  notebooks/
    notebook1/
      notebook.meta.json
      nodes/
         000001.json
         000002.json
         ...
      frames/
         12/
           frame001.png
           frame002.png
         20/
           frame001.png
      media/
         xx_audio.mp3
 
 简单、直接、可扩展、可移植到移动端。
```








# bottom




