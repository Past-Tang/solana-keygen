<div align="center">
  <img src="assets/logo.svg" alt="Solana Keygen Generator" width="680"/>

  # Solana Keygen Generator

  **Solana 靓号密钥对生成器**

  [![Python](https://img.shields.io/badge/Python-3.8+-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
  [![Solana](https://img.shields.io/badge/Solana-Ed25519-14f195?style=flat-square)](https://solana.com)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
</div>

---

## 项目概述

Solana Keygen Generator 是一个基于 Python 的 Solana 靓号（Vanity Address）密钥对生成工具。通过多线程并发暴力搜索，生成公钥满足指定前缀和/或后缀条件的 Solana Ed25519 密钥对。支持实时显示搜索速度、尝试次数和预计剩余时间。项目还包含一个基于 OpenCL GPU 加速的第三方靓号生成器 `SolVanityCL`。

## 技术栈

- **Python**: 核心编程语言
- **solders**: Solana Rust SDK 的 Python 绑定，用于生成 Ed25519 密钥对
- **base58**: Base58 编码/解码（Solana 地址标准格式）
- **ThreadPoolExecutor**: Python 标准库多线程并发
- **argparse**: 命令行参数解析
- **SolVanityCL** (可选): 基于 OpenCL 的 GPU 加速靓号生成器

## 功能特性

- **前缀匹配** -- 生成公钥以指定 Base58 字符串开头的密钥对
- **后缀匹配** -- 生成公钥以指定 Base58 字符串结尾的密钥对
- **前后缀组合** -- 同时指定前缀和后缀条件
- **多线程并发** -- 默认 16 线程并行搜索，可自定义线程数
- **实时状态监控** -- 每秒刷新显示：尝试次数、实时速度、平均速度、运行时间、预计剩余时间
- **ETA 预估** -- 基于 Base58 字符集概率 `(1/58)^N` 计算预期搜索量，动态估算剩余时间
- **Base58 私钥输出** -- 找到匹配密钥对后输出 Base58 编码的完整私钥
- **GPU 加速** (SolVanityCL) -- 可选的 OpenCL GPU 加速方案，大幅提升搜索速度

## 安装说明

1. 克隆仓库到本地：
   ```bash
   git clone https://github.com/Past-Tang/solana-keygen.git
   cd solana-keygen
   ```

2. 安装依赖：
   ```bash
   pip install solders base58
   ```

3. （可选）GPU 加速版本：
   ```bash
   cd SolVanityCL-master
   pip install -r requirements.txt
   ```

## 使用方法

### CPU 多线程版本

```bash
# 生成以 "ABC" 开头的公钥
python mian.py -prefix ABC

# 生成以 "xyz" 结尾的公钥
python mian.py -suffix xyz

# 同时指定前缀和后缀
python mian.py -prefix AB -suffix CD

# 自定义线程数（默认 16）
python mian.py -prefix ABC -num_threads 32
```

### 命令行参数

| 参数 | 类型 | 默认值 | 说明 |
|:---|:---|:---|:---|
| `-prefix` | string | None | 公钥前缀（Base58 格式） |
| `-suffix` | string | None | 公钥后缀（Base58 格式） |
| `-num_threads` | int | 16 | 并发线程数 |

### GPU 加速版本 (SolVanityCL)

```bash
cd SolVanityCL-master
python main.py --help
```

## 运行示例

```
$ python mian.py -prefix ABC -num_threads 16

当前进度: 1,234,567 次尝试 | 实时速度: 45,000次/秒 | 平均速度: 42,000次/秒 | 已运行: 29秒 | 预计剩余时间: 2.35分钟

==================================================
Found matching keypair after 2,345,678 attempts!
Public Key: ABCxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Private Key: 5xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
==================================================
```

## 搜索难度参考

搜索难度与前缀/后缀长度呈指数增长（Base58 字符集，每位 1/58 概率）：

| 条件长度 | 预期尝试次数 | 16线程 ~40K/s 预计时间 |
|:---|:---|:---|
| 1 位 | ~58 | 瞬间 |
| 2 位 | ~3,364 | < 1 秒 |
| 3 位 | ~195,112 | ~5 秒 |
| 4 位 | ~11,316,496 | ~5 分钟 |
| 5 位 | ~656,356,768 | ~4.5 小时 |
| 6 位 | ~38 亿 | ~11 天 |

## 项目结构

```
solana-keygen/
├── mian.py                    # CPU 多线程靓号生成器（主程序）
├── SolVanityCL-master/        # GPU 加速靓号生成器（第三方）
│   ├── main.py                # GPU 版本入口
│   ├── core/                  # 核心模块（CLI、OpenCL 内核）
│   ├── requirements.txt       # GPU 版本依赖
│   ├── Dockerfile             # Docker 容器化支持
│   └── FAQs.md                # 常见问题
├── assets/
│   └── logo.svg               # 项目 Logo
├── LICENSE                    # MIT 许可证
└── README.md
```

## 核心算法

### 搜索流程
1. 启动 N 个工作线程，每个线程独立循环生成 `Keypair()`
2. 将公钥转为 Base58 字符串，检查是否满足前缀/后缀条件
3. 任一线程找到匹配结果后设置 `threading.Event`，所有线程停止
4. 状态监控线程每秒读取全局计数器，计算速度和 ETA

### 线程安全
- 使用 `threading.Lock` 保护全局计数器 `attempts_count`
- 每个工作线程本地累计 100 次后批量更新全局计数器，减少锁竞争
- 使用 `threading.Event` 实现线程间停止通知

## 依赖项

| 包 | 用途 |
|:---|:---|
| solders | Solana Rust SDK Python 绑定，Ed25519 密钥对生成 |
| base58 | Base58 编码/解码 |

## 常见问题

### 搜索速度太慢？
- 增加 `-num_threads` 参数值
- 使用 GPU 加速版本 `SolVanityCL-master`
- 减少前缀/后缀长度

### 找不到匹配的密钥对？
条件越长搜索时间呈指数增长。建议前缀+后缀总长度不超过 4-5 位。

### 私钥格式是什么？
输出的私钥为 Base58 编码的 64 字节完整密钥（前 32 字节为私钥，后 32 字节为公钥）。可直接导入 Phantom、Solflare 等钱包。

## 安全注意事项

- 生成的私钥是钱包的唯一凭证，请妥善保管
- 请勿在不安全的网络环境下运行本工具
- 生成完成后及时清除终端历史记录中的私钥信息
- 建议在离线环境下生成重要钱包的密钥对

## 许可证

[MIT License](LICENSE)

## 免责声明

本工具仅供学习研究使用。使用者需自行承担所有风险，请妥善保管生成的私钥。