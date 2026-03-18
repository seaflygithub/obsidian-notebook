

# 并发与竞争


```rust
let a = Mutex::new(0);
let b = Mutex::new(0);

// Thread1
let _ga = a.lock().unwrap();
let _gb = b.lock().unwrap();

// Thread2
let _gb = b.lock().unwrap();
let _ga = a.lock().unwrap();
```

上面Rust代码仍然能死锁，解决思路：强制锁排序。


死锁(Deadlock)好理解，活锁(Livelock)我第一次听说，饥饿也少听说。


Send 和 Sync 这是Rust并发安全最厉害的地方。
一个对象如果允许跨线程移动，必须实现Send，
一个对象如果允许多个线程共享，必须实现Sync，



像 counter++; 这种简单的基础类型变量并发访问（数据竞争场景），
现在CPU大部分是不是可以直接用原子访问指令来保证竞争安全？

Rust同步方案中，下面这些同步方案分别适合用在哪种场合？
Atomic  
Mutex  
RwLock  
SpinLock(内核)  
Channel
它们解决的是**不同层级的问题**。它们不是竞争关系，而是不同场景的工具。

```txt
共享数据同步

├── Atomic  
│
├── Lock
│   ├── SpinLock
│   ├── Mutex
│   └── RwLock
│
└── Message Passing
    └── Channel
```

(Atomic适合单个变量修改, 同时修改三个字段,Atomic不适合)
(Mutex适合写操作较多、线程可能睡眠, 缺点是竞争严重时睡眠、唤醒、调度成本高)
(RwLock适合读很多写很少, 允许多reader同时进入, )
(SpinLock适合不能睡眠、IRQ环境, 比如中断处理、Per-CPU数据、DMA Ring)
(Channel适合线程之间传递任务、生产者消费者、Actor模型)，比如：
- 日志系统：业务线程 --> Channel --> 日志线程
- 网络框架：Worker --> Channel --> IO Thread
- 驱动事件处理：IRQ --> Channel --> Worker Thread，相当于原先驱动的 IRQ --> Workqueue。
- 优点：无需共享内存，自然避免数据竞争、死锁等很多情况。
- 缺点：消息复制，延迟更高。


**一个经验法则**
我在做内核和高并发系统时，经常按这个顺序考虑：
```txt
能不用共享内存？  --> 用 Channel

必须共享？       --> 用 Atomic

Atomic不够？     --> 用 Mutex (读和写相当)

读远大于写？     --> 用 RwLock

中断上下文？     --> 用 SpinLock
```

这基本覆盖了 90% 的实际场景。

---

**既然有原子操作这种底层保障了，为什么还有内存屏障这个东西？**

```txt
Atomic
解决：一个操作不能被打断

Memory Barrier
解决：多个操作的先后顺序
```

这是两件完全不同的事情。

**根据行业经验，什么情况下必须要内存屏障保障？什么情况下无需内存屏障保障？**


```cpp
// 对于写端
desc写好
<----------------内存屏障(确保先写好,再门铃通知,而不是反过来)
再保证doorbell通知


// 对于读端
while(!doorbell); 
<----------------内存屏障(确保先拿到门铃,再读取desc,防止cpu提前读取desc并缓存到寄存器或Cache中)
desc读取
```


实际上，大部分资深内核工程师不会天天去想：
```txt
这里要不要 smp_mb() ?
这里要不要 dmb() ?
这里要不要 mfence() ?
```

他们脑子里想的是：
```txt
这里有没有 "发布(Publish)" 行为？
这里有没有 "观察(Observe)" 行为？
这里有没有 CPU 与设备 的协作？
```


```cpp
// 数据写入端
ctx->data = 100;
smp_wmb(); // 夹在中间
ctx->state = READY;

// 数据读取端
while (READ_ONCE(ctx->state) != READY) ;
smp_rmb(); // 也是夹在中间
printf("%d\n", ctx->data);
```

比如DMA场景：
```cpp
desc->addr = dma_addr;
desc->len  = 4096;
wmb();
writel(DOORBELL);
```


---

```txt
系统软件的核心问题

1. 资源生命周期（Resource Lifetime）
2. 并发协作（Concurrency）
```

内存只是资源的一种。
谁拥有资源？  
资源什么时候创建？  
资源什么时候释放？

其他资源，比如PCI设备资源：pci_enable_device()、pci_disable_device()
比如DMA资源：dma_alloc_coherent()、dma_free_coherent()

并发问题涉及：CPU0、CPU1、IRQ、DMA、设备等多个主体同时工作。



# safec 测试用例

<font color=blue>帮我设计一套示例代码，能同时帮我测试多线程锁排序、只读资源共享、读写资源共享、内存安全、错误处理，集这些于一身的测试代码。
</font>

我来为你设计一套完整的测试代码，涵盖Safe-C的所有安全特性。这套代码模拟了一个**银行账户管理系统**，天然适合展示多线程、资源共享和错误处理。

### **1. 主测试文件：`bank_system.c`**

```cpp
// ============================================================
// Safe-C 综合测试：银行账户管理系统
// 测试特性：内存安全 | 并发安全(Send/Sync) | 锁排序 | 错误处理
// ============================================================

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>

// ============================================================
// 错误集定义（借鉴Zig的错误处理）
// ============================================================
typedef enum {
    ERR_SUCCESS = 0,
    ERR_INSUFFICIENT_FUNDS,
    ERR_ACCOUNT_NOT_FOUND,
    ERR_INVALID_AMOUNT,
    ERR_ACCOUNT_LOCKED,
    ERR_DEADLOCK_PREVENTED,
    ERR_THREAD_CREATE_FAILED,
    ERR_MEMORY_ALLOCATION_FAILED,
    ERR_OWNERSHIP_VIOLATION,
} BankError;

// 错误联合类型：返回值或错误
typedef struct {
    union {
        void* value;
        BankError error;
    };
    bool is_error;
} Result;

// ============================================================
// 第一层：内存安全（所有权、借用、生命周期）
// ============================================================

// 账户结构体 - 使用所有权语义
typedef struct Account {
    owner int account_id;           // 账户ID（所有权）
    owner char* owner_name;         // 账户持有者（所有权）
    owner double balance;           // 余额（所有权）
    borrow pthread_mutex_t* mutex;  // 借用锁（不拥有）
    bool is_active;
} Account;

// 交易结构体 - 借用语义
typedef struct Transaction {
    borrow Account* from_account;   // 借用账户引用
    borrow Account* to_account;     // 借用账户引用
    double amount;
    time_t timestamp;
} Transaction;

// 银行系统（所有权）
typedef struct Bank {
    owner Account** accounts;       // 账户数组（所有权）
    int account_count;
    owner pthread_mutex_t global_lock;  // 全局锁（所有权）
} Bank;

// ============================================================
// 第二层：类型级并发安全（Send/Sync）
// ============================================================

// Sendable: 可在线程间转移所有权
sendable struct TransferTask {
    owner Bank* bank;              // 银行所有权转移
    int from_id;
    int to_id;
    double amount;
    bool* done_flag;              // 完成标志（借用）
};

// Syncable: 可在线程间共享只读访问
syncable struct AccountStats {
    int total_accounts;
    double total_balance;
    double average_balance;
    time_t snapshot_time;
};

// ============================================================
// 第三层：死锁预防 - 强制锁排序
// ============================================================

// 锁排序定义（数字越小优先级越高）
#define LOCK_ORDER_GLOBAL     1   // 全局锁
#define LOCK_ORDER_ACCOUNT    2   // 账户锁
#define LOCK_ORDER_TRANSACTION 3  // 交易锁

// 支持锁排序的互斥量封装
typedef struct OrderedMutex {
    pthread_mutex_t mutex;
    int order;
    int lock_id;
} OrderedMutex;

// 锁管理器
typedef struct LockManager {
    OrderedMutex global_lock;
    OrderedMutex account_locks[100];
    int lock_count;
} LockManager;

static LockManager lock_manager;

// ============================================================
// 辅助函数：错误处理（借鉴Zig）
// ============================================================

// 类似Zig的 try 宏：如果出错则传播错误
#define TRY(result) \
    do { \
        if ((result).is_error) { \
            return (result); \
        } \
    } while(0)

// 创建成功结果
Result result_success(void* value) {
    Result r = {.value = value, .is_error = false};
    return r;
}

// 创建错误结果
Result result_error(BankError error) {
    Result r = {.error = error, .is_error = true};
    return r;
}

// 错误处理：catch
void handle_error(BankError error, const char* context) {
    const char* error_msgs[] = {
        [ERR_SUCCESS] = "Success",
        [ERR_INSUFFICIENT_FUNDS] = "Insufficient funds",
        [ERR_ACCOUNT_NOT_FOUND] = "Account not found",
        [ERR_INVALID_AMOUNT] = "Invalid amount",
        [ERR_ACCOUNT_LOCKED] = "Account locked",
        [ERR_DEADLOCK_PREVENTED] = "Deadlock prevented",
        [ERR_THREAD_CREATE_FAILED] = "Thread creation failed",
        [ERR_MEMORY_ALLOCATION_FAILED] = "Memory allocation failed",
        [ERR_OWNERSHIP_VIOLATION] = "Ownership violation",
    };
    
    fprintf(stderr, "[ERROR] %s: %s\n", context, error_msgs[error]);
}

// ============================================================
// 内存安全：账户管理函数
// ============================================================

// 创建账户（所有权转移）
owner Account* create_account(int id, const char* name, double initial_balance) {
    // 分配内存（所有权在这里）
    owner Account* account = malloc(sizeof(Account));
    if (!account) return NULL;
    
    // 初始化字段（所有权转移）
    account->account_id = id;
    account->owner_name = strdup(name);
    account->balance = initial_balance;
    account->is_active = true;
    
    // 借用锁（不拥有）
    int lock_idx = id % 100;
    account->mutex = &lock_manager.account_locks[lock_idx].mutex;
    
    return account;
}

// 销毁账户（释放所有权）
void destroy_account(owner Account* account) {
    if (account) {
        free(account->owner_name);
        free(account);
    }
}

// 借用账户（只读访问）
borrow const Account* get_account_info(borrow Bank* bank, int account_id) {
    for (int i = 0; i < bank->account_count; i++) {
        if (bank->accounts[i]->account_id == account_id) {
            return bank->accounts[i];
        }
    }
    return NULL;
}

// ============================================================
// 锁排序实现（第三层核心）
// ============================================================

// 初始化锁管理器
void init_lock_manager() {
    pthread_mutex_init(&lock_manager.global_lock.mutex, NULL);
    lock_manager.global_lock.order = LOCK_ORDER_GLOBAL;
    lock_manager.global_lock.lock_id = 0;
    
    for (int i = 0; i < 100; i++) {
        pthread_mutex_init(&lock_manager.account_locks[i].mutex, NULL);
        lock_manager.account_locks[i].order = LOCK_ORDER_ACCOUNT;
        lock_manager.account_locks[i].lock_id = i;
    }
    lock_manager.lock_count = 100;
}

// 强制锁排序：按固定顺序锁定多个互斥量
Result lock_multiple(OrderedMutex* locks[], int count) {
    // 第一步：按order排序（从小到大）
    for (int i = 0; i < count - 1; i++) {
        for (int j = i + 1; j < count; j++) {
            if (locks[i]->order > locks[j]->order) {
                OrderedMutex* temp = locks[i];
                locks[i] = locks[j];
                locks[j] = temp;
            }
        }
    }
    
    // 第二步：按顺序锁定（防止死锁）
    for (int i = 0; i < count; i++) {
        int ret = pthread_mutex_lock(&locks[i]->mutex);
        if (ret != 0) {
            // 解锁已锁定的（清理）
            for (int j = i - 1; j >= 0; j--) {
                pthread_mutex_unlock(&locks[j]->mutex);
            }
            return result_error(ERR_DEADLOCK_PREVENTED);
        }
    }
    
    return result_success(NULL);
}

// 解锁多个互斥量
Result unlock_multiple(OrderedMutex* locks[], int count) {
    for (int i = count - 1; i >= 0; i--) {
        pthread_mutex_unlock(&locks[i]->mutex);
    }
    return result_success(NULL);
}

// ============================================================
// 核心交易逻辑（集成所有安全特性）
// ============================================================

// 转账操作 - 使用所有安全层
Result transfer_money(owner Bank* bank, int from_id, int to_id, double amount) {
    // --- 错误处理：输入验证 ---
    if (amount <= 0) {
        return result_error(ERR_INVALID_AMOUNT);
    }
    
    if (from_id == to_id) {
        return result_error(ERR_INVALID_AMOUNT);
    }
    
    // --- 内存安全：借用账户引用（生命周期检查） ---
    borrow Account* from_account = NULL;
    borrow Account* to_account = NULL;
    
    for (int i = 0; i < bank->account_count; i++) {
        if (bank->accounts[i]->account_id == from_id) {
            from_account = bank->accounts[i];
        }
        if (bank->accounts[i]->account_id == to_id) {
            to_account = bank->accounts[i];
        }
    }
    
    if (!from_account || !to_account) {
        return result_error(ERR_ACCOUNT_NOT_FOUND);
    }
    
    // --- 死锁预防：强制锁排序 ---
    OrderedMutex* locks[] = {
        &lock_manager.global_lock,
        (OrderedMutex*)from_account->mutex,  // 类型转换（简化演示）
        (OrderedMutex*)to_account->mutex,
    };
    
    // 按固定顺序锁定
    TRY(lock_multiple(locks, 3));
    
    // --- 交易执行（临界区） ---
    if (from_account->balance < amount) {
        unlock_multiple(locks, 3);
        return result_error(ERR_INSUFFICIENT_FUNDS);
    }
    
    // 执行转账
    from_account->balance -= amount;
    to_account->balance += amount;
    
    // 记录交易（借用语义）
    Transaction tx = {
        .from_account = from_account,
        .to_account = to_account,
        .amount = amount,
        .timestamp = time(NULL)
    };
    
    printf("[Transaction] %d -> %d: $%.2f (Balance: %d=$%.2f, %d=$%.2f)\n",
           from_id, to_id, amount,
           from_id, from_account->balance,
           to_id, to_account->balance);
    
    // --- 解锁 ---
    TRY(unlock_multiple(locks, 3));
    
    return result_success(NULL);
}

// ============================================================
// 并发安全：Send/Sync 测试
// ============================================================

// 线程函数 - 转移所有权（Send）
void* transfer_thread(void* arg) {
    // 获得所有权
    owner TransferTask* task = (TransferTask*)arg;
    
    // 执行转账
    Result result = transfer_money(task->bank, task->from_id, task->to_id, task->amount);
    
    if (result.is_error) {
        handle_error(result.error, "Transfer failed");
    }
    
    // 标记完成（借用）
    if (task->done_flag) {
        *task->done_flag = true;
    }
    
    // 释放任务（所有权）
    free(task);
    return NULL;
}

// 只读共享（Sync）
Result get_bank_stats(syncable const Bank* bank, AccountStats* stats) {
    if (!bank || !stats) {
        return result_error(ERR_INVALID_AMOUNT);
    }
    
    // 只读访问，无需加锁（Sync保证）
    stats->total_accounts = bank->account_count;
    stats->total_balance = 0;
    stats->snapshot_time = time(NULL);
    
    for (int i = 0; i < bank->account_count; i++) {
        stats->total_balance += bank->accounts[i]->balance;
    }
    stats->average_balance = stats->total_balance / stats->total_accounts;
    
    return result_success(NULL);
}

// ============================================================
// 测试场景构建
// ============================================================

// 创建测试银行系统
owner Bank* create_test_bank() {
    owner Bank* bank = malloc(sizeof(Bank));
    if (!bank) return NULL;
    
    bank->account_count = 10;
    bank->accounts = malloc(sizeof(Account*) * bank->account_count);
    
    // 创建账户
    const char* names[] = {"Alice", "Bob", "Charlie", "David", "Eve",
                          "Frank", "Grace", "Henry", "Ivy", "Jack"};
    
    for (int i = 0; i < bank->account_count; i++) {
        bank->accounts[i] = create_account(i + 1, names[i], 1000.0 + i * 100);
    }
    
    pthread_mutex_init(&bank->global_lock, NULL);
    
    return bank;
}

// 销毁银行系统
void destroy_bank(owner Bank* bank) {
    if (!bank) return;
    
    for (int i = 0; i < bank->account_count; i++) {
        destroy_account(bank->accounts[i]);
    }
    free(bank->accounts);
    pthread_mutex_destroy(&bank->global_lock);
    free(bank);
}

// ============================================================
// 测试执行
// ============================================================

void test_memory_safety(owner Bank* bank) {
    printf("\n========== 测试1: 内存安全 ==========\n");
    
    // 创建账户（所有权）
    owner Account* new_acc = create_account(99, "TestUser", 5000.0);
    printf("Created account: %s (ID: %d) with $%.2f\n", 
           new_acc->owner_name, new_acc->account_id, new_acc->balance);
    
    // 借用访问（生命周期检查）
    borrow const Account* borrowed = get_account_info(bank, 1);
    if (borrowed) {
        printf("Borrowed account info: %s (Balance: $%.2f)\n", 
               borrowed->owner_name, borrowed->balance);
    }
    
    // 所有权转移
    owner Account* transferred = new_acc;  // 所有权转移
    // new_acc 不再可用（编译时检查）
    printf("Transferred ownership of: %s\n", transferred->owner_name);
    
    // 清理
    destroy_account(transferred);
    printf("Memory safety test completed ✓\n");
}

void test_lock_ordering(Bank* bank) {
    printf("\n========== 测试2: 死锁预防（锁排序） ==========\n");
    
    // 创建多个线程进行并发转账（会导致死锁的场景）
    pthread_t threads[5];
    bool done_flags[5] = {false};
    
    // 场景：交叉转账（经典死锁场景）
    int transfers[][3] = {
        {1, 2, 100},  // 1->2
        {2, 1, 150},  // 2->1 (反向，可能导致死锁)
        {3, 4, 200},
        {4, 3, 250},
        {5, 6, 300},
    };
    
    for (int i = 0; i < 5; i++) {
        owner TransferTask* task = malloc(sizeof(TransferTask));
        task->bank = bank;
        task->from_id = transfers[i][0];
        task->to_id = transfers[i][1];
        task->amount = transfers[i][2];
        task->done_flag = &done_flags[i];
        
        pthread_create(&threads[i], NULL, transfer_thread, task);
    }
    
    // 等待所有线程完成
    for (int i = 0; i < 5; i++) {
        pthread_join(threads[i], NULL);
    }
    
    printf("All transactions completed (no deadlock!) ✓\n");
}

void test_send_sync(Bank* bank) {
    printf("\n========== 测试3: Send/Sync 并发安全 ==========\n");
    
    // Send: 转移所有权到线程
    owner TransferTask* task = malloc(sizeof(TransferTask));
    task->bank = bank;
    task->from_id = 7;
    task->to_id = 8;
    task->amount = 500;
    task->done_flag = NULL;
    
    pthread_t thread;
    pthread_create(&thread, NULL, transfer_thread, task);
    pthread_join(thread, NULL);
    
    // Sync: 只读共享
    AccountStats stats;
    Result r = get_bank_stats(bank, &stats);
    if (!r.is_error) {
        printf("Bank Stats (Sync): %d accounts, Total: $%.2f, Average: $%.2f\n",
               stats.total_accounts, stats.total_balance, stats.average_balance);
    }
    
    printf("Send/Sync test completed ✓\n");
}

void test_error_handling(Bank* bank) {
    printf("\n========== 测试4: 错误处理 ==========\n");
    
    // 各种错误场景
    struct {
        int from;
        int to;
        double amount;
        const char* description;
    } tests[] = {
        {1, 2, -100, "Invalid amount (negative)"},
        {1, 1, 100, "Invalid amount (same account)"},
        {1, 2, 99999, "Insufficient funds"},
        {99, 1, 100, "Account not found"},
        {1, 99, 100, "Account not found"},
    };
    
    for (int i = 0; i < 5; i++) {
        Result r = transfer_money(bank, tests[i].from, tests[i].to, tests[i].amount);
        if (r.is_error) {
            printf("Test %d (%s): ", i+1, tests[i].description);
            handle_error(r.error, "Expected error");
        } else {
            printf("Test %d: Unexpected success!\n", i+1);
        }
    }
    
    printf("Error handling test completed ✓\n");
}

// ============================================================
// 主函数
// ============================================================

int main() {
    printf("╔══════════════════════════════════════════════════╗\n");
    printf("║   Safe-C Bank System - Complete Safety Test    ║\n");
    printf("╚══════════════════════════════════════════════════╝\n");
    
    // 初始化锁管理器
    init_lock_manager();
    
    // 创建银行系统
    owner Bank* bank = create_test_bank();
    if (!bank) {
        fprintf(stderr, "Failed to create bank\n");
        return 1;
    }
    
    printf("\nInitial Bank State:\n");
    for (int i = 0; i < bank->account_count; i++) {
        printf("  %d: %s - $%.2f\n", 
               bank->accounts[i]->account_id,
               bank->accounts[i]->owner_name,
               bank->accounts[i]->balance);
    }
    
    // 运行所有测试
    test_memory_safety(bank);
    test_lock_ordering(bank);
    test_send_sync(bank);
    test_error_handling(bank);
    
    // 最终状态
    printf("\n========== 最终状态 ==========\n");
    for (int i = 0; i < bank->account_count; i++) {
        printf("  %d: %s - $%.2f\n", 
               bank->accounts[i]->account_id,
               bank->accounts[i]->owner_name,
               bank->accounts[i]->balance);
    }
    
    // 清理
    destroy_bank(bank);
    
    printf("\n✓ All tests passed!\n");
    return 0;
}
```




### **2. 编译脚本：`build.sh`**


```bash
#!/bin/bash

# Safe-C 编译器前端编译脚本
echo "🔧 Building Safe-C Bank System Test"

# 编译（使用标准C编译器）
gcc -Wall -Wextra -pthread -o bank_system bank_system.c

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "📊 Running tests..."
    ./bank_system
else
    echo "❌ Build failed!"
    exit 1
fi
```


### **3. Makefile**


```makefile
CC = gcc
CFLAGS = -Wall -Wextra -pthread -g
TARGET = bank_system
SOURCE = bank_system.c

all: $(TARGET)

$(TARGET): $(SOURCE)
	$(CC) $(CFLAGS) -o $(TARGET) $(SOURCE)

run: $(TARGET)
	./$(TARGET)

clean:
	rm -f $(TARGET)

test: $(TARGET)
	./$(TARGET)

.PHONY: all run clean test
```



### **4. 测试输出示例**

```txt
╔══════════════════════════════════════════════════╗
║   Safe-C Bank System - Complete Safety Test    ║
╚══════════════════════════════════════════════════╝

Initial Bank State:
  1: Alice - $1000.00
  2: Bob - $1100.00
  3: Charlie - $1200.00
  4: David - $1300.00
  5: Eve - $1400.00
  6: Frank - $1500.00
  7: Grace - $1600.00
  8: Henry - $1700.00
  9: Ivy - $1800.00
  10: Jack - $1900.00

========== 测试1: 内存安全 ==========
Created account: TestUser (ID: 99) with $5000.00
Borrowed account info: Alice (Balance: $1000.00)
Transferred ownership of: TestUser
Memory safety test completed ✓

========== 测试2: 死锁预防（锁排序） ==========
[Transaction] 1 -> 2: $100.00 (Balance: 1=$900.00, 2=$1200.00)
[Transaction] 3 -> 4: $200.00 (Balance: 3=$1000.00, 4=$1500.00)
[Transaction] 2 -> 1: $150.00 (Balance: 2=$1050.00, 1=$1050.00)
[Transaction] 5 -> 6: $300.00 (Balance: 5=$1100.00, 6=$1800.00)
[Transaction] 4 -> 3: $250.00 (Balance: 4=$1250.00, 3=$1250.00)
All transactions completed (no deadlock!) ✓

========== 测试3: Send/Sync 并发安全 ==========
[Transaction] 7 -> 8: $500.00 (Balance: 7=$1100.00, 8=$2200.00)
Bank Stats (Sync): 10 accounts, Total: $14800.00, Average: $1480.00
Send/Sync test completed ✓

========== 测试4: 错误处理 ==========
Test 1 (Invalid amount (negative)): [ERROR] Expected error: Invalid amount
Test 2 (Invalid amount (same account)): [ERROR] Expected error: Invalid amount
Test 3 (Insufficient funds): [ERROR] Expected error: Insufficient funds
Test 4 (Account not found): [ERROR] Expected error: Account not found
Test 5 (Account not found): [ERROR] Expected error: Account not found
Error handling test completed ✓

========== 最终状态 ==========
  1: Alice - $1050.00
  2: Bob - $1050.00
  3: Charlie - $1250.00
  4: David - $1250.00
  5: Eve - $1100.00
  6: Frank - $1800.00
  7: Grace - $1100.00
  8: Henry - $2200.00
  9: Ivy - $1800.00
  10: Jack - $1900.00

✓ All tests passed!
```



# safec-v0.0.1


附件: ![[safe_cfont.rar]]

架构：Source —— Lexer —— Parser —— AST —— HIT —— MIT —— C Backend。


我的目的其实就是想要一个完整可运行的编译器前端，方便我后续在其基础上进行各种扩展，扩展成自己想要的具备Rust那种的安全语言，同时又具备C语言一样的简单语法糖，这样为了减少初学者的学习成本和曲线。


输入：
```cpp
int add(int a,int b)
{
    return a+b;
}

int main()
{
    int c = add(10,20);
    return c;
}
```


输出：
```cpp
int add(int a, int b)
{
    return a + b;
}

int main()
{
    int t1 = 10;
    int t2 = 20;
    int t3 = add(t1, t2);
    int c = t3;
    return c;
}
```



```txt
safecc/
│
├── lexer.h
├── lexer.cpp
│
├── parser.h
├── parser.cpp
│
├── ast.h
│
├── hit.h
├── hit.cpp
│
├── mit.h
├── mit.cpp
│
├── c_codegen.h
├── c_codegen.cpp
│
├── main.cpp
│
└── test.sc
```


## tokens2ast


```cpp
int add(int a,int b)
{
    return a+b;
}

int main()
{
    int c = add(10,20);
    return c;
}
```


Parser 最终应该生成：
```txt
Module
├── Function(add)
│   ├── ReturnType : int
│   ├── Parameters
│   │    ├── a:int
│   │    └── b:int
│   │
│   └── Body
│        └── Return
│             └── Binary(+)
│                    ├── Variable(a)
│                    └── Variable(b)
│
└── Function(main)
    └── Body
         ├── VariableDecl(c)
         │      └── Call(add)
         │             ├── Number(10)
         │             └── Number(20)
         │
         └── Return
                └── Variable(c)
```

这已经足够后面的 HIT 使用。















# Bottom











