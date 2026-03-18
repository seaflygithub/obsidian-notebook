
## 在线下载运行双核程序

1、先在线下载 CPU1 的程序，作为固件运行在CPU1处理器上。

![[Pasted image 20251222223207.png]]


2、然后在线下载运行 CPU0 程序，CPU0 程序运行起来后，会向CPU1固件发起请求。

![[Pasted image 20251222223234.png]]


## 制作双核启动镜像

1、唯一要注意的是CPU1的链接起始地址(vitis这边设置一个临时链接地址: 0x400000，vitis例程把u-boot镜像拷贝到u-boot运行的地址，然后跳转到u-boot执行)，以及确保目标处理器选择为CPU1。

![[Pasted image 20251222223312.png]]


## 物理共享内存完整源代码

Vitis standalone裸机例程: 其中 mmc_shared_mem.h 是裸机和u-boot共用的头文件，该头文件直接放到 u-boot 源码目录顶层 include 目录即可。

```cpp
#ifndef __SHARED_MEM_BETWEEN_CPUCORES_H__
#define __SHARED_MEM_BETWEEN_CPUCORES_H__

#include <stdint.h>

// Memory address space base address:
//      CPU0=0x0000_0000  (CPU0: Vitis baremetal program)
//      CPU1=ZU48DR_PS_DDR_SIZE - 4MB  (CPU1: u-boot firmware for emmc)
//       SHM=ZU48DR_PS_DDR_SIZE - 4MB - 64MB  (SHM: Shared Memory between CPU0 and CPU1)

// #define U_BOOT_MEM_BASE (0x8000000) // 0x8000000=128MB
// #define SHARED_MEM_BASE (0x8000000 + 4*1024*1024)

// ZU48DR_PS_DDR_SIZE Test list:
// 0x40000000=1GB   <--- OK (1GB)
// 0x20000000=512MB <--- OK (1GB+512MB)
// 0x10000000=256MB <--- OK (1GB+512MB+256MB)
// 0x08000000=128MB <--- OK (1GB+512MB+256MB+128MB)
// 0x04000000=64MB  <--- OK (1GB+512MB+256MB+128MB+64MB)
// 0x02000000=32MB  <--- OK (1GB+512MB+256MB+128MB+64MB+32MB)
// 0x01000000=16MB  <--- Not OK
// 0x00800000=8MB   <--- Not OK
// 0x00400000=4MB   <--- Not OK
// 0x00200000=2MB   <--- Not OK
// #define ZU48DR_PS_DDR_SIZE (0x7C000000)
// #define U_BOOT_MEM_BASE (ZU48DR_PS_DDR_SIZE - 4*1024*1024)
// #define SHARED_MEM_BASE (ZU48DR_PS_DDR_SIZE - 4*1024*1024 - 64*1024*1024)


#define ZU48DR_PS_DDR_SIZE (0x7E000000)
#define U_BOOT_MEM_BASE (ZU48DR_PS_DDR_SIZE - 4*1024*1024)
#define SHARED_MEM_BASE (ZU48DR_PS_DDR_SIZE - 4*1024*1024 - 64*1024*1024)


#ifndef mmc_size_t
typedef unsigned long long mmc_size_t;
#endif

// mmc io sub command
enum mmc_io_flag {
	FLAG_GET_INFO = 1, // mmc info 
	FLAG_GET_DATA,     // mmc read  (data from mmc to ram)
	FLAG_SET_DATA,     // mmc write (data from ram to mmc)
};

struct vitis_mmc_info {
	char name[16];          // such as: mmc@ff170000
	uint32_t bus_speed;     // unit:Hz, such as: 51724137
	uint32_t version;       // Bit[31:16]==major, Bit[15:0]==minor
	uint32_t blocklen;      // unit:byte
	uint32_t bus_width;     // such as 4 (4-bit)
	mmc_size_t capacity; // unit:byte
};

// request from vitis to mmc
struct mmc_cmd_req {
    uint32_t dev_num;       // reserved
	enum mmc_io_flag flag;  // reference to enum mmc_io_flag
    mmc_size_t blkth;     // start_blk#
    mmc_size_t blkcnt;        // blk count will be read or write
    mmc_size_t buf_offset;    // data payload addr: SHARED_DATA_BUF + buf_offset
};

// response from mmc to vitis
struct mmc_cmd_resp {
    int32_t ret;         // 0=success, others=fail
};

// sync state between vitis and mmc
typedef enum {
    STATE_IDLE = 0,  // idle (no request)
    STATE_REQUEST,   // Vitis send request to U-Boot
    STATE_DONE       // U-Boot finish request, and wait for vitis to read
} shared_state_t;

// header of shared memory (layout: state + request + response + data_buf)
struct shared_mem {
    shared_state_t state;            // state (offset:0)
    struct mmc_cmd_req req;          // request (offset:4)
    struct mmc_cmd_resp resp;        // response (offset:4+sizeof(struct mmc_cmd_req))
    uint8_t data_buf[1024*1024*60];  // data buffer (offset:4+sizeof(struct mmc_cmd_req)+sizeof(struct mmc_cmd_resp))
};

#define SHARED_STATE ((volatile shared_state_t *)(SHARED_MEM_BASE + offsetof(struct shared_mem, state)))
#define SHARED_REQ ((volatile struct mmc_cmd_req *)(SHARED_MEM_BASE + offsetof(struct shared_mem, req)))
#define SHARED_RESP ((volatile struct mmc_cmd_resp *)(SHARED_MEM_BASE + offsetof(struct shared_mem, resp)))
#define SHARED_DATA_BUF ((volatile uint8_t *)(SHARED_MEM_BASE + offsetof(struct shared_mem, data_buf)))

static uint32_t get_current_cpu_id(void) {
	
	uint64_t mpidr = 0;
    __asm__ __volatile__(
        "mrs %0, mpidr_el1\n"
        : "=r"(mpidr)
        :
        : "memory"
    );
    return (uint32_t)(mpidr & 0xFF);
}

int vitis_mmc_init(void);
int vitis_mmc_read_blocks(mmc_size_t blkth, mmc_size_t rd_blkcnt, void *buf);
int vitis_mmc_write_blocks(mmc_size_t blkth, mmc_size_t wr_blkcnt, const void *buf);

// Following interfaces are compatible with Xilinx SDPS
#define XSdPs_LookupConfig(a) vitis_mmc_init()
#define XSdPs_CfgInitialize(a,b,c) vitis_mmc_init()
#define XSdPs_CardInitialize(a) vitis_mmc_init()
#define XSdPs_WritePolled(reserved, blkth, blkcnt, buffer) vitis_mmc_write_blocks(blkth, blkcnt, buffer)
#define XSdPs_ReadPolled(reserved, blkth, blkcnt, buffer) vitis_mmc_read_blocks(blkth, blkcnt, buffer)

#endif // __SHARED_MEM_BETWEEN_CPUCORES_H__
```


```cpp

#include "mmc_shared_mem.h"
#include "xil_cache.h"
#include <stdint.h>
#include <errno.h>

static int s_mmc_block_size = 512;
static int s_mmc_wait_timeout = 100000;//unit:us

int vitis_mmc_init(void)
{
    static int inited = 0;
    if (inited) return 0;

    inited = 1;
    Xil_DCacheEnable();
    Xil_DCacheInvalidate();
    memset(SHARED_DATA_BUF, 0, 64);
    Xil_DCacheFlushRange(SHARED_DATA_BUF, 64);
    printf("[%s] XSdPs_CardInitialize Success\r\n", __func__);
    return 0;
}

int vitis_mmc_info(struct vitis_mmc_info *info)
{
	// wait for previous request complete
	while (*SHARED_STATE != STATE_IDLE) { usleep(s_mmc_wait_timeout); }

    // write shared memory
	SHARED_REQ->flag = FLAG_GET_INFO;
    Xil_DCacheFlushRange((uintptr_t)SHARED_REQ, sizeof(struct mmc_cmd_req));

    // trigger request
    *SHARED_STATE = STATE_REQUEST;

    // wait done
    while (*SHARED_STATE != STATE_DONE) { usleep(s_mmc_wait_timeout); }

    // read shared memory
    Xil_DCacheInvalidateRange((uintptr_t)SHARED_RESP, sizeof(struct mmc_cmd_resp));
    Xil_DCacheInvalidateRange((uintptr_t)SHARED_DATA_BUF, sizeof(*info));
    int ret = SHARED_RESP->ret;
    if (ret == 0) {
        if (info) {
            *info = *((struct vitis_mmc_info *)SHARED_DATA_BUF);
            s_mmc_block_size = info->blocklen;
        }

        *SHARED_STATE = STATE_IDLE;
        return 0;
    }

    *SHARED_STATE = STATE_IDLE;
    return ret;
}

int vitis_mmc_read_blocks(mmc_size_t blkth, mmc_size_t rd_blkcnt, void *buf)
{
	// wait for previous request complete
	while (*SHARED_STATE != STATE_IDLE) { usleep(s_mmc_wait_timeout); }


    // write to shared memory
	SHARED_REQ->flag = FLAG_GET_DATA;
	SHARED_REQ->blkth = blkth;
	SHARED_REQ->blkcnt = rd_blkcnt;
	SHARED_REQ->buf_offset = 0;
	Xil_DCacheFlushRange((uintptr_t)SHARED_REQ, sizeof(struct mmc_cmd_req));

	// trigger request
	*SHARED_STATE = STATE_REQUEST;

    // wait for response
	while (*SHARED_STATE != STATE_DONE) { usleep(s_mmc_wait_timeout); }

    // read from shared memory
    Xil_DCacheInvalidateRange((uintptr_t)SHARED_RESP, sizeof(struct mmc_cmd_resp));
    Xil_DCacheInvalidateRange((uintptr_t)SHARED_DATA_BUF, rd_blkcnt * s_mmc_block_size);
    int ret = SHARED_RESP->ret;
    if (ret == 0) {

        if (buf) memcpy(buf, (void *)SHARED_DATA_BUF, rd_blkcnt * s_mmc_block_size);
    	// buffer_dump(SHARED_DATA_BUF, 50);

    	*SHARED_STATE = STATE_IDLE;
    	return 0;
    }

    *SHARED_STATE = STATE_IDLE;
    return ret;
}

int vitis_mmc_read_bytes(mmc_size_t blkth, mmc_size_t rd_bytes, void *buf)
{
    mmc_size_t blkcnt = rd_bytes / s_mmc_block_size;
    mmc_size_t blk_offset = rd_bytes % s_mmc_block_size;
    if (blkcnt==0) {
        if (blk_offset != 0) {
            blkcnt = 1;
        } else {
            printf("warnning: rd_bytes must be larger than 0\r\n");
            return -EINVAL;
        }
    } else {
        if (blk_offset != 0)
            blkcnt += 1;
    }


	// wait for previous request complete
	while (*SHARED_STATE != STATE_IDLE) { usleep(s_mmc_wait_timeout); }


    // write to shared memory
	SHARED_REQ->flag = FLAG_GET_DATA;
	SHARED_REQ->blkth = blkth;
	SHARED_REQ->blkcnt = blkcnt;
	SHARED_REQ->buf_offset = 0;
	Xil_DCacheFlushRange((uintptr_t)SHARED_REQ, sizeof(struct mmc_cmd_req));

	// trigger request
	*SHARED_STATE = STATE_REQUEST;

    // wait for response
	while (*SHARED_STATE != STATE_DONE) { usleep(s_mmc_wait_timeout); }

    // read from shared memory
    Xil_DCacheInvalidateRange((uintptr_t)SHARED_RESP, sizeof(struct mmc_cmd_resp));
    Xil_DCacheInvalidateRange((uintptr_t)SHARED_DATA_BUF, rd_bytes);
    int ret = SHARED_RESP->ret;
    if (ret == 0) {

        if (buf) memcpy(buf, (void *)SHARED_DATA_BUF, rd_bytes);
    	// buffer_dump(SHARED_DATA_BUF, 50);

    	*SHARED_STATE = STATE_IDLE;
    	return 0;
    }

    *SHARED_STATE = STATE_IDLE;
    return ret;
}

int vitis_mmc_write_blocks(mmc_size_t blkth, mmc_size_t wr_blkcnt, const void *buf)
{
	// wait for previous request complete
	while (*SHARED_STATE != STATE_IDLE) { usleep(s_mmc_wait_timeout); }


    // write to shared memory
	SHARED_REQ->flag = FLAG_SET_DATA;
	SHARED_REQ->blkth = blkth;
	SHARED_REQ->blkcnt = wr_blkcnt;
	SHARED_REQ->buf_offset = 0;
	Xil_DCacheFlushRange((uintptr_t)SHARED_REQ, sizeof(struct mmc_cmd_req));
    if (buf) {
        memcpy(SHARED_DATA_BUF, buf, wr_blkcnt * s_mmc_block_size);
        Xil_DCacheFlushRange((uintptr_t)SHARED_DATA_BUF, wr_blkcnt * s_mmc_block_size);
    }

	// trigger request
	*SHARED_STATE = STATE_REQUEST;

    // wait for response
	while (*SHARED_STATE != STATE_DONE) { usleep(s_mmc_wait_timeout); }

    // read from shared memory
    Xil_DCacheInvalidateRange((uintptr_t)SHARED_RESP, sizeof(struct mmc_cmd_resp));
    int ret = SHARED_RESP->ret;

    *SHARED_STATE = STATE_IDLE;
    return ret;
}

int vitis_mmc_write_bytes(mmc_size_t blkth, mmc_size_t wr_bytes, const void *buf)
{
    mmc_size_t blkcnt = wr_bytes / s_mmc_block_size;
    mmc_size_t blk_offset = wr_bytes % s_mmc_block_size;
    if (blkcnt==0) {
        if (blk_offset != 0) {
            blkcnt = 1;
        } else {
            printf("warnning: wr_bytes must be larger than 0\r\n");
            return -EINVAL;
        }
    } else {
        if (blk_offset != 0)
            blkcnt += 1;
    }

    // read from shared mem (rd-mod-wr)
    int ret = vitis_mmc_read_bytes(blkth, wr_bytes, NULL);
    if (ret) return ret;


	// wait for previous request complete
	while (*SHARED_STATE != STATE_IDLE) { usleep(s_mmc_wait_timeout); }


    // write to shared memory
	SHARED_REQ->flag = FLAG_SET_DATA;
	SHARED_REQ->blkth = blkth;
	SHARED_REQ->blkcnt = blkcnt;
	SHARED_REQ->buf_offset = 0;
	Xil_DCacheFlushRange((uintptr_t)SHARED_REQ, sizeof(struct mmc_cmd_req));
    if (buf) {
        memcpy(SHARED_DATA_BUF, buf, wr_bytes);
        Xil_DCacheFlushRange((uintptr_t)SHARED_DATA_BUF, wr_bytes);
    }

	// trigger request
	*SHARED_STATE = STATE_REQUEST;

    // wait for response
	while (*SHARED_STATE != STATE_DONE) { usleep(s_mmc_wait_timeout); }

    // read from shared memory
    Xil_DCacheInvalidateRange((uintptr_t)SHARED_RESP, sizeof(struct mmc_cmd_resp));
    ret = SHARED_RESP->ret;

    *SHARED_STATE = STATE_IDLE;
    return ret;
}
```






下面是 u-boot 服务的核心代码，就是修改主循环代码(common/main.c)，让其定时轮询共享内存的请求状态，一旦裸机cpu0这边发起读写emmc请求，u-boot 这边能立马响应并执行相关操作，把相关数据存放到共享内存指定位置。

```cpp
static void handle_mmc_request(void)
{
    struct mmc_cmd_req req = *SHARED_REQ; // from shared memory
    struct mmc_cmd_resp resp = {.ret = -1 };
    struct cmd_tbl *cmdtp;
    char cmd_str[128] = {0};
    int valid_req = 1; // 1=true, 0=false

    switch (req.flag) {
        case FLAG_GET_INFO:
        {
            // such as: mmc info
            snprintf(cmd_str, sizeof(cmd_str), "mmc info %s", " ");
            break;
        }
        case FLAG_GET_DATA:
        {
            // such as: mmc read 0x20000000 0 1
            snprintf(cmd_str, sizeof(cmd_str),
                    "mmc read 0x%lx 0x%lx 0x%lx",
                    SHARED_DATA_BUF +  req.buf_offset,
                    req.blkth,
                    req.blkcnt);
            break;
        }
        case FLAG_SET_DATA:
        {
            // such as: mmc write 0x20000000 0 1
            snprintf(cmd_str, sizeof(cmd_str),
                    "mmc write 0x%lx 0x%lx 0x%lx",
                    SHARED_DATA_BUF +  req.buf_offset,
                    req.blkth,
                    req.blkcnt);
            break;
        }
        default:
        {
            valid_req = 0;
            break;
        }
    }

    if (valid_req) {
        cmdtp = find_cmd("mmc");
        if (cmdtp) {
            resp.ret = run_command(cmd_str, 0);
        }
    }

    // write back result, and update state done
    *SHARED_RESP = resp;
    *SHARED_STATE = STATE_DONE;
}

/* We come here after U-Boot is initialised and ready to process commands */
void main_loop(void)
{
	const char *s;

	bootstage_mark_name(BOOTSTAGE_ID_MAIN_LOOP, "main_loop");

	if (IS_ENABLED(CONFIG_VERSION_VARIABLE))
		env_set("ver", version_string);  /* set version variable */

	cli_init();

	if (IS_ENABLED(CONFIG_USE_PREBOOT))
		run_preboot_environment_command();

	if (IS_ENABLED(CONFIG_UPDATE_TFTP))
		update_tftp(0UL, NULL, NULL);

    // committed by zu48dr
    {
        // s = bootdelay_process();
        // if (cli_process_fdt(&s))
        // 	cli_secure_boot_cmd(s);
        // autoboot_command(s);
    }

    {
        // clean data
        memset(SHARED_MEM_BASE, 0, 64);
		    printf("%s():CPU%d:start fw complete at 0x%lx\\n",
		        __func__,get_current_cpu_id(), CONFIG_SYS_TEXT_BASE);

        // infinite loop
        for (;;) {

            // req from cpu0(vitis project)
            if (*SHARED_STATE == STATE_REQUEST) {
                // printf("zu48dr:%d: emmc request triggered\\n", __LINE__);
                handle_mmc_request();
            }

            mdelay(100);
        }
    }

	cli_loop();
	panic("No CLI available");
}

```




