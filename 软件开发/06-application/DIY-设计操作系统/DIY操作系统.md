





# scheduler_up.c


灶台、小推车、库房、菜市场都是容器

![[Pasted image 20260606222714.png]]

## 进程A脱离CPU，CPU运行其他任务。




## 厨房菜市场模型

<font color=blue>我想把CPU寄存器比喻成厨房的各种锅碗瓢盆容器，cache比喻成厨房里容量更大的菜篮子，内存比喻成菜市场，然后硬盘比喻成蔬菜生产基地，这样方便我把整个计算机体系串联起来形成一个有机整体，而不是零散的知识。相当于CPU就是厨房，不同的线程就是不同的厨师，比如线程A对应着厨师A，线程B对应着厨师B。并且多核 CPU也能这样比喻，多核CPU里，一个物理封装CPU里有多核，相当于一个厨房里有多个灶台，每个灶台都有一块属于自己的一点小空间，这点小空间里有各种小容器，这些小容器(寄存器)可以存放当前厨师未加工的食材，也可以存放加工好的食材，另外厨房里的菜篮子是厨房里所有灶台共享的存储空间。每个厨师都有自己要做的菜，当然每个厨师都有自己的食材清单，比如厨师A的食材清单里有菠菜，并且菠菜存放在菜市场(内存)里。我们先以单核为例，即厨房里只有一个灶台，当厨师A占用厨房炒菜时，它需要菠菜，发现灶台小容器里没有菠菜食材，于是到厨房的菜篮子里(cache)找菠菜，菜篮子里没有，最后才会去菜市场(内存)里获取菠菜。
</font>


**一颗CPU**=一个厨房；**CPU多核**=厨房内的多个灶台；
**CPU通用寄存器** = 每个灶台自带专属锅碗瓢盆；
CPU系统寄存器＝整间厨房共用的管理工具；
**L1 Cache：单个灶台侧边小提篮（每核私有）**，只给本灶台厨师用；
**L2 Cache：同 CPU 内几个灶台共用中型菜筐**；
**L3 Cache：同一间厨房内部，所有灶台共享的食材小推车**；
DRAM = 厨房外的库房；
磁盘 = 菜市场，货源最全、调取最慢；
**进程** = 一间独立封闭后厨包厢；**线程** = 包厢里干活的厨师；

**厨师与食材**：每个厨师都有自己要做的菜，当然每个厨师都有自己的食材清单，比如厨师A的食材清单里有菠菜，并且菠菜存放在菜市场(内存)里。我们先以单核为例，即厨房里只有一个灶台，当厨师A占用厨房炒菜时，它需要菠菜，发现灶台小容器里没有菠菜食材，于是到厨房的菜篮子里(cache)找菠菜，菜篮子里没有，最后才会去菜市场(内存)里购买获取菠菜。

**Cache 命中**：需要的食材已经在任意一层菜篮里，直接取用，不用访问菜市场。

**缺页异常（MMU 缺页）**：包厢 (进程) 保管一张专属食材登记表（页表），这张表单理论覆盖菜市场全部摊位编号（32 位系统对应 4GB 完整虚拟地址空间），表单每条记录对应一种食材品名；很多条目只登记了食材名字，没有填写该食材在菜市场（物理内存）实际摆放摊位地址。然后当访问其中某个虚拟地址时，但有些条目只写了品名、没填写菜市场真实摊位地址，于是发生缺页异常。

**表有名、无实地 = 缺页；表里无名(属于无效地址) = 程序崩溃**。

外设中断：当外设中断来了，最终发给厨房里的某个灶台，此时并不是厨师来处理这个中断事件，而是厨房总管(OS内核)临时接管灶台，亲自处理突发事件。处理完之后，再把灶台归还给厨师。

- RT-Thread Smart：带 MMU，每个包厢自带登记表，存在缺页；
- RT-Thread Nano：无 MMU，没有虚拟登记表，虚拟地址 = 菜市场真实地址，永远不会触发缺页异常。

```cpp
void rt_schedule(void) { }
比如线程A调用 rt_schedule() 主动让出CPU;
```

---

## 工程管理技术


把函数作为模块导出，方便其他模块调用。
其实就是把函数名和函数地址打包，然后追加放到某个指定section里。

```cpp
RTM_EXPORT(rt_malloc);

#define RTM_EXPORT(symbol)                                            \
const char __rtmsym_##symbol##_name[] rt_section(".rodata.name") = #symbol;     \
const struct rt_module_symtab __rtmsym_##symbol rt_section("RTMSymTab")= \
{                                                                     \
    (void *)&symbol,                                                  \
    __rtmsym_##symbol##_name                                          \
};
```


rt_weak 修饰函数为弱函数，方便其他同名函数覆盖。

```cpp
rt_weak void *rt_malloc(rt_size_t size) { }

#elif defined (__GNUC__)            /* GNU GCC Compiler */
#define rt_section(x)               __attribute__((section(x)))
#define rt_used                     __attribute__((used))
#define rt_align(n)                 __attribute__((aligned(n)))
#define rt_weak                     __attribute__((weak))
#define rt_noreturn                 __attribute__ ((noreturn))
```




## 中断开关嵌套调用

<font color=blue>我发现一个现象，在 rt_schedule() 函数里，会有 rt_hw_interrupt_disable() 和 rt_hw_interrupt_enable() 成对出现，并且中间会继续调用子函数，然后子函数里也有成对的中断关和开，这样嵌套调用中断关和开，没有什么问题么？
</font>

结论：完全没问题！RT-Thread 就是故意设计成【允许嵌套关中断】的，这是安全且标准的做法。

rt_hw_interrupt_disable() 和 rt_hw_interrupt_enable() 不是简单的开中断关中断，而是：
**关中断 = 上锁，并返回当前锁状态**
**开中断 = 恢复之前的锁状态，不是直接全开！**
这叫 中断嵌套（Interrupt Nesting）

```cpp
level1 = rt_hw_interrupt_disable(); // 关第1层 → 中断关
{
    level2 = rt_hw_interrupt_disable(); // 关第2层 → 中断仍然关
    {
        level3 = rt_hw_interrupt_disable(); // 关第3层 → 还是关
    }
    rt_hw_interrupt_enable(level3); // 开第3层 → 仍然关
}
rt_hw_interrupt_enable(level2); // 开第2层 → 仍然关
rt_hw_interrupt_enable(level1); // 开第1层 → 真正打开！
```


**为什么要这样设计？**

因为你不知道调用的**子函数内部会不会也关中断**，如下：
```cpp
rt_schedule()
{
    关中断();
       ...
       调用子函数();  ← 子函数里也可能关中断
       ...
    开中断();
}
```

如果没有嵌套保护：子函数一开中断，**整个中断就突然打开了**，上层函数还以为中断是关的，直接崩溃！

重点：**enable 不是 “开启中断”，是 “恢复之前的状态”**，这就是嵌套安全的根本原因。


---

## rt_schedule 完整人话注释

```cpp
/**
 * 这个函数叫做：执行一次线程调度
 * 功能：挑一个优先级最高的厨师，立刻让他上灶台干活
 */
void rt_schedule(void)
{
    // 定义几个帮手：
    // level：用来存中断开关状态（关中断时用）
    // to_thread：下一个要上台的厨师
    // from_thread：现在要下台的厨师
    rt_base_t level;
    struct rt_thread *to_thread;
    struct rt_thread *from_thread;

    // 拿到【当前正在灶台干活的厨师】
    struct rt_thread *curr_thread = rt_thread_self();

    /*==================== 第一步：关中断，防止别人捣乱 ====================*/
    // 关闭【当前这个CPU核心】的中断（只关自己灶台，不关别人）
    // 并把原来的中断状态存起来，等下要恢复
    level = rt_hw_interrupt_disable();

    /*==================== 第二步：检查调度器是否允许切换 ====================*/
    // 如果调度器没上锁（允许换人）
    if (rt_scheduler_lock_nest == 0)
    {
        // 下一个最高优先级的厨师编号
        rt_ubase_t highest_ready_priority;

        // 如果【就绪队列里有厨师在排队等待上台】
        if (rt_thread_ready_priority_group != 0)
        {
            // 标记：是否需要把当前厨师塞回排队队列
            int need_insert_from_thread = 0;

            // 从排队队列里，挑出【优先级最高的厨师】
            to_thread = _scheduler_get_highest_priority_thread(&highest_ready_priority);

            /*==================== 核心判断：要不要把当前厨师赶下台？ ====================*/
            // 如果当前厨师【正在灶台上运行】
            if ((RT_SCHED_CTX(curr_thread).stat & RT_THREAD_STAT_MASK) == RT_THREAD_RUNNING)
            {
                // 情况1：当前厨师优先级 **比** 排队里最高的厨师 **更高**
                if (RT_SCHED_PRIV(curr_thread).current_priority < highest_ready_priority)
                {
                    // 不换人！继续让当前厨师干
                    to_thread = curr_thread;
                }

                // 情况2：优先级一样高，并且当前厨师**没有主动让位**
                else if (RT_SCHED_PRIV(curr_thread).current_priority == highest_ready_priority
                         && (RT_SCHED_CTX(curr_thread).stat & RT_THREAD_STAT_YIELD_MASK) == 0)
                {
                    // 还是不换人！继续让当前厨师干
                    to_thread = curr_thread;
                }

                // 情况3：有人优先级更高，或者优先级一样但你主动让位了
                else
                {
                    // 必须换人！
                    // 标记：当前厨师要被塞回排队队列
                    need_insert_from_thread = 1;
                }
            }

            /*==================== 真正开始换人 ====================*/
            // 如果要换的厨师 != 当前厨师（真的要换人）
            if (to_thread != curr_thread)
            {
                // 记录当前厨师为“即将下台的厨师”
                from_thread = curr_thread;
                // 把本核心的“当前厨师”改成新厨师
                rt_cpu_self()->current_thread = to_thread;

                // 如果需要把老厨师塞回排队队列
                if (need_insert_from_thread)
                {
                    rt_sched_insert_thread(from_thread);
                }

                // 清除“主动让位”标记
                if ((RT_SCHED_CTX(from_thread).stat & RT_THREAD_STAT_YIELD_MASK) != 0)
                {
                    RT_SCHED_CTX(from_thread).stat &= ~RT_THREAD_STAT_YIELD_MASK;
                }

                // 把新厨师从排队队列里移除（因为他要上台了）
                rt_sched_remove_thread(to_thread);
                // 把新厨师状态设为“运行中”
                RT_SCHED_CTX(to_thread).stat = RT_THREAD_RUNNING | (RT_SCHED_CTX(to_thread).stat & ~RT_THREAD_STAT_MASK);

                //==================== 真正执行上下文切换（换厨师！）====================
                // 如果不在中断里
                if (rt_interrupt_nest == 0)
                {
                    // 执行硬件级别的上下文切换
                    // 把老厨师的锅碗瓢盆打包
                    // 把新厨师的厨具摆上灶台
                    rt_hw_context_switch((rt_uintptr_t)&from_thread->sp,
                            (rt_uintptr_t)&to_thread->sp);

                    // 恢复中断
                    rt_hw_interrupt_enable(level);


#ifdef RT_USING_SIGNALS
                    /* 再次关闭中断（防止被打断） */
                    level = rt_hw_interrupt_disable();

                    /* 看一看：当前新上台的厨师，身上有没有挂着“待处理信号”标记 */
                    if (RT_SCHED_CTX(curr_thread).stat & RT_THREAD_STAT_SIGNAL_PENDING)
                    {
                        /* 有信号要处理！*/

                        /* 先把“有信号”这个标记擦掉（清0） */
                        RT_SCHED_CTX(curr_thread).stat &= ~RT_THREAD_STAT_SIGNAL_PENDING;

                        /* 打开中断 */
                        rt_hw_interrupt_enable(level);

                        /* 重点：
                         * 让当前线程 去处理它收到的所有信号
                         * 相当于：让厨师先看完小纸条，再继续炒菜
                         */
                        rt_thread_handle_sig(RT_TRUE);
                    }
                    else
                    {
                        /* 没有信号 → 直接开中断，什么都不做 */
                        rt_hw_interrupt_enable(level);
                    }
#endif /* RT_USING_SIGNALS */

                    goto __exit;
                }
                else
                {
                    // 在中断里面切换，用中断版本的切换函数
                    rt_hw_context_switch_interrupt(...);
                }
            }
            /*==================== 不需要换人 ====================*/
            else
            {
                // 把当前厨师从队列移除
                rt_sched_remove_thread(curr_thread);
                // 状态设为运行中
                RT_SCHED_CTX(curr_thread).stat = RT_THREAD_RUNNING | ...;
            }
        }
    }

    // 恢复中断
    rt_hw_interrupt_enable(level);

__exit:
    return;
}
```


---
## rt_schedule 逻辑梳理

把上面的人话注释代码拷贝到 VSCode 里，借助编辑器的分层折叠来梳理出每一层的逻辑关系。
针对开源项目的代码，就更方便了，直接把不懂的代码块贴给AI，让AI用人话来解释一下。

```cpp
/**
 * 这个函数叫做：执行一次线程调度
 * 功能：挑一个优先级最高的厨师，立刻让他上灶台干活
 */
void rt_schedule(void)
{
	// caller 主动调用 rt_schedule() 换下一个人

	// 此时的 caller 要么是普通厨师, 要么是总管(用于占用灶台来处理中断的角色)

	// 执行换人后, 还要处理排队队列 和 标志位
}
```

---

## 上下文切换

rt_hw_context_switch = 线程 ↔ 线程 切换（正常炒菜时换人）
rt_hw_context_switch_interrupt = 中断 → 线程 切换（**来中断了，总管接管灶台，处理中断事件，处理完事后换人**）
它们的本质区别：当前是在【线程上下文】还是【中断上下文】！

rt_hw_context_switch  我现在是**厨师**，我要换人！全套寄存器我自己保存，自己恢复，自己切。
rt_hw_context_switch_interrupt  我现在是**总管（中断）**，我处理完事要换人！
硬件已经帮我存了一半现场，我只需要存剩下的，切完直接中断返回，硬件帮我恢复新线程。

---

## signal


```cpp
RT_USING_SIGNALS
RT_THREAD_STAT_SIGNAL_PENDING  // 待处理信号
void rt_thread_handle_sig(rt_bool_t clean_state);
```

你可以把 **Signal 信号** 理解成：**一张贴在厨师背后的小纸条**
- 别人（中断 / 其他厨师 / 内核）可以**悄悄贴上去**
- 厨师**不会立刻发现**
- **必须等厨师下一次重新站上灶台、准备开始炒菜前**
- 系统才会提醒他：
    > **“喂！你背后有张纸条，先处理完再干活！”**


**中断 = 有人直接砸门、强行打断炒菜**
- 厨师必须**立刻停手**
- 总管（内核）接管处理
- **厨师不能反抗**


**信号量 / 消息队列 = 厨师之间传食材、传消息**
- 正常工作流程
- 你等我、我等你


**信号 Signal = 贴在背后的小纸条**
- **不打断炒菜**
- **不抢占灶台**
- **不立即处理**
- **只在厨师【下一次上台干活前】强制处理**


---


信号 **适合用在什么场景？（正确用法）**
1. **让某个线程优雅退出 / 停止**
> 厨师正在炒菜，你不想直接砸锅，
> 贴个纸条：**“炒完这盘就下班，别继续了”**
> 线程下次运行时，看到信号，自己优雅退出。

2. **异常通知、错误处理**
> 系统发现厨师操作错误，
> 贴条：**“你出错了，过来处理一下！”**
> 线程自己处理错误，不崩溃。

3. **简单的异步事件通知（不带数据）**
> 只需要告诉线程：**“有事发生了，你处理一下”**
> 不需要传数据。


---

## 就绪队列


![[Pasted image 20260606222125.png]]


```cpp
void rt_sched_insert_thread(struct rt_thread *thread);// 把线程塞回排队队列
void rt_sched_remove_thread(struct rt_thread *thread);// 把线程从排队队列移除，因为他要上灶台了
```

一句话总结 rt_sched_insert_thread:
把一个厨师 重新放回 排队等候区， 并且根据他有没有用完时间片，决定把他排在队伍【前面】还是【后面】。
如果该线程是主动让出or睡眠的，就放在队伍前面，如果是时间片消耗完的就放队伍后面，
每当从队列里取厨师，就从最高优先级里，并且固定从队列前面开始取。


## rt_sched_insert_thread 完整人话注释

```cpp
/**
 * @brief 把一个线程放回系统就绪队列
 *        线程状态会被设置为 READY（就绪）
 *        线程会从挂起队列里移除
 *
 * @param thread 要放回去的线程
 *
 * @note 用户应用程序不要调用这个函数
 */
void rt_sched_insert_thread(struct rt_thread *thread)
{
    rt_base_t level;

    // 确保厨师指针不是空的
    RT_ASSERT(thread != RT_NULL);

    /*==================== 关中断，防止排队时被打断 ====================*/
    level = rt_hw_interrupt_disable();


    /*==================== 特殊情况：如果是当前正在运行的厨师 ====================*/
    // 如果这个厨师 == 当前正在灶台干活的厨师
    if (thread == rt_current_thread)
    {
        // 直接把状态设为 RUNNING
        RT_SCHED_CTX(thread).stat = RT_THREAD_RUNNING | ...;
        goto __exit; // 直接退出，不用排队
    }


    /*==================== 正常情况：把厨师设置为“排队状态” ====================*/
    // 设置状态为：就绪（排队等灶台）
    RT_SCHED_CTX(thread).stat = RT_THREAD_READY | ...;


    /*==================== 核心：决定排队伍前面还是后面 ====================*/

    // 如果厨师【主动让位 / 时间片用完了】
    if((RT_SCHED_CTX(thread).stat & RT_THREAD_STAT_YIELD_MASK) != 0)
    {
        // 排到 队伍【前面】
        rt_list_insert_before(..., &节点);
    }

    // 如果厨师【还有时间片没用完】
    else
    {
        // 排到 队伍【后面】
        rt_list_insert_after(..., &节点);
    }


    /*==================== 更新优先级位图（告诉系统：这个优先级有人排队了） ====================*/
    rt_thread_ready_priority_group |= ...;


__exit:
    // 开中断
    rt_hw_interrupt_enable(level);
}
```


## 就绪队列优先级


```log
【队头】  1号厨师  ←  下次最先被取出
         2号厨师
         3号厨师
【队尾】  4号厨师
```

rt_sched_insert_thread() 核心的逻辑:
如果厨师【主动让位 / 时间片用完了】, 则放到队伍前面, 下次最先被取出执行；
如果厨师【还有时间片没用完】，则排到队伍后面。

---


从上面注释表明，同一个优先级，会有多个厨师排队，

rt_thread_ready_priority_group 只管一件事：
**“哪个**优先级**有厨师在排队”**，它不管**这个优先级下面有几个厨师！**


rt_thread_ready_priority_group 等同于大厅总看板：
哪个优先级的队伍有人排队，只记**优先级号**，不记人数。比如：
- 优先级 5 有厨师 → 看板标记 **5 号有人**，不记录有多少人
- 优先级 7 有厨师 → 看板标记 **7 号有人**


这里以最大32个优先级为例，刚好每个优先级占用一个bit，bit越低则优先级越高。


---

<font color=blue>rt-thread-5.2.0 版本的内核，先拿单核调度器为例，假设总共有32个优先级，并且优先级数字越小，优先级越大。在内核运行起来后，有多个不同优先级的任务，每个优先级不止一个任务，那么 rt-thread 是如何保证每个优先级的每个任务都能被及时执行到？比如5号优先级下有3个任务，8号优先级(bit8)有2个任务，按照高优先级任务 → 绝对优先抢占执行，那内核岂不是永远只能运行5号优先级的3个任务了，8号优先级的任务永远得不到灶台。
</font>

高优先级任务只要能跑，低优先级任务就绝对得不到 CPU！
只有 0~7 级 **一个能跑的都没有，8 级才能跑！**

5 级线程不能**一直死循环占着 CPU**，必须 **自己主动歇一歇、等一等、睡一睡**，8 级才能上台！
实际工程中 4 种标准做法：
- 1、高优先级线程里加 **rt_thread_mdelay() / rt_thread_delay()**；
- 2、高优先级线程 **等待信号量 / 消息队列 / 事件**（工业级标准用法）；
- 3、高优先级线程 **rt_thread_yield () 主动让位**；
- 4、高优先级线程 **处理完任务直接退出**，相当于该任务是一次性的，跑完就退出线程。

<font color=red>RT-Thread 里，所有高优先级线程都不能死循环空跑，否则低优先级永远饿死！
</font>


---

while (1) // 5级优先级任务
{
    // 1. 读传感器
    read_sensor();

    // 2. 主动睡 50ms
    rt_thread_mdelay(50);
}

while (1)  // 8级优先级任务
{
    // 5 级睡觉的时候，我就能跑！
    display_screen();
    rt_thread_mdelay(100);
}

<font color=blue>如上代码所示，如果8级任务占用灶台超过50ms了怎么办？相当于5级任务mdelay(50)其实超过50ms了，这种在现实中是怎么办或者怎么妥协？
</font>

如果 8 级任务执行时间 > 50ms，那么 5 级任务 **一定会被延迟**，醒来后 **不能立刻运行**！
这就叫 **优先级反转 / 低优先级拖死高优先级**
现实中 **绝对不允许** 这种情况发生！


最终结果：5 级本该 50ms 跑一次，结果变成 70ms 才跑一次甚至更久，高优先级被低优先级拖死了！
现实工程中 **绝对不允许** 低优先级执行太久！
实时系统铁律：所有线程都必须是 **短！小！快！** 不准长时间霸占 CPU！

在实时系统里：
高优先级 = 短跑选手（快进快出）
低优先级 = 捡漏选手（高优先级空闲时才跑）
低优先级绝对不能长时间霸占 CPU
否则高优先级一定被拖死！

---

RT-Thread 5.2.0 默认就是全抢占式优先级调度，原生硬实时抢占，32 优先级配置完全生效。
“硬实时抢占” = 靠【中断 + 抢占调度】实现的【立刻响应能力】

```cpp
// prio5(高)
while(1){read_sensor(); rt_thread_mdelay(50);}
// prio8(低)
while(1){display_screen(); rt_thread_mdelay(100);}
```

- 5 号运行→调用 mdelay (50)，**线程阻塞、入延时链表，内核触发调度，CPU 交给 8 号**；
- 8 号开始执行 display_screen，假设这个函数要 70ms；
- **第 50ms 时刻：系统定时器中断触发，5 号延时到期、被唤醒进入就绪队列**；
- **中断退出前触发调度检查：发现就绪最高优先级是 5 < 当前运行优先级 8 → 立即抢占，保存 8 号现场，切换回 5 号运行**；
- 剩余 20ms 的 display_screen 代码被暂停，等后续 5 号再次阻塞后 8 号继续跑剩余逻辑。

硬件定时器（SysTick/HWTimer）只干 2 件事：
- 给系统提供时间基准（tick），用来计算 `rt_thread_mdelay(50)` 到没到时间。
- 唤醒睡眠的线程：时间到了 → 把线程从睡眠态唤醒 → 设为 **就绪态**。


---

<font color=blue>如果5级里，有多个同是5级的任务，并且第1个5级任务mdelay(50)，但是如果后续的任务占用灶台总用时超过50ms，这种情况怎么办？
</font>

**同优先级（都是 5 级）的任务之间，**
**不会抢占！不会抢占！不会抢占！**
**必须等当前任务主动让出 CPU，下一个才能跑！**

RT-Thread 铁律：同优先级之间：只有时间片轮转，没有抢占！

- **50ms 时间到！A 被唤醒！** A被放到就绪队列
- **但是！B 或 C 还在跑！**
- **A 只能排队等！等到 B/C 主动让出 CPU！**


```log
就绪队列: [1级] ... [5级] ... [8级] ...
                    A就绪

意思是，只要同5级的其他任务都执行玩了，A才会从就绪队列加载到灶台上执行
```


```log
就绪队列：
[1级] ...
[5级]  --> B(正在跑)  -->  C(排队)  -->  A(刚唤醒，在就绪队列排队)
[8级] ...

假设上述就绪队列，B跑完之前，A就唤醒了，那么B跑完之后，是先跑C还是先跑A？
答案：B 跑完之后 → 先跑 A！绝对先跑 A！
RT-Thread 5.2.0 单核调度真实代码逻辑:
	主动让出 / 延时唤醒的同优先级任务 → 排到队头！
	时间片用完的任务 → 排到队尾！
```


---

<font color=blue>从bit0 到 bit31，C语言，从低位到高位遍历，如何最快遍历得到第一个bit为1的位？
</font>

从低位到高位（bit0 → bit31）找第一个为 1 的 bit，最快的办法就是用编译器内置函数，
时间复杂度：**O(1)**，1 个指令周期出结果！

最快代码（C 语言，GCC/Keil 都支持）：
```cpp
// 从低位(bit0)到高位(bit31)找第一个1
int find_first_bit(uint32_t value)
{
    // __builtin_ctz = count trailing zeros
    // 直接返回“末尾有多少个0” = 第一个1的位置
    return __builtin_ctz(value);
}
```

它会被编译成 1 条 CPU 指令，目前 ARM、x86、RISC-V 支持这样的指令。

**从低位找第一个 1 = __builtin_ctz (value)**
**从高位找第一个 1 = __builtin_clz (value)**
**速度：1 条 CPU 指令，O (1)**


RT-Thread 为了兼容所有编译器，直接用了**查表法**（O(1)），具体细节请看其 `__rt_ffs` 函数。


<font color=blue>那如果不止32位，比如我最多优先级数是256bits，它无法用一个基本整型来存放了。这种从低位到高位，获取到第一个bit为1的最快办法是什么？尽量不要用查表法。
</font>

256 位 = 分成 8 个 32 位块（`uint32_t groups [8]`），
从第 0 个块开始遍历，
再用 `__builtin_ctz` 找这个块里最低位 1。


<font color=blue>同样都是256位，`__lowest_bit_bitmap[(rt_uint32_t)(value & (value - 1) ^ value) % 37];` 查表和遍历+__builtin_ctz，哪个更快？
</font>

遍历+内置ctz更快，
关键短板：哈希查表天生带「内存依赖」，
`__lowest_bit_bitmap[]`是全局常量数组，查表需要**访问内存**：
- L1 缓存命中：开销尚可；Cache 失效时一次内存加载几十周期，性能暴跌；
- RTOS 内核调度是高频临界区代码，**最怕不可控的 Cache 抖动**。
并且取模是除法运算，CPU 除法远慢于移位 / 位运算；
而内置ctz直接编译成硬件位扫描指令，**无除法、无访存、周期固定**。


<font color=blue>是不是但凡涉及到内存依赖的都需要注意Cache命中问题？什么情况下需要尤为关注Cache命中问题？是不是这块目标内存内的数据频繁变动时，就需要尤为关注Cache命中问题？
</font>

但凡要读内存（查表、读变量、数组），**一定有 Cache 命中问题！**
不是数据频繁变动才要关注，而是**这段代码越核心、越快、越频繁**，越要关注！
这些高频代码**哪怕多 1 次 Cache 不命中，系统整体性能雪崩**。
Cache 不命中会导致**偶尔慢 100 倍**，因为它访存需要至少100个时钟周期。


<font color=blue>数据频繁变动 = Cache 经常失效、经常要重读内存 = 速度不稳定、变慢。这种数据频繁变动，在实际生产环境的高并发场景，会不可避免遇到，所以这个不是最可怕的吗？毕竟是因为重读内存避无可避，只能尽量将热数据放在前面，是这样吗？
</font>

你说得对：高并发下，数据频繁变动 = Cache 频繁失效 = 速度暴跌，这确实非常可怕！
但它和【RTOS 调度器 / 中断 / 临界区】里的 Cache 失效，不是同一个可怕！

第一种可怕：**高并发业务场景（网络、数据库、用户请求）**
Cache 失效 = 性能下降，但系统不会崩、不会死、不会失控！
你能做的优化：热数据放前面、内存对齐、避免伪共享、局部性原理、分批处理、减少锁竞争。

第二种可怕：**RTOS 调度器 / 中断 / 临界区（内核硬实时路径）**
Cache 失效 = 实时性崩坏 = 控制失效 = 机器失控 = 安全事故！


<font color=blue>分批处理，怎么理解？
</font>

分批处理（人话版 + 高并发 / RTOS 都通用）
分批处理 = 不要一口气把所有事情做完，切成一小批、一小批，慢慢做。
避免一次性占用大量内存 / 霸占 CPU 太久 / 导致 Cache 失效雪崩 / 导致高优先级任务被卡住。

提升 Cache 命中率的 “分批处理”，必须满足一个铁律：
不切换任务！不让出 CPU！不 yield！
这种分批是：一次性处理的数据量 < CPU Cache 总大小


<font color=blue>等等，比如我总共要处理的数据量是128KB，Cache总共32KB，相当于假设我分4批处理，相当于cache要经历4次miss，那我这128KB不分批，Cache不也要miss 4次吗？怎么体现出提升Cache命中率？
</font>

你现在问的是**整个计算机底层最容易被误解、99% 的人都理解错**的问题！
那为什么所有人都说 “分批处理提升 Cache 命中率”？
因为他们说的不是 **“次数”**，而是 **“不会被踢出去”**！

我用**最简单的例子**让你瞬间看懂！

引用你上述的例子，我们对这128KB内存进行【读-改-写】，
无论分批处理还是不分批，Cache Miss 最少4次，分批就是尽量减少cache miss 次数。
如果只是一轮【读-改-写】，那固定4次miss，但是实际中可能要对同一小片数据进行多次【读-改-写】，
如果不分批处理，那会导致每次【读-改-写】都要miss，导致性能下降。

**核心目的：消除重复 Cache Miss，削减总 Cache Miss 次数**
对同一个数据块or同一个缓存行
进行多次读改写时不会反复Cache miss

![[Pasted image 20260606203821.png]]



---


## rt_sched_remove_thread 完整人话注释


```cpp
/**
 * @brief 把一个线程从系统就绪队列里删除
 *
 * @param thread 要被踢出去的线程（厨师）
 *
 * @note 应用程序不要调用这个函数，只给内核用
 */
void rt_sched_remove_thread(struct rt_thread *thread)
{
    rt_base_t level;

    // 安全检查：确保厨师不是空的
    RT_ASSERT(thread != RT_NULL);

    /*==================== 关中断，防止排队时被打断 ====================*/
    level = rt_hw_interrupt_disable();


    /*==================== 打印日志：我要把这个厨师踢出队列 ====================*/
    LOG_D("remove thread[%.*s], the priority: %d", ...);


    /*==================== 第一步：把厨师从队列里删掉 ====================*/
    rt_list_remove(&RT_THREAD_LIST_NODE(thread));
    // 人话：把这个厨师从排队链表上摘下来


    /*==================== 第二步：检查这个优先级队列是不是空了 ====================*/
    if (rt_list_isempty(&(rt_thread_priority_table[RT_SCHED_PRIV(thread).current_priority])))
    {
        // 如果这个优先级 **一个厨师都没有了**

        /*==================== 第三步：更新全局排队看板（位图） ====================*/
        // 把这个优先级标记为：**没人排队**
        rt_thread_ready_priority_group &= ~RT_SCHED_PRIV(thread).number_mask;

        // （>32优先级的额外处理，不用管）
    }


    /*==================== 开中断，结束 ====================*/
    rt_hw_interrupt_enable(level);
}
```



## 线程挂起


```cpp
rt_err_t rt_thread_suspend(rt_thread_t thread)
{
    return rt_thread_suspend_with_flag(thread, RT_UNINTERRUPTIBLE);
}
RTM_EXPORT(rt_thread_suspend);
```

一旦你调用 rt_thread_suspend()，
这个线程一旦被你挂起，谁都叫不醒它，只有调用 `rt_thread_resume()` 才能醒！
连**信号、中断唤醒、IPC 唤醒都拦死，绝对不被打扰！**
因为 **挂起（Suspend）的设计本意就是：强制暂停，不允许被意外唤醒！**

不可中断挂起 = 强制冻结，只认 resume，谁都别想打扰！


---

## 调度临界区

rt_enter_critical = 进临界区 = 把调度器暂时锁住，不让线程切换
rt_exit_critical = 出临界区 = 解锁调度器，允许线程切换，顺便检查要不要调度
rt_scheduler_lock_nest  这是一个**计数器**，记录 “锁了几层”。因为临界区可以**嵌套**。
为什么要关中断？—— 因为修改 `rt_scheduler_lock_nest` 必须**原子操作**，不能被打断。
作用 —— 调度器被锁住 → 不允许线程切换！

进临界区 = 禁止线程切换
出临界区 = 恢复线程切换，并立刻检查是否需要切换


```txt
锁住期间：
哪怕有更高优先级线程就绪，也不能抢CPU

解锁瞬间：
立刻检查：有没有更高优先级线程？有 → 立刻切换
```



```cpp
/**
 * @brief This function will lock the thread scheduler.
 */
rt_base_t rt_enter_critical(void)
{
    rt_base_t level;
    rt_base_t critical_level;

    /* 关中断！防止别人打断我下面这一步操作 */
    level = rt_hw_interrupt_disable();

    /* 调度器锁计数 +1
     * 数字越大 = 锁得越深
     * 最大值很大，不用怕溢出
     */
    rt_scheduler_lock_nest ++;

    /* 把当前锁了几层存起来，返回给调用者 */
    critical_level = rt_scheduler_lock_nest;

    /* 开中断，恢复之前状态 */
    rt_hw_interrupt_enable(level);

    /* 返回当前锁深度 */
    return critical_level;
}
RTM_EXPORT(rt_enter_critical);

/**
 * @brief This function will unlock the thread scheduler.
 */
void rt_exit_critical(void)
{
    rt_base_t level;

    /* 关中断！保证修改安全 */
    level = rt_hw_interrupt_disable();

    /* 调度器锁计数 -1 */
    rt_scheduler_lock_nest --;

    /* 如果锁计数减到 0 了
     * → 说明彻底退出临界区了
     */
    if (rt_scheduler_lock_nest <= 0)
    {
        rt_scheduler_lock_nest = 0;

        /* 开中断 */
        rt_hw_interrupt_enable(level);

        /* 如果当前有线程在运行 */
        if (rt_current_thread)
        {
            /* 做一次调度！
             * 因为刚才锁住不让切换
             * 现在解锁了，看看是不是该换线程了
             */
            rt_schedule();
        }
    }
    else
    {
        /* 还没完全解锁，只是退出一层
         * 开中断，直接返回
         */
        rt_hw_interrupt_enable(level);
    }
}
RTM_EXPORT(rt_exit_critical);
```






---

## NUMA非一致内存访问

单颗 CPU＝**一间独立大厨房**；
L1 = 厨师个人小提篮、L2 = 同簇厨师共用菜筐、L3 = 本厨房全灶台共用巨型菜篮；
主板上**多颗 CPU 插槽 = 多间独立厨房**，这就是 NUMA 多内存节点。


## 多CPU插槽+多内存条插槽

1 颗 CPU Socket = 1 间独立厨房；
CPU 内置 IMC 内存控制器 = 厨房专属仓库管理员；
挨着 CPU 的内存插槽 = 本厨房自带仓库货架

一、硬件层面：内存条天生按插槽归属 NUMA 节点（固定死，插在哪就归哪）
服务器装机规范：**两边 CPU 插内存必须对称**（CPU0 插 4 条、CPU1 也要对应 4 条），不然 NUMA 内存不均衡、性能暴跌。

- CPU0 内核读**自己 Node0 内存**：找自家仓库，本地存取（快）；
- CPU0 内核读**Node1 内存条**：走跨厨房走廊，远程访存（慢 1.5~3 倍延迟）；

二、开机：Linux 内核怎么识别全部内存、拆分节点？
- **BIOS/ACPI 上报硬件拓扑**：开机固件通过**SRAT/SLIT 表**告诉内核：哪个 CPU 对应哪几片物理内存地址、节点间距离；
- Linux 内核据此拆分**多个 NUMA Node（pg_data_t 结构体，一个结构体实例就是一个Node）**：
	- 1 个 Node = 一组 CPU 核心 + 一段连续物理内存（就是插在对应 CPU 旁的所有内存条总和）；
	- 每个 Node 内部再细分 Zone：`ZONE_DMA/DMA32/NORMAL`，适配老外设 DMA 寻址限制；
- **全系统所有内存条容量相加 = 整机总物理内存**，内核汇总所有 Node 内存统计总内存。



## 实时系统和分时系统

简单来说，就是实时系统优先保**紧急任务实时性**，分时系统优先保**所有任务的资源公平**。

**那什么时候用实时系统什么时候用分时系统？**

不是任务多就不能用实时系统。
比如工业网关、车载设备，**上百个实时任务**照样跑 RTOS，
只要核心目标是**关键任务必须限时响应**。如果有这个硬性要求，就用实时系统。
场景：工业控制、机器人、电力设备、自动驾驶等
哪怕几百个任务，**总有一批高优先级硬实时任务**（采样、控制、中断响应），必须毫秒 / 微秒级响应。
靠精细划分优先级、裁剪任务耗时、合理做分批让出，避免低优先级饿死，依然以实时系统为主。


比如桌面 APP、服务器业务、多用户登录，几十个 / 上百个任务都要正常运转，
不能让某一个任务长期霸占 CPU、把其他任务 “饿死”。
编译代码、视频渲染、批量数据处理这类任务，跑多久不确定。
任务 / 程序数量庞大且来源复杂（比如手机 APP、电脑软件），一个程序崩溃不能牵连整个系统。
分时系统普遍搭配 **MMU 虚拟内存**，进程地址空间隔离；
传统 RTOS 多为扁平内存，一错全挂，不适合海量、不可信的任务集群。


现在很多设备用**混合架构**，实时内核跑关键控制任务，分时系统跑海量普通应用，两边各司其职。




## 原子指令


Exclusive Monitor（独占监视器）
它只记录两件事：哪个地址被标记了独占、哪个核标记的。


独占监视器，所有核同时发 LDREX / STREX，到底哪个核能成功读改写呢？

ARM 架构规定：一个核同一时间**只能有一个地址处于 EX 独占状态**。
```txt
LDREX r0, [addrA]  ; 核0：记录“我独占了 addrA”
LDREX r1, [addrB]  ; 核0：**直接覆盖**，现在只认 addrB
```

软件规范也要求：**一个核同一时刻只能跑一个独占序列**。

CMN 全局监视器（HN‑F 内）的真实配置:
- 互连型号CMN‑600 —— 每 HN 最大独占条目数16
- 互连型号CMN‑650 —— 每 HN 最大独占条目数32
- 互连型号CMN‑700 —— 每 HN 最大独占条目数64
条目含义：**（地址标签，核 ID，状态）**，一个地址块同一时间**最多 1 项**（唯一所有者）





# scheduler_mp.c


## rt_schedule 完整人话注释


```cpp
void rt_schedule(void)
{
    rt_base_t level;
    struct rt_thread *to_thread;
    struct rt_thread *current_thread;
    struct rt_cpu    *pcpu;
    int              cpu_id;

    // 此时正在当前CPU核心上运行这段代码
    // 完全正确！我现在就在这个灶台上。

    // 关闭当前核心的本地中断
    // 人话：把门关上！任何人、任何事都别打断我选人！
    level = rt_hw_local_irq_disable();

    // 拿到当前CPU核心的id、正在炒菜厨师等信息
    // 人话：当前是几号灶台？现在谁在炒菜？
    cpu_id = rt_hw_cpu_id();
    pcpu   = rt_cpu_index(cpu_id);
    current_thread = pcpu->current_thread;

    // 如果当前灶台正处于中断状态
    // 如果现在火警 / 紧急事件（中断）正在处理，不能直接换厨师！
    // 先记下来：等处理完紧急事再换！
    if (rt_atomic_load(&(pcpu->irq_nest)))
    {
        pcpu->irq_switch_flag = 1;  // 标记：等会儿再切换
        rt_hw_local_irq_enable(level);
        return ;
    }

    // 嵌套计数器加1,用来禁止递归调用 schedule()
    // 人话：我正在选人，别再叫我选人，防止我把自己绕晕！
    SCHEDULER_ENTER_CRITICAL(current_thread);

    // 检查厨师有没有收到：挂起、停止、杀死、唤醒 等通知。
    // 如果有，先把状态标记好，方便后面直接切换
    SCHED_THREAD_PREPROCESS_SIGNAL(pcpu, current_thread);

    // 如果厨师自己锁了灶台（进了临界区），不能强行把他拉下来！
    // 记个标记：等他解锁了再换！
    if (RT_SCHED_CTX(current_thread).critical_lock_nest > 1)
    {
        // 先记下来：等他解锁以后，必须换厨师！
        SET_CRITICAL_SWITCH_FLAG(pcpu, current_thread);

        // 我先退出调度，不打扰他干活
        SCHEDULER_EXIT_CRITICAL(current_thread);

        /* -RT_ESCHEDLOCKED */
    }
    else
    {
        // 清除标记，准备正式切换
        CLR_CRITICAL_SWITCH_FLAG(pcpu, current_thread);
        pcpu->irq_switch_flag = 0;

        // 锁住整个灶台，开始正式选人
        SCHEDULER_CONTEXT_LOCK(pcpu);

        // 真正挑选：全局/本地队列里最高优先级厨师！
        to_thread = _prepare_context_switch_locked(cpu_id, pcpu, current_thread);

        if (to_thread)
        {
            // 切换厨师！
            // 保存老厨师的锅碗瓢盆 SP
            // 拿出新厨师的工具 SP
            rt_hw_context_switch((rt_ubase_t)&current_thread->sp,
                                 (rt_ubase_t)&to_thread->sp, to_thread);
        }
        else
        {
            // 当前线程继续使用本灶台
            // 人话：没人比现在的厨师优先级更高，那就继续让他炒

            // 解锁当前灶台
            SCHEDULER_CONTEXT_UNLOCK(pcpu);
            SCHEDULER_EXIT_CRITICAL(current_thread);
        }
    }

    // 打开门，恢复正常
    rt_hw_local_irq_enable(level);

    // 执行信号相关的回调
    // 比如厨师被挂起后要做的清理工作
    SCHED_THREAD_PROCESS_SIGNAL(current_thread);
}
```


**每个核心 = 独立的一套调度信息**
- 自己的当前厨师
- 自己的就绪队列
- 自己的中断嵌套
- 自己的调度锁




















# Linux内核性能事件

## 惊群问题


叫醒一堆厨师，但只有一个厨师能拿到资源。

每次事件都唤醒一堆进程，做大量**上下文切换**，全是无效工作。

最经典场景：多进程 / 线程 accept 同一个监听端口
父进程 create socket、bind、listen，fork 出 N 个 worker 进程，每个 worker 都阻塞在 `accept()`，等新连接。一个新连接到来 → **所有 N 个进程都被唤醒**；只有**一个**能 accept 成功、处理连接；剩下 **N-1 个**：抢不到，报错，又阻塞回去。


<font color=blue>给我按照上述写一个能直接运行的例程，包含tcp客户端、服务端，我想验证 accept 是否正的让所有 worker 都被惊动（accept 阻塞返回之后立马加个打印，打印当前worker __func__ + workerindex waked up）
</font>


```cpp
// server.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <netinet/in.h>
#include <errno.h>

#define PORT 8888
#define WORKER_NUM 4  // 开4个worker，方便看惊群

// 每个worker进程执行的逻辑
void worker(int listen_fd, int worker_idx) {
    printf("[worker %d] 启动，阻塞在 accept()...\n", worker_idx);

    while (1) {
        // 阻塞等待连接
        int client_fd = accept(listen_fd, NULL, NULL);

        // ==============================================
        // 关键：只要从 accept() 返回，就打印“被唤醒”
        // ==============================================
        printf("[worker %d] %s waked up\n", worker_idx, __func__);

        if (client_fd < 0) {
            // 惊群：抢不到连接，accept 失败，继续循环阻塞
            perror("  accept failed");
            continue;
        }

        // 只有一个进程能走到这里
        printf("[worker %d] accept 成功！处理连接 fd=%d\n", worker_idx, client_fd);
        sleep(1);       // 模拟处理业务
        close(client_fd);
        printf("[worker %d] 连接处理完成\n\n", worker_idx);
    }
}

int main() {
    int listen_fd = socket(AF_INET, SOCK_STREAM, 0);

    struct sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(PORT);
    addr.sin_addr.s_addr = INADDR_ANY;

    int opt = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt));

    bind(listen_fd, (struct sockaddr*)&addr, sizeof(addr));
    listen(listen_fd, 128);
    printf("服务端监听 :%d，fork %d 个 worker...\n\n", PORT, WORKER_NUM);

    // fork N 个 worker
    for (int i = 0; i < WORKER_NUM; i++) {
        pid_t pid = fork();
        if (pid == 0) {
            worker(listen_fd, i);
            exit(0);
        }
    }

    // 父进程等待子进程（防止僵尸）
    while (wait(NULL) > 0);
    close(listen_fd);
    return 0;
}
```



```cpp
// client.c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

int main() {
    int fd = socket(AF_INET, SOCK_STREAM, 0);

    struct sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(8888);
    addr.sin_addr.s_addr = inet_addr("127.0.0.1");

    printf("客户端发起连接...\n");
    connect(fd, (struct sockaddr*)&addr, sizeof(addr));

    // 连接成功后保持2秒再退出，让服务端打印完整
    sleep(2);
    close(fd);
    return 0;
}
```



```cpp
// epoll_thunder.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <sys/wait.h>
#include <netinet/in.h>
#include <errno.h>

#define PORT 8888
#define WORKER_NUM 4

void worker(int listen_fd, int worker_idx) {
    printf("[worker %d] start, epoll_wait...\n", worker_idx);

    int epfd = epoll_create1(0);
    struct epoll_event ev;
    ev.data.fd = listen_fd;
    ev.events = EPOLLIN; // LT（默认），不加 EPOLLEXCLUSIVE
    epoll_ctl(epfd, EPOLL_CTL_ADD, listen_fd, &ev);

    while (1) {
        struct epoll_event events[1];
        int n = epoll_wait(epfd, events, 1, -1);

        // 只要从 epoll_wait 返回，就打印
        printf("[worker %d] %s waked up\n", worker_idx, __func__);

        if (n < 0) continue;

        if (events[0].data.fd == listen_fd) {
            int client_fd = accept(listen_fd, NULL, NULL);
            if (client_fd < 0) {
                perror("  accept fail");
                continue;
            }
            printf("[worker %d] accept ok, fd=%d\n", worker_idx, client_fd);
            sleep(1);
            close(client_fd);
            printf("[worker %d] done\n\n", worker_idx);
        }
    }
}

int main() {
    int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    int opt = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR|SO_REUSEPORT, &opt, sizeof(opt));

    struct sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(PORT);
    addr.sin_addr.s_addr = INADDR_ANY;

    bind(listen_fd, (struct sockaddr*)&addr, sizeof(addr));
    listen(listen_fd, 128);
    printf("master listen :%d, fork %d workers\n\n", PORT, WORKER_NUM);

    for (int i = 0; i < WORKER_NUM; i++) {
        pid_t pid = fork();
        if (pid == 0) {
            worker(listen_fd, i);
            exit(0);
        }
    }

    while (wait(NULL) > 0);
    close(listen_fd);
    return 0;
}
```


```bash
# build.sh
gcc epoll_thunder.c -o eth.elf
gcc server.c -o server.elf
gcc client.c -o client.elf

# 终端1运行服务端
#./server.elf

# 终端2运行客户端（触发一次连接）
#./client.elf
```


- **直接 accept ()**：Linux ≥2.6 已修复，**不会惊群**（你现在的情况）。
- **epoll LT（默认）**：**仍然会惊群**，工程上要靠锁或 **EPOLLEXCLUSIVE** 解决。



## io_uring

io_uring怎么干掉syscall

当 accept 之后，
一千万连接每个都收发包的话，光syscall就有两千万次每秒，
每次哪怕只有100纳秒，光这一项就要两秒每秒，系统根本扛不住，
io_uring 的诞生就是为了把这件事压到接近零。

单次 syscall 表面成本：陷入内核 + 上下文检查 = 100ns
实际成本: cache抖动、TLB失效、流水线刷新，典型场景下放大到 500ns ~ 1us
千万级QPS下，2000万次 syscall / 秒，光这一项就吃掉两秒每秒，系统已经不可能跑起来，
这是 C10M 时代你必须打破的物理墙。


io_uring 的核心解决办法就是通过 mmap 建立共享内存，
用户态把请求写入 SQ Ring，

```cpp
// 用户态: 把 1000 个 recv 一次性堆到 SQ ring
for (int i=0; i<1000; i++) {
    struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
    io_uring_prep_recv(sqe, fds[i], bufs[i], BUF_SIZE, 0);
    sqe->user_data = (u64)fds[i]; // [ARCH]完成时回填
}
io_uring_submit(&ring); // [ARCH]一次syscall提交1000个

io_uring_for_each_cqe(&ring, head, cqe) {
	int fd = (int)cqe->user_data;
	int n = cqe->res;
	handle_data(fd, n);
}
```



---


## DPDK

一个数据包从网卡到用户态的8微秒之旅
客户端发出64字节TCP包 —— 服务端NIC: DMA到CPU12 Ring —— 。。。 —— [CPU12]用户调用read,syscall进内核拷贝 —— [用户态]read返回,拿到数据

协议栈不是瓶颈，协议栈处理本身只占2us，
真正吃掉CPU预算的是它周边的所有动作：
中断、上下文切换、唤醒、调度、用户态拷贝，
这就是为什么 C10M 优化的重点不是协议栈算法，而是怎么把那些边角动作全干掉，
这就是 DPDK busy-poll 的诞生原因，它甚至连中断都没有，时长直接缩到1.5us。

cache line 抖动：真正的性能杀手
一个连接如果中断CPU和用户态CPU不是同一个，
就会发生跨 NUMA 数据搬运，单次开销可达500ns，一千万QPS的连接，一次就是5秒每秒，机器直接崩，
这就是为什么 C10M 优化最后都收敛到一句话: 让数据待在原来的CPU不要乱跑。

```cpp
// 看起来人畜无害的引用计数
atomic_inc(&sk->sk_refcnt);

// 实际汇编: lock xadd
// 1. 总线发出 lock 信号 (现代CPU是 cache line lock)
// 2. 该 cache line 的所有副本被失效
// 3. 写入并返回新值
// 4. 其他CPU下次访问该 cache line 必须重新加载

// 多个 CPU 高频写同一变量: 单次 ~100ns, 比一次syscall还贵
```

如上述代码，
这就是为什么C10M铁律是: 不要让多个CPU写同一个cache line。

---

内核协议栈的四条税
- 1、通用税：兼容所有协议(IPv4/v6/SCTP)，每包都走完整 if/else 流程。
- 2、可中断税：内核任务可被抢占、迁移、换核，cache 状态全部废掉。
- 3、多用户税：每包都要做权限检查、namespace切换、资源隔离。
- 4、同步税：多核共享数据结构，必然有锁、RCU、原子操作不可避免。

DPDK 的优势
- 零拷贝，NIC DMA 直达用户内存
- 针对场景定制，砍掉所有不用的代码
DPDK 的缺点
- 整个CPU核100%占用，没流量也照样占用；
- 重写整个 TCP/IP 协议栈，失去 iptables、tcpdump、netstat 全部生态；

所以，DPDK只适合极致场景，比如负载均衡器、网关、DDoS防御这种纯网络功能盒子。



C10M时代，
per-cpu是唯一可真正扩展的方案，因为它从根上消除了跨核同步。



## folio


作者设计这个的动机非常朴素，
大文件场景下，for 循环一个一个page处理是性能杀手，
folio 就是把一组连续的 page 打包成一个对象，一次锁、一次操作。


folio 对多线程访问文件性能友好，
因为锁的粒度变大了，但锁的次数大量变少了。


delayed allocation
你调用 write 时根本不去分配磁盘块，
当用户调用 write 后并不立即分配磁盘块，
一直到两秒钟后，后台线程启动 writeback 时，才一次性把所有积累起来的 dirty folio 合并起来，
去分配一大段连续的磁盘空间，
这样做也有一个代价，crash 时可能丢失 dirty 数据，所以你必须 fsync。


为什么作者不去修补，非要从零写一个新的？
答案是软件工程里最经典的 trade-off，当代码的核心抽象本身错了的时候，
重写反而比补丁更便宜。




# qemu-纯裸机zynq实验


我想快速在 qemu 上编译运行自己写的纯裸机代码。




































# Bottom






