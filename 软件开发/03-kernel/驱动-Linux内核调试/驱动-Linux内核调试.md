
# 驱动问题分类


1、**对时序敏感的问题**
- ftrace 是内核内置的跟踪框架，无需修改驱动代码（或少量修改），可跟踪函数调用流程、中断响应时间、任务调度延迟、锁等待时间等，精准定位时序瓶颈和实时性问题。

2、**死锁、系统卡死 or 硬件卡死问题**
- lockdep 是内核内置的死锁检测框架，可在驱动运行时自动检测自旋锁、互斥锁的使用不当（如嵌套锁、循环等待、锁泄露等），并输出详细的锁依赖关系和调用堆栈。编译内核时开启`CONFIG_LOCKDEP`配置，驱动运行时若存在死锁风险，`lockdep`会提前在`dmesg`中输出警告信息，即使发生死锁，也可通过前期警告定位问题。
- 当系统因死锁 / 硬件卡死触发内核崩溃时，`kdump`可快速保存内核内存镜像（`vmcore`），重启后通过`crash`工具分析内存镜像，查看崩溃前的线程状态、锁信息、寄存器值等，无需实时日志输出。开启内核`CONFIG_CRASH_DUMP`配置，配置`kdump`保存路径，崩溃后通过`crash vmcore vmlinux`命令分析根因。

3、**偶发、难以复现的问题**
- ftrace + perf

4、**硬件底层 or 信号级问题**


# ftrace工具的使用


```bash
# 需要内核支持
# menuconfig: Kernel hacking > Tracers


# 需要挂载 debugfs
mount | grep debugfs
ret=$?
if [ $ret -ne 0 ];then
    mount -t debugfs none /sys/kernel/debug
fi


# 展示支持的追踪类型
cat /sys/kernel/debug/tracing/available_tracers


# 打开特定的追踪类型
if [ $# -ne 2 ];then
    echo "usage: $0 function your_funcname"
    exit 1
fi
trace_select="$1"
trace_name="$2"
echo 0 > /sys/kernel/debug/tracing/tracing_on
echo nop > /sys/kernel/debug/tracing/current_tracer
# echo function > /sys/kernel/debug/tracing/current_tracer
# echo your_function_name > /sys/kernel/debug/tracing/set_ftrace_filter
echo $trace_select > /sys/kernel/debug/tracing/current_tracer
echo $trace_name > /sys/kernel/debug/tracing/set_ftrace_filter
echo 1 > /sys/kernel/debug/tracing/tracing_on



# 然后执行对应操作，最后查看 trace：
# cat /sys/kernel/debug/tracing/trace


# 关闭trace
# echo 0 > /sys/kernel/debug/tracing/tracing_on
# echo nop > /sys/kernel/debug/tracing/current_tracer
# echo > /sys/kernel/debug/tracing/set_ftrace_filter


# 限定PID跟踪
# echo <pid> > /sys/kernel/debug/tracing/set_ftrace_pid
```


---

查看函数调用栈:
```bash
cd /sys/kernel/debug/tracing/
echo 0 > tracing_on
echo function > current_tracer 
echo arm_dma_alloc > set_ftrace_filter 
echo 1 > options/func_stack_trace 
echo 1 > tracing_on 

# 执行触发操作

# 查看跟踪信息
cat /sys/kernel/debug/tracing/trace
```





# bottom





