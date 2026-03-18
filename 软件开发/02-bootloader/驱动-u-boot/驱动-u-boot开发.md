
# 模拟最简单驱动模型

借鉴 u-boot 的类设备管理模型，帮我实现一个最小的设备、驱动管理代码，满足抽象管理，满足用户自上向下读写访问。可以用一个简单的设备来举例。

“类——设备——驱动” 这种三层结构，比如 “LED类——LED设备——LED驱动”。

对下面的代码操作的对象要有画面感，后续通过画面感来浓缩该知识点。实际的项目代码中，一定会糅杂各种知识点，这些知识点就像不同频率的波形一样交织在一起，我们学习其中某个知识点时，就需要想傅里叶变换一样把某个知识点单独提取出来学习，等把所有主要知识点都掌握之后，再根据需要把它们糅在一起，就好理解了。

![[Pasted image 20251229113543.png]]



一、**核心数据结构**

```cpp
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* 1. 设备操作接口：定义同类设备的通用行为 */
struct device_ops {
    int (*read)(void *priv, int addr, char *buf, int len);  // 读操作
    int (*write)(void *priv, int addr, const char *buf, int len);  // 写操作
};

/* 2. 设备类（uclass）：管理同类设备 */
struct uclass {
    const char *name;               // 类名称（如 "led"）
    struct device *devices;         // 设备链表头
    struct device_ops *default_ops; // 类默认操作（可选）
};

/* 3. 设备实例（udevice）：代表具体设备 */
struct device {
    const char *name;               // 设备名称（如 "led0"）
    struct uclass *uclass;          // 所属类
    struct device *next;            // 链表下一个设备
    void *priv;                     // 私有数据（硬件相关信息）
    struct device_ops *dev_ops;     // 设备专属操作（优先于类默认）
};

/* 4. 驱动：绑定硬件与操作逻辑 */
struct driver {
    const char *name;               // 驱动名称（如 "gpio_led"）
    const char *compatible;         // 匹配设备的标识（类似设备树compatible）
    struct device_ops *dev_ops;     // 驱动实现的操作
    void *(*probe)(const char *name); // 初始化设备并返回私有数据
};
```

二、**核心管理逻辑（注册和查找）**

```cpp
/* 全局类链表和驱动链表 */
static struct uclass *uclass_list = NULL;
static struct driver *driver_list = NULL;

/* 注册类 */
void uclass_register(struct uclass *cls) {
    cls->devices = NULL;
    // 插入类链表头部
    cls->next = uclass_list;
    uclass_list = cls;
    printf("注册类: %s\\n", cls->name);
}

/* 注册驱动 */
void driver_register(struct driver *drv) {
    // 插入驱动链表头部
    drv->next = driver_list;
    driver_list = drv;
    printf("注册驱动: %s (兼容: %s)\\n", drv->name, drv->compatible);
}

/* 查找类 */
struct uclass *uclass_find(const char *name) {
    struct uclass *cls;
    for (cls = uclass_list; cls; cls = cls->next) {
        if (!strcmp(cls->name, name))
            return cls;
    }
    return NULL;
}

/* 查找驱动（根据compatible） */
struct driver *driver_find(const char *compatible) {
    struct driver *drv;
    for (drv = driver_list; drv; drv->next) {
        if (!strcmp(drv->compatible, compatible))
            return drv;
    }
    return NULL;
}

/* 向类中添加设备（设备实例化） */
struct device *device_add(const char *uclass_name, const char *dev_name, 
    const char *compatible) {
    // 1. 查找类和驱动
    struct uclass *cls = uclass_find(uclass_name);
    struct driver *drv = driver_find(compatible);
    if (!cls || !drv) {
        printf("设备添加失败：类或驱动不存在\\n");
        return NULL;
    }

    // 2. 创建设备实例
    struct device *dev = malloc(sizeof(struct device));
    dev->name = dev_name;
    dev->uclass = cls;
    dev->dev_ops = drv->dev_ops;       // 绑定驱动的操作
    dev->priv = drv->probe(dev_name);  // 调用驱动初始化硬件

    // 3. 插入类的设备链表
    dev->next = cls->devices;
    cls->devices = dev;
    printf("添加设备: %s (类: %s, 驱动: %s)\\n", dev_name, uclass_name, drv->name);
    return dev;
}

/* 从类中查找设备 */
struct device *device_find(struct uclass *cls, const char *dev_name) {
    struct device *dev;
    for (dev = cls->devices; dev; dev = dev->next) {
        if (!strcmp(dev->name, dev_name))
            return dev;
    }
    return NULL;
}
```

三、**LED 设备示例（硬件实现）**

```cpp
/* LED 私有数据（硬件信息） */
struct led_priv {
    int gpio;      // GPIO 引脚号
    char status;   // 状态（0: 灭, 1: 亮）
};

/* LED 读操作：读取当前状态 */
static int led_read(void *priv, int addr, char *buf, int len) {
    struct led_priv *lp = priv;
    if (addr != 0 || len != 1)
        return -1;
    buf[0] = lp->status ? '1' : '0';  // 地址0存储状态
    printf("读取 LED 状态: %c\\n", buf[0]);
    return 0;
}

/* LED 写操作：控制亮灭 */
static int led_write(void *priv, int addr, const char *buf, int len) {
    struct led_priv *lp = priv;
    if (addr != 0 || len != 1)
        return -1;
    lp->status = (buf[0] == '1');  // 地址0写入状态
    printf("设置 LED 状态: %s\\n", lp->status ? "亮" : "灭");
    return 0;
}

/* LED 驱动操作集 */
static struct device_ops led_ops = {
    .read = led_read,
    .write = led_write,
};

/* LED 驱动 probe 函数：初始化硬件 */
static void *led_probe(const char *name) {
    struct led_priv *lp = malloc(sizeof(struct led_priv));
    // 模拟 GPIO 初始化（实际中应配置硬件寄存器）
    lp->gpio = 12;  // 假设使用 GPIO12
    lp->status = 0; // 初始状态：灭
    printf("初始化 LED 硬件 (GPIO: %d)\\n", lp->gpio);
    return lp;
}

/* 定义 LED 驱动 */
struct driver led_driver = {
    .name = "gpio_led",
    .compatible = "myboard,led",  // 匹配标识
    .dev_ops = &led_ops,
    .probe = led_probe,
};
```

四、**上层访问接口（用户接口）**

层次结构：用户 —— 类 —— 设备 —— 操作

```cpp
/* 上层读设备接口 */
int uclass_read(const char *cls_name, const char *dev_name, int addr, char *buf, int len) {
    struct uclass *cls = uclass_find(cls_name);
    struct device *dev = device_find(cls, dev_name);
    if (!cls || !dev)
        return -1;

    // 优先使用设备自身的操作，否则用类默认操作
    struct device_ops *dev_ops = dev->dev_ops ? dev->dev_ops : cls->default_ops;
    return dev_ops->read(dev->priv, addr, buf, len);
}

/* 上层写设备接口 */
int uclass_write(const char *cls_name, const char *dev_name, int addr, const char *buf, int len) {
    struct uclass *cls = uclass_find(cls_name);
    struct device *dev = device_find(cls, dev_name);
    if (!cls || !dev)
        return -1;

    struct device_ops *dev_ops = dev->dev_ops ? dev->dev_ops : cls->default_ops;
    return dev_ops->write(dev->priv, addr, buf, len);
}
```

五、**测试代码（模拟用户访问）**

```cpp
int main() {
    // 1. 注册类
    struct uclass led_uclass = {.name = "led"};
    uclass_register(&led_uclass);

    // 2. 注册驱动
    driver_register(&led_driver);

    // 3. 添加设备（实例化）
    device_add("led", "led0", "myboard,led");  // 类名+设备名+兼容标识

    // 4. 上层访问设备
    char buf[1];
    uclass_write("led", "led0", 0, "1", 1);  // 开灯
    uclass_read("led", "led0", 0, buf, 1);   // 读状态

    uclass_write("led", "led0", 0, "0", 1);  // 关灯
    uclass_read("led", "led0", 0, buf, 1);   // 读状态

    return 0;
}
```







# bottom





