

# 快速学习路线图


https://www.bilibili.com/video/BV1AK4y1c7EX


**一、熟悉PL开发流程**

基础小实验、学会仿真基本语法，时序图——verilog代码能够相互转换。

**二、基础IP核使用**

1、Clock：掌握IP核配置，以及如何分频倍频
2、FIFO：掌握FIFO核配置，FIFO读写时序
3、RAM：掌握RAM核配置，RAM读写时序

学习基础IP核，为后续项目做准备，这三个基础IP核，项目会经常用到。


**三、低速协议(UART/SPI/IIC)、外设调试**（10~15天）

1、UART：可以做到绘制串口时序图，并根据时序图写出代码。
2、学习 Xilinx 调试工具 ILA、VIO 用法以及调试技巧。
3、IIC/SPI接口：找几款 IIC/SPI 接口的外设传感器，学会查看外设芯片的数据手册，联合 ILA/VIO 调试外设，提高程序调试能力。


**四、AXI4总线**（5天~7天）

AXI4有一大堆信号，慢慢理清信号之间的关系，AXI4总线需要学习：
1、AXI4、AXI4_Stream、AXI4_Lite 的区别、理解握手过程；
2、AXI4_Stream、AXI4_Lite 总线，看懂端口信号、看懂时序图即可；
3、AXI4总线：这是重点学习对象，不仅需要弄明白端口信号及时序，还要熟练写出AXI4主机源程序。

Xilinx 官方提供了三种 AXI4 总线的源码及时序仿真图，只需要学习时序图即可。官方提供的 AXI4 主机源码写的非常混乱，不建议花过多精力去学习它的源码。


**五、DDR3、DDR4**（7天~10天）

DDR3在实际项目中经常被用到，尤其是图像处理，DDR3是图像处理的灵魂。
DDR3重点学习AXI4接口，通过 AXI4 总线读写DDR3。关于 Native 接口，了解时序即可。
学习DDR3的时候，会遇到很多问题，记录学习过程中遇到的问题，如果面试官提问讲述你项目中遇到的问题，可以轻松应答。


**六、选择方向**

上述内容学习完了，可以选择一个方向深入学习，选择方向非常重要。
**常见的方向**：图像处理、通信/数字信号处理、高速接口、深度学习/机器视觉/AI、原型验证等等。
FPGA方向多，内容也很多，做通信的可能不知道 VGA/HDMI接口，做图像的也可能不知道 ASK、FSK 等等。

**FPGA图像处理**
一般是做图像预处理，分为图像算法和图像接口。
常见的图像接口有 mipi、hdmi、vga、sdi、lvds 等等。
图像预处理算法一般是 sobel 边缘检测、直方图等等。
推荐图像算法入门书籍，韩斌老师的《Matlab与FPGA图像处理》


**高速接口**
大部分公司做的高速接口，都是调用一些IP核，比如 aurora、srio、xdma 核等，这个方向比较看重调试经验。
PCIE、SRIO 等协议有专门的公司在做，做协议难度较大，也比较底层，需要时间来沉淀。



# DDR3





草稿：[[ZYNQPL-DDR3.excalidraw]]


FPGA：DDR保姆级教程、轻松掌握DDR
https://www.bilibili.com/video/BV1Lx4y1F7D


基础-什么是系统时钟？什么是参考时钟？什么是用户时钟？

基础-DDR3 MIG 核如何配置

基础-官方 example design 解读（Native接口）

基础-如何搭建DDR3仿真模型

基础-自定义用户端仿真

进阶-官方 example design 解读(AXI4接口)

进阶-如何上板调试

进阶-如何将DDR3封装成FIFO




## DDR3基础知识


**DDR3工作特点**：
- 由于其是电容型存储，所以需要周期性刷新充电；
- 时钟上升沿和下降沿都会传输数据；
- 支持突发传输，突发长度一般为 8 beats。

**DDR3的存储特点**：Bank、行地址、列地址
行列：行和列组成一个表格，表格里面的每一格，就是最小单元，最小单元有 8bit、16bit 等等。
Bank：上面行列组成一个表格，如果DDR3有8个表格，那么就有8个Bank。


**DDR3容量计算**：Bank数量 x 行数量 x 列数量 x 存储单元容量
比如 Bank address 位宽为3，Row address 位宽为14，Column address 位宽为12，
则其容量为：2^13 x 2^14 x 2^12 x 16bit


**DDR3的命名**
以镁光的DDR3为例，MT41J64M16JT-125-G，
根据其数据手册得知 [[C598835_DDR+SDRAM_MT41J64M16JT-125-G.pdf]]，
![[Pasted image 20260327144451.png]]


容量，如上图橘色表格部分，
容量 = 存储单元数 x 每个单元位宽
👉 **1024 Mbit（= 1 Gbit）指的是“单颗 DRAM 芯片”的容量**，也就是单个颗粒本身的存储容量。
![[Pasted image 20260327151704.png]]




先统一单位：1.25 ns = 1.25 × 10⁻⁹ s

代入计算：
$$
f = \frac{1}{1.25 \times 10^{-9}} = 0.8 \times 10^9 = 800 MHz
$$


👉 **这是时钟频率（CK）**
但 DDR 是：**Double Data Rate（双沿传输）**
✔ 所以最终传输带宽为：800 MHz × 2 = 1600 MT/s



**DDR3输入数据掩码**
LDM、UDM：LDM控制DQ0~DQ7，UDM控制DQ8~DQ15
比如你往DDR3里写入一个16bit数据，
如果LDM、UDM都为0，那么16bit数据可以一次性全部写入DDR3，
如果某个为高，其对应的字段就会被屏蔽，即不能写入DDR3。


<font color=blue>既然这个掩码这么麻烦，加上本来数据线就有16根，为什么还要这个掩码拆开来控制数据写入？
</font>

👉 **“既然有 16 根数据线，为什么还要额外加 DQM（LDM/UDM）来做掩码？”**
👉 **DQM（LDM/UDM）的存在，是为了支持“部分写（partial write）”，避免昂贵的读-改-写（RMW）操作，同时保证总线效率。** 比如你只想改其中 8 bit（比如一个 byte）。

**如果没有 DQM**
👉 你必须：
1️⃣ 先从 DDR 读出 16bit  
2️⃣ 在 CPU/逻辑里改其中 8bit  
3️⃣ 再把 16bit 写回去
👉 这就是经典：**Read-Modify-Write（读-改-写）**

✅ **有了 DQM，可以这样**：不需要读出来修改再写回去，直接写里面的局部字段。
👉 写一个 16bit 数据，只想写低8bit：
LDM = 0（写）  
UDM = 1（屏蔽）
👉 DDR 会只更新 `DQ[7:0]`，`DQ[15:8]` 保持原值。
✔ **完全不需要读！**


👉 **DDR 是 burst 传输（连续数据流）**
👉 DDR 不是一次传一个数据，而是一次 burst（8 / 16 个 beat）
👉 数据线必须 **每个 cycle 都稳定输出固定宽度**


**AXI 的 WSTRB（你应该见过）**
👉 AXI 写通道有：`WSTRB[n]`，本质就是 **DQM 的上层版本**
👉 DQM 的作用：**在不改变总线宽度的前提下，实现细粒度写入**



## DDR3时钟分析


![[Pasted image 20260327154702.png]]

如上图所示，我们只需要写好【用户端】和【MIG IP核】之间的时序即可非常简单的读写DDR3了。

![[Pasted image 20260327231629.png]]


<font color=blue>MIG IP核有2个输入时钟，一个是 sys_clk，一个是 ref_clk，直接一个 sys_clk 不好吗？为什么还要多一个 ref_clk ，照道理说参考时钟也能从系统时钟这里取呀。
</font>

**核心原因**：**DDR PHY 需要“高精度参考时钟**”
DDR3/DDR4 的 PHY 里有一堆东西：
- 延迟线（IDELAY / ODELAY）
- 校准电路（calibration）
- DQS 对齐
- write leveling
- read gate training
👉 这些模块有一个共同特点：
👉 **它们需要一个“稳定、低抖动、固定频率”的参考时钟**



✅ **时钟比例关系**
DDR3芯片工作的时钟与用户端时钟有一个比例关系：
DDR3芯片工作的频率:用户端时钟频率 = 4:1 或者 2:1。
当DDR3芯片工作的时钟为800MHz的时候，比例只能为 4:1。

<font color=blue>至此，我发现一个现象，用户时钟总是比DDR3时钟低，而且至少低一倍。
</font>

因为控制器在做“并行化 + 降频处理”：
👉 实际发生的是：
```txt
DDR：窄总线 + 高速（串行化方向）
用户：宽总线 + 低速（并行化方向）
```

🔹 4:1 模式（最常见）
👉 MIG 会把数据“拼宽”：
```txt
DDR：16 bit × 800 MHz × DDR(2)
↓
用户侧：128 bit × 200 MHz
```
👉 验证一下带宽守恒：
```txt
16 × 1600 = 25600 Mbit/s
128 × 200 = 25600 Mbit/s
```

**为什么必须这么做？为什么要串并转化？（核心原因）**

❌ FPGA 逻辑跑不了 800MHz，FPGA fabric 常见极限为 200~300 MHz，这也顺便解释了 "**当DDR3芯片工作的时钟为800MHz的时候，比例只能为 4:1，不能是2:1**"。

👉 所以对于FPGA这边，**频率越低 → 数据越宽**



## MIG IP核的配置

Xilinx FPGA 芯片分为两种：其一是A7、K7这种纯FPGA，另一种是ZYNQ系列。
- 纯FPGA中，用户端想往DDR3写数据，直接往 MIG IP 核写就可以了；
- ZYNQ系列，如下图，DDR3是挂载PS端的DDR3控制器上的，PL用户逻辑直接往 AXI_HP 写数据就行。

![[Pasted image 20260327163903.png]]


---

**用户逻辑与MIG之间**的接口有两种：**Native接口 和 AXI4 接口**

![[Pasted image 20260327222631.png]]

---

✅ **系统时钟来源**：
- No Buffer —— FPGA内部直供时钟
- Single-Ended —— 单端时钟
- Differential —— 差分时钟

![[Pasted image 20260327230404.png]]

---

✅ **参考时钟**

参考时钟必须为200MHz,
如果系统时钟刚好也200M, 则可以选择系统时钟, 
否则不能选系统时钟作为参考时钟的输入来源。

![[Pasted image 20260327231118.png]]


---

✅ **IBUF原语**
IBUF它能使输入的信号更加稳定，减少抖动等等。

![[Pasted image 20260327232729.png]]

🟡 2. Single-Ended
外部晶振 → FPGA引脚 → IBUF → MIG
✔ 外部输入  
✔ 单端信号（比如普通50MHz晶振）
👉 MIG 会帮你插 IBUF
你这个系统其实是：50MHz（外部） → IBUF → PLL → 200MHz（内部） → MIG
👉 MIG 看到的是：“内部已经处理好的干净时钟”，所以选 No Buffer。
MIG 这个选项本质在问：
👉 **“这个时钟，是不是已经在 FPGA 内部处理好了？”**


🟢 **情况1：内部时钟**（你之前那个场景）
外部晶振 → IBUF → PLL/MMCM → BUFG → MIG
👉 MIG 看到的是：
“已经进入全局时钟网络的内部时钟”
✔ 时钟已经：
- 经过 clock manager（PLL/MMCM）
- 经过 BUFG 分发
👉 ✅ **选：No Buffer**


🔵 **情况2：直接用外部时钟**（你现在问的这个）
外部时钟 → FPGA引脚 → IBUF / IBUFDS → MIG
👉 MIG 看到的是：
“刚进芯片，还没进入全局时钟网络”
👉 ❗这里的关键不是“干不干净”，而是是否已经进入 FPGA 的**全局时钟网络（BUFG）**
No Buffer 的本质是：**这个时钟已经是“全局时钟资源（global clock）**”


👉 MIG 需要的不是“IBUF”，而是“合法的时钟路径终点”
🟢 外部时钟路径：PAD → IBUF → BUFG → MIG
👉 关键点是：✔ 是否进入 BUFG
👉 选 No Buffer，意味着“**我保证这个时钟已经是 BUFG 后的全局时钟**”
👉 选 `Single-Ended / Differential`，意味着：
“**这个时钟还是 IO 级别，请你（MIG）帮我做 IBUF + BUFG**”
✅ **MIG要BUFG之后的时钟（是否经过IBUF不重要）**


<font color=blue>本来应该选 No Buffer 的，但是选成 Single-Ended 了，会发生什么？
</font>

🔵 Single-Ended：MIG **会帮你自动插入 IBUF**
假设你的实际情况是：
50MHz 外部晶振 → IBUF → PLL → 200MHz → BUFG → MIG
实际路径会变成：PLL输出 → BUFG → （逻辑线）→ IBUF ❌ → MIG

💥 但致命问题是：**IBUF 只能接 IO PAD，不能接内部信号！**
ERROR: IBUF input must be connected to a package pin

🧠 判断口诀
时钟来自哪里？
来自 FPGA 内部（PLL/MMCM） → ✅ No Buffer
来自 FPGA 引脚（晶振）     → ✅ Single-Ended / Differential


<font color=blue>MIG 的 sys_clk / clk_ref / ui_clk 之间到底是什么关系？
</font>

🎯 一句话总览
> **sys_clk = MIG 主工作时钟（驱动控制器 + PHY）**  
> **clk_ref = PHY 校准用参考时钟（给 IDELAY 等）**  
> **ui_clk = 给用户逻辑用的接口时钟（降频后的稳定时钟）**


```txt
        外部晶振
            │
         (IBUF)
            │
        PLL / MMCM
            │
      ┌───────────────┐
      │               │
   sys_clk        clk_ref
      │               │
      ▼               ▼
   MIG核心        PHY校准模块
      │
      ▼
   分频 / CDC
      │
      ▼
    ui_clk  →  给用户逻辑（AXI接口）
```












<font color=blue>为什么IO级别的时钟不能直接作为MIG输入？
</font>

IO时钟 ≠ 时钟网络：PAD → IBUF → （普通布线）→ 逻辑
👉 这条路径的特点：
- ❌ 走的是 **普通 routing 资源**
- ❌ 延迟不可控
- ❌ skew（不同路径延迟差）很大
- ❌ jitter 被放大
- ❌ 不能保证全芯片一致

而 BUFG 后是这样：PAD → IBUF → BUFG → （专用全局时钟网络）→ 全芯片
👉 这条路径的特点：
- ✅ 专用低skew网络
- ✅ 延迟可预测
- ✅ 抖动受控
- ✅ 专门为时钟设计

⚠️ **MIG 为什么“特别严格”？**
因为它不是普通逻辑，而是 **DDR 控制器（强实时 + 强时序约束）**
比如DDR3数据窗口可能只有 **几百 ps**
✅ BUFG 的作用是把“一个时钟”变成“**全芯片一致的时间基准**”
MIG 其实在做一件事：
👉 建立 FPGA 内部逻辑 与 DDR PHY 的“**时间对齐关系**”

如果时钟不稳定，MIG 无法判断：
- 数据什么时候采样？
- 延迟该调多少？
- DQS 和 CLK 如何对齐？


<font color=blue>为什么 DDR 必须用 DQS（数据选通信号），而不是只靠 CLK？
</font>

❌ **只靠 CLK，数据采样会失败（窗口太小 + skew太大）**  
✅ **必须用 DQS，让“数据自己带时钟”**

**如果只用 CLK，会发生什么？**
理想情况你可能会这样想：CLK ↑ → 采样 DQ
但现实是：CLK 和 DQ 不是同时到达 FPGA 的，因为走线长度、温度、电压等因素
结果就是：CLK 到了，但 DQ 还没稳定 or DQ 已经过了稳定区

🔥 一个非常关键的直觉
> **CLK 是“我什么时候采样”**  
> **DQS 是“数据什么时候准备好了”**

👉 所以真正的逻辑是：
不是用 CLK 去找数据  
而是用 DQS 告诉你：**现在可以采了**
MIG 在做一件非常复杂的事：用 DQS 去“对齐数据窗口”

DDR 不再相信“全局时间”，而是让“**数据自己定义时间**”


<font color=blue>为什么 DQS 在读和写时方向是反的？（读是输入，写是输出）
</font>

🎯 一句话结论
> ✅ **谁发送数据，谁就发送 DQS**  
> 👉 因此：
> - 写（FPGA → DDR）：DQS 由 FPGA 输出
> - 读（DDR → FPGA）：DQS 由 DDR 输出


👉 （FPGA → DDR）FPGA 在发数据，所以：
- FPGA 知道数据什么时候稳定
- FPGA 可以对齐 DQ 和 DQS
👉 ✅ **FPGA 输出 DQS**
DDR 实际上做了一件非常聪明的事：**把“时间控制权”交给数据源**


<font color=blue>为什么 DQS 需要“中心对齐（center-aligned）”而不是“边沿对齐”？
</font>

🎯 一句话结论
> ❌ **边沿对齐：采样点在最危险的位置（边界）**  
> ✅ **中心对齐：采样点在最安全的位置（数据眼中心）**


📊 数据眼（Data Eye）：数据眼就是黑色那一坨，👉 中间最稳，两边最危险
```txt
时间轴 →

DQ:   ────████████────
            ↑
         最稳定区域（center）
```


**举个具体例子（DDR3）**
- 一个 bit 周期：1.25ns
- 半个周期：0.625ns
👉 **把 DQS 延迟**：→ 正好落在数据中间


<font color=blue>为什么 DDR 是“双沿采样（DDR）”，但 DQS 却不是简单的2倍频时钟？
</font>

🟢 DQS不是“频率工具”，而是“**时序对齐工具**”

```cpp
// 为什么“DQS看起来像 2× 时钟”？
// 因为DQS每个数据边界 → DQS 都会翻转
DQ :   D0   D1   D2   D3
DQS:   ↑    ↓    ↑    ↓
```


<font color=blue>为什么 DQS 在 FPGA 内部要经过 IDELAY / ISERDES，再做采样？
</font>

🎯 一句话结论
> ✅ **IDELAY：用来“把采样点移到数据眼中心”**  
> ✅ **ISERDES：用来“在高速域正确采样并降速到逻辑域”**

IDELAY 负责“调准时间”，ISERDES 负责“**抓住数据**”


---

MIG 全称为 Memory Interface Generator
MIG = “DDR接口自动实现器（Controller + PHY + Calibration）”

<font color=blue>既然 MIG 这边就包含PHY了，那DDR3那边的颗粒算什么？我以为DDR3颗粒那边才算PHY。
</font>

🎯 DDR3 颗粒本身 ≠ PHY，**它是“被 PHY 驱动的存储设备”**

🔬 正确的系统分层是这样的：
```txt
[ FPGA (MIG) ]  ←→  [ DDR3 芯片 ]
      │                    │
      │                    └── 存储阵列 + 简单I/O逻辑
      │
      ├── Controller（控制器）
      ├── PHY（物理层）  ← ★在这里
      └── Calibration（校准）
```

**为什么 PHY 必须在 FPGA 侧？**

⚡ 原因1：**板级走线误差（skew）**
FPGA → DDR 的每一根线长度不同
👉 skew = 几十 ~ 几百 ps
👉 只有 FPGA 知道这个 skew  
👉 所以必须 FPGA 来补偿


⚡ 原因2：**时钟不是全局共享的**
- DDR3 没有全局统一时钟
- 是 source-synchronous（DQS）
👉 谁接收数据，谁就要做采样调整  
👉 → FPGA 必须有 PHY


⚡ 原因3：**校准是动态的**
- 温度变化
- 电压变化
- 工艺变化
👉 MIG 会 runtime calibration  
👉 DDR3 芯片不会做这个

**你可以把整个过程抽象成**：
```txt
问题：数据什么时候稳定？
解决：用 DQS 标记时间
优化：用 IDELAY 找最佳采样点
执行：用 ISERDES 采样
```


<font color=blue>MIG 是怎么“看到数据眼”的？
</font>

👉 **它并不是“看波形”**  
👉 而是用“数字方法”去“扫”出来

👉 DDR 有专门的训练模式
如何判断“当前 delay 是否可用”？
```txt
if 读出来 == 预期数据:
    标记为 PASS
else:
    标记为 FAIL
```

最终会得到一个类似这样的结果：
```txt
tap:  0 1 2 3 4 5 6 7 8 9 10 11 12 ...
res:  F F F P P P P P P P  P  F  F


🎯 这就是数据眼！
            ←-- data eye --→
            P P P P P P P  P


MIG 怎么选最终采样点？
取中间：center = (first_pass + last_pass) / 2
比如PASS区间：tap 3 ~ tap 10
最终选择：    tap = (3+10)/2 = 6
```


## DDR3仿真平台（Native接口）

1、如果你是纯FPGA平台，建议使用 Modelsim 仿真，也就是将 Modelsim 和 Vivado 关联起来，这样可以大大提高仿真的速度。

2、搭建仿真模型，就是在 TestBench 顶层添加一个 ddr3_model.sv 文件，该文件的作用是模拟DDR3物理芯片。如果没有该文件，直接仿真MIG会失败，DDR3初始化信号 init_calib_complete 会一直拉不高。

### 方法1：最简单


1、配置完 MIG IP 核，生成官方 example 工程，在官方工程的 import 目录下，找到以下文件：

```txt
ddr3_model.sv
ddr3_model_parameters.vh
example_top.v
sim_tb_top.v
wiredly.v
```




## DDR3仿真平台（AXI4接口）

ZYNQ PS和PL交互专题介绍
第一节：介绍PS端接口AXI_GP、AXI_HP、AXI_ACP。
第二节：介绍AXI协议：axi_lite、axi_stream、axi_full
第三节：基于axi_lite的PS和PL项目，讲解使用如何axi_lite方法实现交互，带你做demo。
第四节：基于axi_full的PS和PL交互项目。
第五节：基于AXI_DMA的PS和PL交互项目




## PL读写PS端DDR3














# AXI4

## AXI4_LITE PS 和 PL 交互


在 Xilinx 提供的平台中，PS和PL交互方式有很多种，比如官方的 AXI DMA 等等IP核。如果不想使用 ip 核，也可以自己手写一个 AXI4 的时序代码，采用 AXI_HP 接口。初学者先学 AXI4_Lite 的方式，之后其他方式一通百通。

外设：DS18B20 温度传感器（三根线：地、电、数据）

![[Pasted image 20260329100603.png]]

（1）AXI4_Lite 基础知识；
（2）学习 Xilinx 官方 AXI4_Lite 从机模板代码，以及如何根据需要修改它。
（3）如何驱动 DS18B20 温度传感器。


---

**AXI_GP 称为接口，AXI4_Lite 称为协议**，这两个别搞混了。

1、PS端共有4个 AXI_GP 接口，其中两个PS为主PL为从，另外两个相反；
2、PL 这边作为Slave，那么可以认为 PL 就是 PS 的外设；
3、PL 既然是外设，那么PS端就有对应的地址和寄存器。

4、其中**寄存器基地址就等同于PL端模块的ID号**，不然如果有两个模块就难以区分了。


![[Pasted image 20260329101820.png]]


如上图所示，AXI4_Lite 需要重点关注右边红框中的几个信号。

---

**作为PL端，这些信号如何接收数据？**

👉 **PS写入PL寄存器**
比如：Xil_Out32(0x4300_0000 + 0x00, 1)
PL端的从机模块，收到的写地址 awaddr 为0，写数据 wdata 为1。

比如：Xil_Out32(0x4300_0000 + 0x04, 2)
PL端的从机模块，收到的写地址 awaddr 为4，写数据 wdata 为2。

其中还有一个握手机制，比如 AXI4_Lite 还有个 ready 信号，如果该信号为低，则表明PL这边还没准备好，写地址和写数据这两个信号会一直保持。直到为高，表示PL准备好了，可以接收写数据和写地址这两个信号了。

👉 **PS读取PL寄存器**

比如：Xil_In32(0x4300_0000 + 0x04)
PL端的从机模块，收到的读地址 araddr 为4，然后PL将 rdata 发送给PS，rdata 值就是寄存器值。







# Bottom







