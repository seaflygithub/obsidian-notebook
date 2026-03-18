
应用场景：需要很多路can的并发传输场景
最终目标：总线占用率尽量高的前提下，又能保证不丢数据，尽量往极限测。

## 中断层面优化

**✅ 2️⃣ 不丢中断**（Interrupt Handling）
- RX 中断必须及时处理
- TX 完成中断不能堆积

❗ 中断处理必须“短平快”，**绝对不要在中断里做这些**：
- ❌ memcpy 大数据
- ❌ printf
- ❌ 复杂逻辑

✅ 正确做法，中断里只做：
```txt
1. 读硬件 FIFO
2. 写入软件 ring buffer
3. 退出
```



## 数据层面优化


**✅ 3️⃣ 不丢数据**（最关键）

- FIFO overflow ❌
- 中断延迟 ❌
- CPU 抢占 ❌

---

**丢数据的根因**

**❗ 1️⃣ 中断被延迟**

来源：
- 关中断时间过长
- 高优先级任务抢占

👉 解决：
- CAN 中断优先级调高

**❗ 2️⃣ RX FIFO 溢出**

症状：
- 丢帧
- error counter 增加

👉 解决：
- ISR 读干净 FIFO（while循环）
- 软件 buffer 足够大


**❗ 3️⃣ 波特率太高** + CPU 不够

👉 典型：
- 1Mbps + 高频帧
- MCU 跑不动


**❗ 4️⃣ TSEG2 太小**（你刚踩的坑）

👉 会导致：
- 抖动 → CRC error
- 重发 → 总线占用率暴涨


---

**进阶建议**（可选，但很有用）

✅ 1. 用 DMA（如果硬件支持），减少中断压力

✅ 2. 批量处理，ISR 一次读多个 frame

✅ 3. 中断合并（coalescing），减少中断频率




# FIFO追尾问题

网盘文件: xxx

下面的代码，重点关注 canframequeue_push_force 和 canframequeue_push 这两个函数。

**追尾现象：head会推着tail往前走，而不是越过tail**


![[Pasted image 20260422173537.png]]


（1）覆盖策略：覆盖丢失本层队列里最旧的数据
（2）不覆盖策略：如果持续追尾，**这种追尾会逐层往数据源方向传导**，直到上游数据源能够容忍丢失最新数据。


![[Pasted image 20260419173721.png]]

下面是microblaze工程中完整源代码(canframequeue.h):

```cpp
#ifndef __MICROBLAZE_CAN_FRAME_QUEUE_H__
#define __MICROBLAZE_CAN_FRAME_QUEUE_H__

#include <stdint.h>

#ifndef XCAN_MAX_FRAME_SIZE_IN_WORDS
#define XCAN_MAX_FRAME_SIZE_IN_WORDS 4
#endif // XCAN_MAX_FRAME_SIZE_IN_WORDS

#if defined(__linux__)
#define xil_printf printf
#endif // __linux__

typedef struct
{
    uint32_t data[XCAN_MAX_FRAME_SIZE_IN_WORDS];
} can_frame_t;

typedef struct
{
    can_frame_t *frames;
    uint32_t framecnt; // 必须是 2 的幂
    uint32_t mask;     // framecnt - 1

    volatile uint32_t head; // producer 写
    volatile uint32_t tail; // consumer 写

    // 记录历史最高水位
    uint32_t high_watermark;
} canframequeue_t;

// 获取队列当前水位（最常用）
static uint32_t canframequeue_watermark(canframequeue_t *q)
{
    return (q->head - q->tail) & q->mask;
}

static uint32_t canframequeue_high_watermark(canframequeue_t *q)
{
    return q->high_watermark;
}

// 队列容量（有效容量）
static uint32_t canframequeue_capacity(canframequeue_t *q)
{
    return q->framecnt - 1; // 因为留一个空位
}

static inline int is_power_of_two(uint32_t x)
{
    return x && !(x & (x - 1));
}

// 剩余空间（很实用）
static uint32_t canframequeue_space(canframequeue_t *q)
{
    return canframequeue_capacity(q) - canframequeue_watermark(q);
}

static void canframequeue_init(canframequeue_t *q,
                                   can_frame_t *frames,
                                   uint32_t framecnt)
{
    if (!is_power_of_two(framecnt))
    {
        xil_printf("queue_init error: framecnt must be power of 2\r\n");
        while (1)
            ; // 或 assert
    }

    q->frames = frames;
    q->framecnt = framecnt;
    q->mask = framecnt - 1;

    q->head = 0;
    q->tail = 0;
}

static int canframequeue_push(canframequeue_t *q, uint32_t *src)
{
    uint32_t head = q->head;
    uint32_t next = (head + 1) & q->mask;
    uint32_t level;

    /* 满了 */
    if (next == q->tail)
    {
        return 1; // fail
    }

    /* 写入数据（4 word，成本极低） */
    q->frames[head].data[0] = src[0];
    q->frames[head].data[1] = src[1];
    q->frames[head].data[2] = src[2];
    q->frames[head].data[3] = src[3];

    /* 内存屏障（防止重排序） */
    __sync_synchronize();

    /* 发布: 更新 head（最后写，保证顺序） */
    q->head = next;

    // 设置历史最高水位
    level = (next - q->tail) & q->mask;
    if (level > q->high_watermark)
    {
        q->high_watermark = level;
    }

    return 0;
}


// 这里为什么还要多一个覆盖策略的接口(canframequeue_push_force)呢？
// 这是一种妥协设计选择（overwrite policy）
// 当 head 追尾 tail 时，会推着 tail 往前走一格, 即覆盖最旧一帧
// 在严格要求数据完整性的场景下，不建议使用该接口，因为它会导致部分帧丢失,
// 也就是传一段缺几帧，传一段缺几帧这种现象。
// 但在那种对数据完整性要求不高的情况下, 而对实时性要求高的场景下,
// 遇到队列满的情况, 一般建议调用该接口, 
// 因为它能保证最新的帧能够及时呈现出来, 比如网络流媒体场景, 
// 缺个几帧对网络视频观看整体体验影响不大, 
// 但如果不用这种覆盖策略, 那么就丢失实时性, 
// 网络流媒体场景, 给观众的感觉就是视频跳帧严重,
// 就是那种前一秒还是这个画面, 后一秒已经是好几十秒之后的画面了,
// 如果采用这种覆盖策略, 虽然也会跳帧, 
// 但毕竟一旦head追尾tail,head就会推着tail往前走,
// 这样即使跳帧也是很平滑的, 人眼不容易感知到, 
// 但是如果在那种网络极差的环境下,
// 即使采用这种覆盖策略, 也解决不了跳帧严重问题, 
// 因为 tail 远远慢于 head 了, 慢一点或者偶尔慢一下还能接受, 
// 这时候作为网络流媒体的解决方案, 
// 就是降低视频画质, 降低画质就是为了缓解帧缓冲队列的水位压力,
// 或者网络环境低于某个阈值, 直接停止播放并给观看者反馈网络问题, 
// 毕竟流媒体环境, 实时性体验胜于一切, 
// 假设网络环境极差情况下, 并且低于某个阈值了, 还强行推流视频, 
// 就会出现严重的视频跳帧, 
// 这种实时性体验极差, 这会让观众误以为不是网络问题, 是视频平台问题, 
// 但这是网络环境极差导致的head快速推着tail往前走的结果.
static void canframequeue_push_force(canframequeue_t *q, uint32_t *src)
{
    uint32_t head = q->head;
    uint32_t next = (head + 1) & q->mask;
    uint32_t level;

    // 满了 → 覆盖最旧一帧
    // next 会推着 tail 往前走
    if (next == q->tail)
    {
        q->tail = (q->tail + 1) & q->mask;
    }

    q->frames[head].data[0] = src[0];
    q->frames[head].data[1] = src[1];
    q->frames[head].data[2] = src[2];
    q->frames[head].data[3] = src[3];

    __sync_synchronize();

    q->head = next;

    // 设置历史最高水位
    level = (next - q->tail) & q->mask;
    if (level > q->high_watermark)
    {
        q->high_watermark = level;
    }
}

// pop（返回指针，零拷贝）
static can_frame_t *canframequeue_pop(canframequeue_t *q)
{
    if (q->tail == q->head)
    {
        return NULL; // empty
    }

    can_frame_t *frame = &q->frames[q->tail];

    __sync_synchronize();

    q->tail = (q->tail + 1) & q->mask;

    return frame;
}

#endif // __MICROBLAZE_CAN_FRAME_QUEUE_H__
```










# Bottom


