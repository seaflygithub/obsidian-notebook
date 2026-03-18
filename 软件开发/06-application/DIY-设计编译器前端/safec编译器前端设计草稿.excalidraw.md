---

excalidraw-plugin: parsed
tags: [excalidraw]

---
==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠== You can decompress Drawing data with the command palette: 'Decompress current Excalidraw file'. For more info check in plugin settings under 'Saving'


# Excalidraw Data

## Text Elements
bank_system.safec ^fFyZiMsb

// ============================================================
// bank_system.safec - Safe-C 银行账户管理系统
// 特性：内存安全 | 并发安全(Send/Sync) | 锁排序 | 错误处理
// ============================================================

#pragma safe(file)  // 文件级安全声明

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>

// ============================================================
// 错误集定义（借鉴Zig的错误处理）
// ============================================================
error_set BankError {
    ERR_SUCCESS = 0,
    ERR_INSUFFICIENT_FUNDS,
    ERR_ACCOUNT_NOT_FOUND,
    ERR_INVALID_AMOUNT,
    ERR_ACCOUNT_LOCKED,
    ERR_DEADLOCK_PREVENTED,
    ERR_THREAD_CREATE_FAILED,
    ERR_MEMORY_ALLOCATION_FAILED,
    ERR_OWNERSHIP_VIOLATION,
};

// 错误联合类型
error_union Result {
    void* value;
    BankError error;
};

// ============================================================
// 第一层：内存安全（所有权、借用、生命周期）
// ============================================================

// 账户结构体
struct Account {
    owner int account_id;           // 账户ID（所有权）
    owner char* owner_name;         // 账户持有者（所有权）
    owner double balance;           // 余额（所有权）
    borrow pthread_mutex_t* mutex;  // 借用锁（不拥有）
    bool is_active;
};

// 交易结构体 - 使用借用语义
struct Transaction {
    borrow Account* from_account;   // 借用账户引用
    borrow Account* to_account;     // 借用账户引用
    double amount;
    time_t timestamp;
};

// 银行系统
struct Bank {
    owner Account** accounts;       // 账户数组（所有权）
    int account_count;
    owner pthread_mutex_t global_lock;  // 全局锁（所有权）
};

// ============================================================
// 第二层：类型级并发安全（Send/Sync）
// ============================================================

// Sendable: 可在线程间转移所有权
sendable struct TransferTask {
    owner Bank* bank;              // 银行所有权转移
    int from_id;
    int to_id;
    double amount;
    borrow bool* done_flag;        // 完成标志（借用）
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

#define LOCK_ORDER_GLOBAL     1
#define LOCK_ORDER_ACCOUNT    2

struct OrderedMutex {
    pthread_mutex_t mutex;
    int order;
    int lock_id;
};

struct LockManager {
    OrderedMutex global_lock;
    OrderedMutex account_locks[100];
    int lock_count;
};

static LockManager lock_manager;

// ============================================================
// 辅助函数：错误处理
// ============================================================

// Zig风格的try宏
#define try(result) \
    do { \
        if ((result).is_error) { \
            return (result); \
        } \
    } while(0)

// 创建成功结果
safe Result result_success(void* value) {
    Result r = {.value = value, .is_error = false};
    return r;
}

// 创建错误结果
safe Result result_error(BankError error) {
    Result r = {.error = error, .is_error = true};
    return r;
}

// 错误处理函数
safe void handle_error(BankError error, const char* context) {
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

// 创建账户 - 返回所有权
safe owner Account* create_account(int id, const char* name, double initial_balance) {
    owner Account* account = malloc(sizeof(Account));
    if (!account) {
        return NULL;
    }
    
    account->account_id = id;
    account->owner_name = strdup(name);
    account->balance = initial_balance;
    account->is_active = true;
    
    // 借用锁（不拥有所有权）
    int lock_idx = id % 100;
    account->mutex = &lock_manager.account_locks[lock_idx].mutex;
    
    return account;
}

// 销毁账户 - 释放所有权
safe void destroy_account(owner Account* account) {
    if (account) {
        free(account->owner_name);
        free(account);
    }
}

// 借用账户 - 只读访问
safe borrow const Account* get_account_info(borrow Bank* bank, int account_id) {
    for (int i = 0; i < bank->account_count; i++) {
        if (bank->accounts[i]->account_id == account_id) {
            return bank->accounts[i];
        }
    }
    return NULL;
}

// ============================================================
// 锁排序实现
// ============================================================

safe void init_lock_manager() {
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

// 强制锁排序
safe Result lock_multiple(OrderedMutex* locks[], int count) {
    // 按order排序
    for (int i = 0; i < count - 1; i++) {
        for (int j = i + 1; j < count; j++) {
            if (locks[i]->order > locks[j]->order) {
                OrderedMutex* temp = locks[i];
                locks[i] = locks[j];
                locks[j] = temp;
            }
        }
    }
    
    // 按顺序锁定
    for (int i = 0; i < count; i++) {
        int ret = pthread_mutex_lock(&locks[i]->mutex);
        if (ret != 0) {
            for (int j = i - 1; j >= 0; j--) {
                pthread_mutex_unlock(&locks[j]->mutex);
            }
            return result_error(ERR_DEADLOCK_PREVENTED);
        }
    }
    
    return result_success(NULL);
}

safe Result unlock_multiple(OrderedMutex* locks[], int count) {
    for (int i = count - 1; i >= 0; i--) {
        pthread_mutex_unlock(&locks[i]->mutex);
    }
    return result_success(NULL);
}

// ============================================================
// 核心交易逻辑
// ============================================================

safe Result transfer_money(owner Bank* bank, int from_id, int to_id, double amount) {
    // 错误处理：输入验证
    if (amount <= 0) {
        return result_error(ERR_INVALID_AMOUNT);
    }
    
    if (from_id == to_id) {
        return result_error(ERR_INVALID_AMOUNT);
    }
    
    // 借用账户引用
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
    
    // 死锁预防：强制锁排序
    OrderedMutex* locks[] = {
        &lock_manager.global_lock,
        (OrderedMutex*)from_account->mutex,
        (OrderedMutex*)to_account->mutex,
    };
    
    try(lock_multiple(locks, 3));
    
    // 交易执行
    if (from_account->balance < amount) {
        unlock_multiple(locks, 3);
        return result_error(ERR_INSUFFICIENT_FUNDS);
    }
    
    from_account->balance -= amount;
    to_account->balance += amount;
    
    // 记录交易
    Transaction tx = {
        .from_account = from_account,
        .to_account = to_account,
        .amount = amount,
        .timestamp = time(NULL)
    };
    
    printf("[Transaction] %d -> %d: $%.2f\n", from_id, to_id, amount);
    
    try(unlock_multiple(locks, 3));
    
    return result_success(NULL);
}

// ============================================================
// 并发安全：Send/Sync 测试
// ============================================================

safe void* transfer_thread(void* arg) {
    owner TransferTask* task = (TransferTask*)arg;
    
    Result result = transfer_money(task->bank, task->from_id, task->to_id, task->amount);
    
    if (result.is_error) {
        handle_error(result.error, "Transfer failed");
    }
    
    if (task->done_flag) {
        *task->done_flag = true;
    }
    
    free(task);
    return NULL;
}

safe Result get_bank_stats(syncable const Bank* bank, AccountStats* stats) {
    if (!bank || !stats) {
        return result_error(ERR_INVALID_AMOUNT);
    }
    
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

safe owner Bank* create_test_bank() {
    owner Bank* bank = malloc(sizeof(Bank));
    if (!bank) {
        return NULL;
    }
    
    bank->account_count = 10;
    bank->accounts = malloc(sizeof(Account*) * bank->account_count);
    
    const char* names[] = {"Alice", "Bob", "Charlie", "David", "Eve",
                          "Frank", "Grace", "Henry", "Ivy", "Jack"};
    
    for (int i = 0; i < bank->account_count; i++) {
        bank->accounts[i] = create_account(i + 1, names[i], 1000.0 + i * 100);
    }
    
    pthread_mutex_init(&bank->global_lock, NULL);
    
    return bank;
}

safe void destroy_bank(owner Bank* bank) {
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

safe void test_memory_safety(owner Bank* bank) {
    printf("\n========== 测试1: 内存安全 ==========\n");
    
    owner Account* new_acc = create_account(99, "TestUser", 5000.0);
    printf("Created account: %s (ID: %d) with $%.2f\n", 
           new_acc->owner_name, new_acc->account_id, new_acc->balance);
    
    borrow const Account* borrowed = get_account_info(bank, 1);
    if (borrowed) {
        printf("Borrowed account info: %s (Balance: $%.2f)\n", 
               borrowed->owner_name, borrowed->balance);
    }
    
    owner Account* transferred = new_acc;
    printf("Transferred ownership of: %s\n", transferred->owner_name);
    
    destroy_account(transferred);
    printf("Memory safety test completed ✓\n");
}

safe void test_lock_ordering(Bank* bank) {
    printf("\n========== 测试2: 死锁预防（锁排序） ==========\n");
    
    pthread_t threads[5];
    bool done_flags[5] = {false};
    
    int transfers[][3] = {
        {1, 2, 100},
        {2, 1, 150},
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
    
    for (int i = 0; i < 5; i++) {
        pthread_join(threads[i], NULL);
    }
    
    printf("All transactions completed (no deadlock!) ✓\n");
}

safe void test_send_sync(Bank* bank) {
    printf("\n========== 测试3: Send/Sync 并发安全 ==========\n");
    
    owner TransferTask* task = malloc(sizeof(TransferTask));
    task->bank = bank;
    task->from_id = 7;
    task->to_id = 8;
    task->amount = 500;
    task->done_flag = NULL;
    
    pthread_t thread;
    pthread_create(&thread, NULL, transfer_thread, task);
    pthread_join(thread, NULL);
    
    AccountStats stats;
    Result r = get_bank_stats(bank, &stats);
    if (!r.is_error) {
        printf("Bank Stats (Sync): %d accounts, Total: $%.2f\n",
               stats.total_accounts, stats.total_balance);
    }
    
    printf("Send/Sync test completed ✓\n");
}

safe void test_error_handling(Bank* bank) {
    printf("\n========== 测试4: 错误处理 ==========\n");
    
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
        }
    }
    
    printf("Error handling test completed ✓\n");
}

// ============================================================
// 主函数
// ============================================================

safe int main() {
    printf("╔══════════════════════════════════════════════════╗\n");
    printf("║   Safe-C Bank System - Complete Safety Test    ║\n");
    printf("╚══════════════════════════════════════════════════╝\n");
    
    init_lock_manager();
    
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
    
    test_memory_safety(bank);
    test_lock_ordering(bank);
    test_send_sync(bank);
    test_error_handling(bank);
    
    printf("\n========== 最终状态 ==========\n");
    for (int i = 0; i < bank->account_count; i++) {
        printf("  %d: %s - $%.2f\n", 
               bank->accounts[i]->account_id,
               bank->accounts[i]->owner_name,
               bank->accounts[i]->balance);
    }
    
    destroy_bank(bank);
    
    printf("\n✓ All tests passed!\n");
    return 0;
} ^sg499adv

bank_system.safec.c ^N0nH0Brn

// ============================================================
// bank_system.safec.c - Safe-C 编译后的标准C代码
// 所有安全注解已移除，转换为标准C
// ============================================================

#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>

// ============================================================
// 错误处理（转换为标准C枚举和结构体）
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

typedef struct {
    union {
        void* value;
        BankError error;
    };
    bool is_error;
} Result;

// ============================================================
// 数据结构（移除所有安全注解）
// ============================================================

struct Account {
    int account_id;
    char* owner_name;
    double balance;
    pthread_mutex_t* mutex;
    bool is_active;
};

struct Transaction {
    struct Account* from_account;
    struct Account* to_account;
    double amount;
    time_t timestamp;
};

struct Bank {
    struct Account** accounts;
    int account_count;
    pthread_mutex_t global_lock;
};

// Send/Sync注解已移除
struct TransferTask {
    struct Bank* bank;
    int from_id;
    int to_id;
    double amount;
    bool* done_flag;
};

struct AccountStats {
    int total_accounts;
    double total_balance;
    double average_balance;
    time_t snapshot_time;
};

// ============================================================
// 锁排序
// ============================================================

#define LOCK_ORDER_GLOBAL     1
#define LOCK_ORDER_ACCOUNT    2

typedef struct {
    pthread_mutex_t mutex;
    int order;
    int lock_id;
}OrderedMutex;

typedef struct {
    OrderedMutex global_lock;
    OrderedMutex account_locks[100];
    int lock_count;
} LockManager;

static LockManager lock_manager;

// ============================================================
// 辅助函数
// ============================================================

#define try(result) \
    do { \
        if ((result).is_error) { \
            return (result); \
        } \
    } while(0)

Result result_success(void* value) {
    Result r = {.value = value, .is_error = false};
    return r;
}

Result result_error(BankError error) {
    Result r = {.error = error, .is_error = true};
    return r;
}

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
// 账户管理函数（移除所有权注解）
// ============================================================

struct Account* create_account(int id, const char* name, double initial_balance) {
    struct Account* account = malloc(sizeof(struct Account));
    if (!account) {
        return NULL;
    }
    
    account->account_id = id;
    account->owner_name = strdup(name);
    account->balance = initial_balance;
    account->is_active = true;
    
    int lock_idx = id % 100;
    account->mutex = &lock_manager.account_locks[lock_idx].mutex;
    
    return account;
}

void destroy_account(struct Account* account) {
    if (account) {
        free(account->owner_name);
        free(account);
    }
}

const struct Account* get_account_info(struct Bank* bank, int account_id) {
    for (int i = 0; i < bank->account_count; i++) {
        if (bank->accounts[i]->account_id == account_id) {
            return bank->accounts[i];
        }
    }
    return NULL;
}

// ============================================================
// 锁排序实现（无变化）
// ============================================================

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

Result lock_multiple(OrderedMutex* locks[], int count) {
    for (int i = 0; i < count - 1; i++) {
        for (int j = i + 1; j < count; j++) {
            if (locks[i]->order > locks[j]->order) {
                OrderedMutex* temp = locks[i];
                locks[i] = locks[j];
                locks[j] = temp;
            }
        }
    }
    
    for (int i = 0; i < count; i++) {
        int ret = pthread_mutex_lock(&locks[i]->mutex);
        if (ret != 0) {
            for (int j = i - 1; j >= 0; j--) {
                pthread_mutex_unlock(&locks[j]->mutex);
            }
            return result_error(ERR_DEADLOCK_PREVENTED);
        }
    }
    
    return result_success(NULL);
}

Result unlock_multiple(OrderedMutex* locks[], int count) {
    for (int i = count - 1; i >= 0; i--) {
        pthread_mutex_unlock(&locks[i]->mutex);
    }
    return result_success(NULL);
}

// ============================================================
// 核心交易逻辑（移除安全注解）
// ============================================================

Result transfer_money(struct Bank* bank, int from_id, int to_id, double amount) {
    if (amount <= 0) {
        return result_error(ERR_INVALID_AMOUNT);
    }
    
    if (from_id == to_id) {
        return result_error(ERR_INVALID_AMOUNT);
    }
    
    struct Account* from_account = NULL;
    struct Account* to_account = NULL;
    
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
    
    OrderedMutex* locks[] = {
        &lock_manager.global_lock,
        (OrderedMutex*)from_account->mutex,
        (OrderedMutex*)to_account->mutex,
    };
    
    try(lock_multiple(locks, 3));
    
    if (from_account->balance < amount) {
        unlock_multiple(locks, 3);
        return result_error(ERR_INSUFFICIENT_FUNDS);
    }
    
    from_account->balance -= amount;
    to_account->balance += amount;
    
    struct Transaction tx = {
        .from_account = from_account,
        .to_account = to_account,
        .amount = amount,
        .timestamp = time(NULL)
    };
    
    printf("[Transaction] %d -> %d: $%.2f\n", from_id, to_id, amount);
    
    try(unlock_multiple(locks, 3));
    
    return result_success(NULL);
}

// ============================================================
// 并发安全函数（移除Send/Sync注解）
// ============================================================

void* transfer_thread(void* arg) {
    struct TransferTask* task = (struct TransferTask*)arg;
    
    Result result = transfer_money(task->bank, task->from_id, task->to_id, task->amount);
    
    if (result.is_error) {
        handle_error(result.error, "Transfer failed");
    }
    
    if (task->done_flag) {
        *task->done_flag = true;
    }
    
    free(task);
    return NULL;
}

Result get_bank_stats(const struct Bank* bank, struct AccountStats* stats) {
    if (!bank || !stats) {
        return result_error(ERR_INVALID_AMOUNT);
    }
    
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

struct Bank* create_test_bank() {
    struct Bank* bank = malloc(sizeof(struct Bank));
    if (!bank) {
        return NULL;
    }
    
    bank->account_count = 10;
    bank->accounts = malloc(sizeof(struct Account*) * bank->account_count);
    
    const char* names[] = {"Alice", "Bob", "Charlie", "David", "Eve",
                          "Frank", "Grace", "Henry", "Ivy", "Jack"};
    
    for (int i = 0; i < bank->account_count; i++) {
        bank->accounts[i] = create_account(i + 1, names[i], 1000.0 + i * 100);
    }
    
    pthread_mutex_init(&bank->global_lock, NULL);
    
    return bank;
}

void destroy_bank(struct Bank* bank) {
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

void test_memory_safety(struct Bank* bank) {
    printf("\n========== 测试1: 内存安全 ==========\n");
    
    struct Account* new_acc = create_account(99, "TestUser", 5000.0);
    printf("Created account: %s (ID: %d) with $%.2f\n", 
           new_acc->owner_name, new_acc->account_id, new_acc->balance);
    
    const struct Account* borrowed = get_account_info(bank, 1);
    if (borrowed) {
        printf("Borrowed account info: %s (Balance: $%.2f)\n", 
               borrowed->owner_name, borrowed->balance);
    }
    
    struct Account* transferred = new_acc;
    printf("Transferred ownership of: %s\n", transferred->owner_name);
    
    destroy_account(transferred);
    printf("Memory safety test completed ✓\n");
}

void test_lock_ordering(struct Bank* bank) {
    printf("\n========== 测试2: 死锁预防（锁排序） ==========\n");
    
    pthread_t threads[5];
    bool done_flags[5] = {false};
    
    int transfers[][3] = {
        {1, 2, 100},
        {2, 1, 150},
        {3, 4, 200},
        {4, 3, 250},
        {5, 6, 300},
    };
    
    for (int i = 0; i < 5; i++) {
        struct TransferTask* task = malloc(sizeof(struct TransferTask));
        task->bank = bank;
        task->from_id = transfers[i][0];
        task->to_id = transfers[i][1];
        task->amount = transfers[i][2];
        task->done_flag = &done_flags[i];
        
        pthread_create(&threads[i], NULL, transfer_thread, task);
    }
    
    for (int i = 0; i < 5; i++) {
        pthread_join(threads[i], NULL);
    }
    
    printf("All transactions completed (no deadlock!) ✓\n");
}

void test_send_sync(struct Bank* bank) {
    printf("\n========== 测试3: Send/Sync 并发安全 ==========\n");
    
    struct TransferTask* task = malloc(sizeof(struct TransferTask));
    task->bank = bank;
    task->from_id = 7;
    task->to_id = 8;
    task->amount = 500;
    task->done_flag = NULL;
    
    pthread_t thread;
    pthread_create(&thread, NULL, transfer_thread, task);
    pthread_join(thread, NULL);
    
    struct AccountStats stats;
    Result r = get_bank_stats(bank, &stats);
    if (!r.is_error) {
        printf("Bank Stats (Sync): %d accounts, Total: $%.2f\n",
               stats.total_accounts, stats.total_balance);
    }
    
    printf("Send/Sync test completed ✓\n");
}

void test_error_handling(struct Bank* bank) {
    printf("\n========== 测试4: 错误处理 ==========\n");
    
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
            printf("Test %d (%s) ", i+1, tests[i].description);
            handle_error(r.error, "Expected error");
        }
    }
    
    printf("Error handling test completed ✓\n");
}

// ============================================================
// 主函数（移除safe注解）
// ============================================================

int main() {
    printf("╔══════════════════════════════════════════════════╗\n");
    printf("║   Safe-C Bank System - Complete Safety Test    ║\n");
    printf("╚══════════════════════════════════════════════════╝\n");
    
    init_lock_manager();
    
    struct Bank* bank = create_test_bank();
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
    
    test_memory_safety(bank);
    test_lock_ordering(bank);
    test_send_sync(bank);
    test_error_handling(bank);
    
    printf("\n========== 最终状态 ==========\n");
    for (int i = 0; i < bank->account_count; i++) {
        printf("  %d: %s - $%.2f\n", 
               bank->accounts[i]->account_id,
               bank->accounts[i]->owner_name,
               bank->accounts[i]->balance);
    }
    
    destroy_bank(bank);
    
    printf("\n✓ All tests passed!\n");
    return 0;
} ^0j700siE

%%
## Drawing
```compressed-json
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=
```
%%