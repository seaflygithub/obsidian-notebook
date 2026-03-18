
# CNN识别手写数字

附件: Handwritten-digit-recognition-based-on-CNN-master.zip
网盘: Handwritten-digit-recognition-based-on-CNN-master.zip
草稿: [[Handwritten-digit-recognition.excalidraw]]
仓库: https://github.com/IammyselfYBX/Handwritten-digit-recognition-based-on-CNN


## 正向传播缩略图

（详情见草稿）
```cpp
// MatrixMultiply(1,1152,180,绿色矩阵,紫色矩阵,蓝色矩阵);
void MatrixMultiply(int w,int h,int out_deminsion,
    double *input_matrix,double *para_layer,double*output_matrix) {
    for(int i=0;i<w;i++) // w=1
        for(int j=0;j<out_deminsion;j++){ // out_deminsion=180
            output_matrix[i*w+j]=0; 
            for(int k=0;k<h;k++) // h=1152
                output_matrix[i*w+j] += 
                    input_matrix[i*w+k]*para_layer[k*out_deminsion+j];
        }
}
```

## 反向传播缩略图

（详情见草稿）
```cpp
void CalculateMatrixGrad(int w,int h,
    double *input_matrix,double *grad,double *output_matrix) {
    for(int i=0;i<w;i++){
        output_matrix[i]=0;//梯度清空，方便累加
        for(int j=0;j<h;j++){
            output_matrix[i]+=input_matrix[i*h+j]*grad[j];
        }
    }
}
```


```cpp
void MatrixBackPropagationMultiply(int w,int h,
    double *para,double *grad,double *rgrad) {
    for(int i=0;i<w;i++)
        for(int j=0;j<h;j++)
            rgrad[i*h+j]=para[i]*grad[j];
}
```

```cpp
// 计算交叉熵损失
double Cross_entropy(double *a,int m) {
    double u=0;
    u=(-log10(a[m]));
    return u;
}

// 更新网络参数
void MatrixBackPropagation(int w,int h,
    double *input_matrix,double *output_matrix) {
    for(int i=0;i<w;i++)
        for(int j=0;j<h;j++)
            output_matrix[i*h+j]-=lr*input_matrix[i*h+j];
}
```

```cpp
// 矩阵分割, 平分成2个矩阵, 因为有2个分支
void MatrixSplit(double *input_matrix,
    double *splited_matrix1,double *splited_matrix2){
    for(int idx=0;idx<1152;idx++)
        if(idx<576)
            splited_matrix1[idx]=input_matrix[idx];
        else
            splited_matrix2[idx-576]=input_matrix[idx];
}

// 反向激活
void ReluBackPropagation(int w,
    double *input_matrix,double *grad,double *output_matrix){
    for(int i=0;i<w;i++)
        if(input_matrix[i]>0) output_matrix[i]=1*grad[i];
        else output_matrix[i]=0.05*grad[i];
}

// 翻转卷积核，翻转180度
void OverturnKernel(int k,
    double *input_matrix,double *output_matrix){
    for(int i=0;i<k;i++)
        for(int j=0;j<k;j++)
            output_matrix[(k-1-i)*k+(k-1-j)]=input_matrix[i*k+j];
}
```

```cpp
// 激活函数: ReLU, 用来给模型注入"非线性", 主要用来抑制负值
void Relu(int w,int h,
    double *input_matrix,double *output_matrix){
    for(int i=0;i<w;i++)
       for(int j=0;j<h;j++)
          output_matrix[i*w+j]=
              max(input_matrix[i*w+j],input_matrix[i*w+j]*0.05);
    // 公式: ReLU(x)=max(x,0.05x)
}

// 卷积操作
void Conv2d(int w,int h,int k,
    double *input_matrix,double *kernel,double *out_matrix){
    for(int i=0;i<w-k+1;i++)        
        for(int j=0;j<h-k+1;j++){   
            out_matrix[i*(w-k+1)+j]=0; 
            for(int row=i;row<i+3;row++)
                for(int col=j;col<j+3;col++)
                    out_matrix[i*(w-k+1)+j] +=
                        input_matrix[row*w+col]*kernel[(row-i)*k+(col-j)];
        }
}

// 该函数用于更新网络参数
void MatrixBackPropagation(int w,int h,
    double *input_matrix,double *output_matrix) {
    for(int i=0;i<w;i++)
      for(int j=0;j<h;j++)
        output_matrix[i*h+j]-=lr*input_matrix[i*h+j];
}
```



# YOLOv3目标检测

## 基础认识

YOLO特点：速度极快，适合实时场景（如自动驾驶、监控）。

<font color=blue>YOLO 和 CNN 是什么关系？以及区别是什么？</font>

YOLO 是一种**专门用于 “目标检测” 的算法**，它的底层网络完全基于 CNN 构建：
- 早期 YOLO（v1/v2）使用自定义的 CNN 作为 “特征提取 backbone”；
- YOLOv3 及之后版本采用更高效的 CNN 架构（如 Darknet-53，本质是包含残差连接的深度 CNN）；
- YOLO 的核心逻辑（“一次性预测目标的位置和类别”），依赖 CNN 提取的图像特征来实现 —— 没有 CNN 的特征提取能力，YOLO 无法完成目标检测。


## 范例使用

附件: 网盘: darknet-master.zip
官方链接: [[darknet]]


**1、修改编译配置**: 解压之后，修改顶层的 Makefile 最开始几行，把这些开关都设置为0，因为我电脑是虚拟机 Ubuntu 20.04 且没有装 opencv、NVIDIA设施。已修改存网盘。

**2、编译**: 直接执行make

**3、测试运行**: 用现成的权重文件和数据来测试

```bash
#系统环境:虚拟机Ubuntu20.04、无GPU和opencv

./darknet detect cfg/yolov3.cfg yolov3.weights data/dog.jpg
#或者
./darknet detector test cfg/coco.data cfg/yolov3.cfg ../yolov3.weights data/dog.jpg
```

**4、标签文件**: data/coco.names



## 代码分析-检测推理主流程

**test_detector()**

0、首先要明白推理和训练的区别，推理就是前向传播，即输入图片，输出结果；而训练则是包含前向传播和反向传播，即输入图片，输出结果会反向传给输入端，来进行学习。推理也可以称为预测。

1、先从最简单的图示开始探究，至少有个简单的全局观，下面是分析主流程代码总结的简图。

![[Pasted image 20251222111306.png]]

1、从 test_detector() 开始
2、后续的探究，都在这张全局图上逐渐展开，这也是人脑学习新知识的路径，从简单到复杂。
3、上面的加载名称，可以理解为训练数据的标准答案，AI预测完会从中挑选结果。
4、上面的加载网络，包括网络配置文件的加载、网络权重文件的加载、网络参数设置等。
5、本节知道这些就足够了。

---

**加载名称**

![[Pasted image 20251222111339.png]]

1、加载名称列表，其实就是各种动物、物品的字符串名称，并存放在一个文本文件里，代码需要把它们加载到内存里，也就是加载到指定的字符串数组里。其中 coco.names 相当于一本 “数字转文字的字典”。
![[Pasted image 20251222111351.png]]


2、加载字符集图片，预测完要在图片上框框标记吧，总是需要框住目标，然后给目标标记上名称吧，这里目标名称，就是文字组成的，这里的字符集图片，其实可以理解为字库。

![[Pasted image 20251222111410.png]]


3、加载字符集图片的原理剖析如下图所示：就是把图像的RGB三种颜色通道的像素值单独剥离出来，分别存放到三个数组里，以备后续使用。

![[Pasted image 20251222111425.png]]

---

**加载网络**

![[Pasted image 20251222111443.png]]

1、加载配置，cfg/yolov3.cfg 文件，相当于网络训练/预测的内置参数集合，它定义了整个网络的整体结构、各层参数、训练策略等关键信息。比如卷积层怎么配置等等。

2、加载权重，yolov3.weight 文件，你可以理解为这是之前已经预训练好的卷积核内的值，可以用来增量训练，或者用来识别。

3、设置批次，即同时处理多少张图片。在执行训练任务时，为了利用 GPU 并行计算能力加速训练，批次大小通常设为较大值比如16、32、64等，让网络同时处理多个样本，提高计算效率。在执行预测任务时，如果是识别单张图片，通常批次设置为1，如果是视频这种，批次设置为2、4、8这种，一般不会设置很大。

```cpp
// 预测图片时, 批次设置为1
set_batch_network(net, 1);
```


---

**开始预测**

对应的函数 network_predict()，把要预测的图片，输入进来，然后调用该函数进行预测。

---

**获取结果**

![[Pasted image 20251222111523.png]]

1、获取所有检测框，get_network_boxes()函数，网络原始输出中包含大量低置信度的预测框（可能是误检），该函数会根据设定的**置信度阈值（`thresh`）** 进行筛选，（例如 `thresh=0.5` 时，只保留置信度 50% 以上的框）。

2、去除所有重复框，do_nms_sort()函数，通过非极大值抑制(NMS)的方法去除重复框，基本原理是通过筛选出置信度最高的框，并移除与它高度重叠的其他框，从而保留最准确的目标检测结果。

3、绘制最终检测框，draw_detections()函数，其作用是在原始图像上绘制边界框、类别标签和置信度等信息，让检测结果以直观的方式呈现（人眼可直接理解）。

4、保存结果图片，save_image()函数，把绘制检测框的最终结果图片保存到文件。


## 代码分析-网络结构

1、前面已经做了基础的铺垫，对顶层的一些功能做了基本介绍，至少让我们知道了顶层做了哪些行为，这些行为的目的是什么，能了解到这一步就非常好了，后续会逐渐深入探究下去。

![[Pasted image 20251222111555.png]]


2、通过对加载配置的探究，parse_network_cfg()函数，通过分析代码得知实际加载了哪些所谓的层(layers)。如下图所示，梳理出整个网络的每个层，先暂时不关心每个层的详细配置，先从整体层面看看当前的网络配置有哪些层。cfg/yolov3.cfg 配置文件就配置了整个网络结构，网络结构如下图。

![[Pasted image 20251222111613.png]]


3、我们需要知道v3的网络结构为上图那样子，然后需要了解其中用到的每个类型层的作用和基本参数等信息，比如卷积层、shortcut层、YOLO层、ROUTE层、UPSAMPLE层。

4、加载权重文件，load_weights()函数，如果存在权重文件，则调用此函数加载。


---

**开始预测**

1、首先要把输入图片转化成网络需要的格式，load_image_color()函数加载原始图像并转换为网络可处理的格式，letterbox_image()函数对原始图像进行 "letterbox 缩放"，使其尺寸适配网络输入要求（net->w 和 net->h），同时保持原始图像的宽高比，避免目标变形。

2、开始预测，调用 network_predict() 函数，而该函数进一步调用 forward_network() 函数。


## 代码分析-各层配置

D:\project\app\yolov3\darknet-master\cfg\yolov3.cfg

**卷积层**

```cpp
[convolutional]
batch_normalize=1 // 1=启用归一化处理
filters=32        // 表示该层有32个卷积核
size=3            // 每个核尺寸是:3x3
stride=1          // 卷积核的滑动步长是1
pad=1             // 1=启用边界填充，避免因卷积操作导致特征图尺寸缩小过快
activation=leaky  // 卷积层的激活函数，这里指定为 Leaky ReLU 函数
```

activation=leaky 卷积层的激活函数，这里指定为 Leaky ReLU 函数，作用是解决了普通 ReLU 对负输入 “死亡” 的问题（负输入保留微小梯度），更适合目标检测等需要捕捉多尺度特征的场景。

activation=linear 这个是线性激活，即 f(x)=x；上面的 leaky，即 x = (x>0)? x:x*0.1;

pad=1 1=启用边界填充，作用是保护图像边缘的特征信息，避免因卷积操作导致特征图尺寸缩小过快。

batch_normalize=1 1=启用归一化处理，作用是加速模型训练收敛、缓解梯度消失、降低对学习率的敏感度，同时减少过拟合风险。

---

**shortcut层**

```cpp
[shortcut]
from=-3
activation=linear
```

from=-3 基于当前shortcut层往前数第 3 层的输出，比如当前 `shortcut` 是网络的第 10 层，则它会接收第 7 层（10-3=7）的输出。该层作用是定义残差连接的 “跳跃起点”，将更早层的特征直接引入当前层，实现跨层特征融合。这种设计让浅层的原始特征（如边缘、纹理）能与深层的抽象特征（如目标部件）结合，避免特征在多层传递中丢失。

activation=linear 指定 shortcut 层的激活函数为线性激活，即 $f(x)=x$ 。该层作用是保证残差连接的特征能 “无损失” 地传递。残差连接的核心是 “输入特征 + 卷积层输出特征”（残差相加），线性激活确保相加后的特征不会被非线性函数扭曲，从而让梯度在反向传播时能直接通过 `shortcut` 层流回浅层，缓解梯度消失问题。

shortcut 通过跨层连接，并通过 `linear` 激活实现特征的直接相加，作用是：
- 正向传播：融合不同层级的特征，保留原始信息，避免特征退化；
- 反向传播：让梯度直接回传至浅层，解决深层网络的梯度消失问题，使网络能稳定训练到更深的层数（如 YOLOv3 主干网 Darknet-53 的 53 层）。



---

**yolo层**

```cpp
[yolo]
mask = 0,1,2    // (大、中、小)选择小尺寸锚框
anchors = 10,13,  16,30,  33,23,  30,61,  62,45,  59,119,  116,90,  156,198,  373,326
classes=80      // 80个类别
num=9           // 上述anchors中锚框总数为9
jitter=.3       // 边界框的随机抖动幅度:30%,仅训练时生效
ignore_thresh = .7   // 预测框与真实框的重叠度在(0.7,1]区间, 则不计算分类损失和置信度损失
truth_thresh = 1     // 真实框的匹配阈值
random=1
```

yolo层是YOLOv3网络的检测输出层，所有参数都围绕目标检测的核心逻辑（锚框匹配、类别预测、置信度筛选等）配置，直接决定检测效果。这一层的配置参数最多，所以重点关注该层。

mask=0,1,2 从 anchors 列表中选择指定索引的锚框，作为当前 yolo 层的可用锚框。从输入到输出，共3个yolo层，且每个yolo层的锚框尺寸依次减小(大、中、小)，对应的mask索引值从(大目标:6,7,8、中目标:3,4,5、小目标:0,1,2)，也就是锚框从大尺寸到小尺寸，从而实现多尺度覆盖。

classes=80 网络会为每个检测框输出 80 个类别概率，表示框内目标属于各类别的可能性。若自定义数据集（如仅检测 “猫”“狗”），需将 `classes` 改为对应数量（如 2），同时调整 `filters`（卷积层输出通道数，公式：`filters = (classes + 5) × 3`）。

num=9 告知网络当前配置的锚框总数，即上面 anchors 里总共有9个锚框。

jitter=.3 控制边界框的随机抖动幅度（范围 0~1）。通过随机调整真实目标框的位置、尺寸（抖动幅度为 30%），增强训练数据的多样性，提升模型的泛化能力（避免过拟合）。注意，推理时 `jitter` 会失效，仅在训练阶段起作用。

ignore_thresh = .7 置信度忽略阈值，用于训练时的损失计算。训练时，若预测框与真实框的 IoU（重叠度）在 `(truth_thresh, ignore_thresh]` 区间（即 0.7~1 之间），该预测框会被标记为 “忽略框”，不计算分类损失和置信度损失，仅优化坐标损失。目的是避免惩罚那些与真实框高度重叠但未被选中的预测框，减少训练噪声。【分类损失】、【置信度损失】、【坐标损失】

truth_thresh = 1 真实框匹配阈值，用于判断预测框是否与真实框匹配。训练时，若预测框与真实框的 IoU ≥ `truth_thresh`（这里为 1，即完全重叠），则认为该预测框成功匹配真实目标，需要计算完整损失（坐标、置信度、分类损失）。阈值为 1 表示严格匹配，确保只有精准定位的预测框才会被计入有效训练样本。

random=1 控制训练时是否启用随机缩放、裁剪等数据增强（1 启用，0 禁用）。启用后，训练时会随机调整输入图像的尺寸、裁剪区域，进一步增加数据多样性，提升模型对不同尺度、角度目标的适应能力。注意，推理时需设为 0，确保输入图像尺寸固定，检测结果稳定。

各参数分工明确：
- `mask`/`anchors` 负责锚框分配与匹配；
- `classes` 定义检测类别范围；
- `jitter`/`random` 提升训练泛化能力；
- `ignore_thresh`/`truth_thresh` 优化训练损失计算。


---



**route层**

```cpp
[route]
layers = -1, 61   // 负数表示相对索引, 0和正数表示绝对索引
```

route层的主要作用是实现不同层级特征的融合或特定层特征的复用。

layers 用于指定当前route层的输入来源：
- -1表示相对索引: 表示当前route层的上一层；
- 61表示绝对索引: 表示网络中第 61 层（层索引从 0 开始计数）。



---

**upsample层**

```cpp
[upsample]
stride=2
```

stride=2 意味着将输入特征图的尺寸将输入特征图的尺寸放大到原来的2倍（宽和高各扩大 2 倍）。比如输入特征图的尺寸是 13x13，经过该层之后，输出特征图的尺寸会变成 26x26。




## 代码分析-算子硬件加速

前面对YOLOv3的网络结构已经有比较深入的理解了，该章节主要探究如何调用GPU资源、CUDA接口、以及CPU资源，如何调用，何时调用，哪个位置需要调用。

src/cuda.c

```cpp
#ifdef GPU
...

#ifdef CUDNN      // 神经网络专用显卡接口
#endif // CUDNN
...
#endif // GPU
```



## 代码分析-各个版本

YOLOv3（2018）：Darknet 框架，多尺度检测 + 残差连接，奠定现代 YOLO 基础； YOLOv5（2020）：Ultralytics 开发，PyTorch 框架（易部署），首次引入 “系列化模型”（n/s/m/l/x）； YOLOv8（2023）：Ultralytics 新一代，统一检测 / 分割 / 姿态任务，模块化设计 + 自动训练； YOLOv10（2024）：Ultralytics 最新，极致轻量化 + 速度，适配边缘设备。

**YOLOv5核心优化**：**“工程化标杆”，易部署 + 系列化**

1. **框架迁移**：从 Darknet 迁移到 PyTorch，支持动态图、自动混合精度训练（AMP），开发和部署效率大幅提升（YOLOv3 需手动编译 Darknet，门槛高）；
2. **系列化模型设计**：首次推出 n（ nano）、s（small）、m（medium）、l（large）、x（extra large）系列，按需选择 “速度 - 精度” 平衡点（如 YOLOv5n 适合边缘设备，YOLOv5x 追求高精度）；
3. 数据增强升级： • 自适应锚框计算（自动根据数据集调整锚框尺寸，无需手动配置）； • 混合增强（MixUp）、自适应图片缩放（减少黑边填充，提升计算效率）；
4. 推理优化： • Focus 模块（将 640×640 图片拆分为 320×320×4 特征图，减少计算量同时保留细节）； • 导出支持 ONNX、TensorRT、CoreML 等格式，适配 GPU/CPU/ 边缘设备（如 Jetson Nano）；
5. 对比YOLOv3：训练速度提升 2-3 倍，部署成本大幅降低，小目标检测精度提升明显（得益于更好的特征融合）。

**YOLOv8核心优化**：**“全能选手”，统一多任务 + 模块化**

1. **统一任务框架**：支持检测、分割、姿态估计、实例分割等多任务，一套代码适配多种需求（YOLOv3 仅支持检测）；
2. **模块化设计**：将网络拆分为 Backbone（主干）、Neck（特征融合）、Head（检测头）、Loss（损失函数），支持自定义替换（如替换 Backbone 为 ResNet）；
3. 训练自动化： • 自动学习率调整、自动数据增强、自动模型剪枝； • 支持迁移学习（预训练模型覆盖更多场景，如红外检测、小目标检测）；
4. **部署更灵活**：支持 TensorRT、ONNX、OpenVINO、TensorFlow Lite 等几乎所有主流部署框架，适配 GPU/CPU/ARM 设备。
5. 对比YOLOv3：功能全面升级，训练效率提升 5 倍，部署成本降低 80%，是目前最主流的工业级 YOLO 版本。

**YOLOv10核心优化**：**“轻量化巅峰”，极致速度 + 低资源占用**

1. 轻量化设计： • 提出 P2E 模块（高效特征提取，减少参数量和计算量）； • 简化 Neck 层结构，去除冗余分支；
2. 速度突破：YOLOv10-N 在 CPU 上可达 100+ FPS，GPU 上可达 1000+ FPS（640×640 输入），比 YOLOv5-N 快 50%+；
3. 精度保持：在极致轻量化的同时，mAP 仅比 YOLOv5-N 低 1-2%，实现 “速度 - 精度” 的最优平衡；
4. 边缘设备适配：显存占用低至几十 MB，适配手机、单片机等资源受限设备。
5. 对比YOLOv3：速度提升 10 倍 +，资源占用降低 90%，适合边缘计算、实时嵌入式场景（如无人机、可穿戴设备）。

**四、实际选型建议（对应优化方向）**

- 若需要 **快速部署、工业落地**：选 YOLOv8（全能）或 YOLOv6（工业专用）；
- 若需要 **边缘设备 / 低资源场景**：选 YOLOv10-N 或 YOLOv5-N；
- 若需要 **极高精度（如医疗 / 科研）**：选 YOLOv9 或 YOLOv7；
- 若需要 **多任务（检测 + 分割 + 姿态）**：选 YOLOv8 或 YOLOv9；







# YOLOv11电脑部署

B站：林亿饼：YOLO计算原理
【YOLO环境配置】: https://www.bilibili.com/video/BV182bZzMEYD


## 电脑硬件环境

![[Pasted image 20251222094500.png]]

1、查看自己电脑硬件环境，最好是有英伟达显卡，如果没有，也能用CPU来跑AI。
![[Pasted image 20251222094519.png]]


2、查看内存，如果内存小于8GB，那么你连工具软件都会很卡顿，就别提后面跑模型了。
![[Pasted image 20251222094546.png]]


3、以上一切就绪，那就开始操作了，配置YOLO环境整体需要安装这4样东西，确保每个步骤成功后，再进行下一步。
![[Pasted image 20251222094603.png]]


## 下载yolo源代码和模型

为了方便环境统一，我们都使用统一的版本，进入网页，把zip包下载下来，然后解压到某固定目录，方便后续使用。

https://github.com/ultralytics/ultralytics/tree/v8.3.163


接下来还需要下载预训练模型，我们把 yolo11n系列(nano)的模型文件都下载下来放到 ultralytics-8.3.163 目录里备用。

https://github.com/ultralytics/assets/releases

![[Pasted image 20251222094712.png]]



## 安装Anaconda

1、bing搜索: tuna anaconda，可以找到清华的镜像网站，进入后，找到安装包下载链接点进去，然后搜索 2024.06-1 这个版本，找到带 Windows 字样的安装包下载下来，双击安装，用户Just Me，路径不能有空格和中文名。

https://mirrors.tuna.tsinghua.edu.cn/help/anaconda/

![[Pasted image 20251222094750.png]]


2、设置 anaconda 和 pip 国内镜像，同样是刚才的清华镜像站。根据镜像站的提示，新建配置文件 C:\Users\你的用户名\.condarc。

3、bing搜索: tuna pip，可以找到 pip 清华镜像站，然后在 anaconda prompt 命令行终端执行网站说明的相关命令进行设置。


## 安装显卡驱动


打开 anaconda prompt，输入 nvidia-smi 回车运行，正常情况下会打印一个表格: 如果版本号大于等于11.8，那么就可以直接后续安装PyTorch，如果版本号不满足，则需要安装显卡驱动。
![[Pasted image 20251222094827.png]]


1、bing搜索: 英伟达显卡驱动，根据自身显卡型号下载对应系列的驱动即可。
![[Pasted image 20251222094902.png]]


2、下载好后，直接双击安装，全程默认下一步，安装完之后重启电脑。
![[Pasted image 20251222094932.png]]


3、电脑重启完成后，重新打开 anaconda prompt，再次执行 nvidia-smi 看看版本号。版本号大于11.8了，就确认驱动没问题了。我们就可以安装 PyTorch 了。


## 安装YOLO环境

<font color=blue>Anaconda 是个什么软件，有什么作用？ </font>
Anaconda 就类似于环境容器，为每个环境做好隔离管理。
![[Pasted image 20251222095022.png]]

1、先打开 anaconda prompt 命令行窗口，执行如下命令:
```python
# 列出当前所有环境
conda env list

# 新建环境
conda create -n YOLOv11Env python=3.11

# 进入到指定环境
conda activate YOLOv11Env

# 退出环境
conda deactivate
```


2、接下来要安装 PyTorch，为了让 PyTorch 调用你的显卡，你得综合考虑你显卡的型号、显卡驱动的版本、Python的版本、其他包的版本、甚至源代码的版本。
![[Pasted image 20251222095058.png]]


浏览器直接进入 PyTorch 官网，cuda选择12.8，选好后，复制下面的命令，然后打开 conda prompt 并进入yolo环境，粘贴并运行刚刚复制的命令。
![[Pasted image 20251222095122.png]]


在前面小节安装好显卡驱动后，就可以根据我们的实际电脑情况安装 PyTorch 了：
![[Pasted image 20251222095140.png]]


选择好对应配型后，复制下面的命令，然后打开 anaconda prompt，首先进入yolo环境，然后才执行上述安装命令。


安装完成之后，在 prompt 检验一下:
```python
(YOLOv11Env) C:\\Users\\seafly>pip show torch
Name: torch
Version: 2.9.1+cu130     <------代表你安装的是GPU版本的PyTorch(cuda),否则就是CPU版
Summary: Tensors and Dynamic neural networks in Python with strong GPU acceleration
Home-page: <https://pytorch.org>
Author:
Author-email: PyTorch Team <packages@pytorch.org>
License: BSD-3-Clause
Location: E:\\SW\\AI\\anaconda3\\envs\\YOLOv11Env\\Lib\\site-packages
Requires: filelock, fsspec, jinja2, networkx, sympy, typing-extensions
Required-by: torchvision

(YOLOv11Env) C:\\Users\\seafly> python
Python 3.11.14 | packaged by Anaconda, Inc...
>>> import torch
>>> import torchvision
>>> torch.cuda.is_available()
True
>>> torch.randn(1).cuda()
tensor([1.2018], device='cuda:0')
>>>

>>> import torch
>>> torch.cuda.is_available()
True
>>> torch.cuda.device_count()
1
>>> torch.cuda.current_device()
0
>>> torch.cuda.device(0)
<torch.cuda.device at 0x7efce0b03be0>

>>> torch.cuda.get_device_name(0)
'GeForce GTX 950M'
```


## 安装其他依赖包

1、打开 conda prompt，切换到yolo环境，然后…
```python
# 切换环境
conda activate YOLOv11Env

# 进入到源码目录
pushd  E:\\project\\ai\\yolov11\\ultralytics-8.3.163

# 安装其他依赖
pip install -e .
```


2、安装完成后，我们可以马上试试yolo效果:
```python
# 查看版本号
yolo version

# 运行官方示例,用 yolo11n.pt 模型来预测源码目录里的 ultralytics/assets/ 里的2张图片
yolo detect predict
```


## 开发环境-安装PyCharm
1、官网下载安装 PyCharm，安装社区版足够用了。
![[Pasted image 20251222095326.png]]



2、打开刚刚解压的yolo源码，ultralytics-8.3.225，设置编译环境:
![[Pasted image 20251222095346.png]]


3、新建并编辑例程文件，然后运行体验一下效果:
![[Pasted image 20251222095422.png]]


4、提供的例程文件:
```python
# mypredict.py
from ultralytics import YOLO

model = YOLO(r"../yolo11n.pt")

model.predict(
    source=r"ultralytics/assets",
    save=True,
    show=False,
)
```


```python
# mycam.py
from ultralytics import YOLO
import cv2

model = YOLO(r"../yolo11n.pt")

results = model(
    source=0,
    stream=True,
)

for result in results:
    plotted = result.plot()
    cv2.imshow("YOLO Inference", plotted)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
```


## 推理入门

1、推理就是预测，预测就是推理，说的都是同一件事。而训练其实就是你实现准备好一大堆图片和人工标注的正确答案，把它们一起喂给模型，喂一次模型就会更新一次参数，随着你喂的次数越来越多，模型预测的结果就会越来越准确。总结一下，推理就是使用模型，训练就是获取模型。

2、不夸张的说，学习AI其实就是在学习如何解决推理和训练过程中遇到的各种问题。

预测一张图片 = 预处理 + 推理 + 后处理

![[Pasted image 20251222095512.png]]


1、看看模型属性：

```python
from ultralytics import YOLO

#加载模型文件
model = YOLO(r"../yolo11n.pt")

#比如打印出 detect, 表示 yolo11n.pt 这个模型的任务是目标检测
print(model.task)

#打印出预测支持的所有类型，也就是分类名称列表
print(model.names)

#打印出该模型一共有多少个参数
print(sum(p.numel() for p in model.parameters()))
```


![[Pasted image 20251222095535.png]]


预测选项，即预测参数
https://docs.ultralytics.com/modes/predict/#inference-arguments


1、下面是常用的推理参数:
```python
# mypredict.py
from ultralytics import YOLO

model = YOLO(r"../yolo11n.pt")

model.predict(
    source=r"ultralytics/assets",
    save=True,   # 通常save和show互斥设置
    show=False,
    # line_width=5,表示绘制线粗细为5个像素点
    # visualize = True,可视化特征图,就是把推理过程的特征图保存成图片
    # 其他参数可以自行摸索
)
```



## 训练入门-最简单的YOLO训练


1、先找个简单的数据集、简单的模型跑通一下训练，可以提前排除掉很多可能出现的报错。也就是说，先把阶段定格在一个基本可用的训练上。

2、先来排除掉一个可能的报错，打开我的电脑，地址栏里输入 %appdata% 回车，找到 Ultralytics 文件夹，删掉里面的 settings.json 文件。目的是确保后续自动下载的数据集可以保存到正确的位置。

3、用 PyCharm 打开yolo源码项目，并确保已经配置好了环境。新建一个源文件 [[mytrain.py]] 文件：
```python
from ultralytics import YOLO

if __name__ == "__main__":
    model = YOLO(r"../yolo11n.pt")
    model.train(
        data = r"coco8.yaml",  # 表示我们打算训练 coco8.yaml 这个数据集
        epochs = 10,           # 训练个10轮
        imgsz = 640,
        batch = 2,
        cache = False,
        workers = 0
    )
```

4、然后运行，程序会自动下载 coco8.zip 压缩包，并自动解压，如果本地对应位置有压缩包，就会直接进行解压以及后续的工作。如果相关资源文件下载失败之类的，那就手动下载相关链接的文件，然后放到指定位置。
![[Pasted image 20251222095645.png]]

![[Pasted image 20251222095655.png]]


5、训练完之后的权重文件会保存到如下目录:

```python
...\\ultralytics-8.3.225\\runs\\detect\\train\\weights\\best.pt
...\\ultralytics-8.3.225\\runs\\detect\\train\\weights\\last.pt
```


## 训练入门-什么是数据集

1、需要准备YOLO格式的数据集，以及你应该怎么给yolo提供数据集。
![[Pasted image 20251222095729.png]]


![[Pasted image 20251222095743.png]]


![[Pasted image 20251222095756.png]]


![[Pasted image 20251222095809.png]]


## 训练入门-安装labelimg

1、labelimg可以制作数据集，同时也可以用来可视化数据集。

2、安装 labelimg，直接在 Anaconda 中安装且不能与yolo在同一个环境，因为它对Python版本依赖比较紧密，因此我们需要借助 Anaconda 给它单独开个环境。

```python
conda create -n labelimg python=3.8

#查看环境列表
conda env list

#进入指定环境
conda activate labelimg

#进入环境后,我们在该环境里就可以安装labeimg了
pip install labelimg

#pip安装失败就用下面conda安装
conda install conda-forge::labelimg

#安装好后,打开labelimg试试
labelimg
```

---

1、首先创建 classes.txt 文本文件，并且和labels里文本文件放在一起，然后把 coco8.yaml 里的 names 列表拷贝到文本文件里，删除前空白和数字冒号，最终 classes.txt 文件内容如下:
![[Pasted image 20251222095902.png]]


2、启用 labelimg 可视化数据:
```python
#进入指定环境
conda activate labelimg

#labelimg <图片路径> <classes.txt文件> <标签路径>
labelimg
		D:\\SW\\AI\\yolov8\\ultralytics-8.3.225\\datasets\\coco8\\images\\train
		D:\\SW\\AI\\yolov8\\ultralytics-8.3.225\\datasets\\coco8\\labels\\train\\classes.txt
		D:\\SW\\AI\\yolov8\\ultralytics-8.3.225\\datasets\\coco8\\labels\\train
```


![[Pasted image 20251222095931.png]]


3、快捷键，按一下a可以快速切换到上一张图片，按d是下一张图片。

4、我们就可以查看和修改数据集了，同理，我们也可以看看 coco8 的验证集标注，只要在同一个集里，classes.txt 文件内容都相同，所以我们直接复制粘贴前面的 classes.txt 文件即可，且你要查看验证集val的标注，那么classes.txt文件就要拷贝到它目录下的labels目录下，和图片标注文本文件在同一个目录下。


## 训练入门-逛逛现成数据集

1、带你用 labelimg 可视化一些别人做好的数据集。

ultralytics-8.3.225\ultralytics\cfg\datasets

2、在上面路径下，里面的 .yaml 文件每个配置文件都对应着具体的数据集。比如 coco8.yaml 文件对应着一共8张图片，coco128.yaml 对应着一共128张图片。目录里还提供了其他数据集，比如 medical-pills.yaml，african-wildlife.yaml 等等。我们可以通过运行训练 demo 的方式把数据集下载下来。


## 训练入门-如何让训练跑更快

1、教你一些提高训练效率的技巧。下面这种就是让电脑全速训练的状态了。
![[Pasted image 20251222100019.png]]

```python
from ultralytics import YOLO

if __name__ == "__main__":
    model = YOLO(r"../yolo11n.pt")
    model.train(
        data = r"african-wildlife.yaml",
        epochs = 10,    #表示训练多少轮,这里表示训练10轮
        imgsz = 640,    #设置图片尺寸,比如这里是640x640
        batch = 2,      #表示一次喂2张图片,-1表示让模型自动帮你适配合适大小
        cache = False,  #cache="ram",事先缓存训练集的图片
        workers = 0,    #数据打包的线程数
        val = True,     #在训练中是默认打开的
        device = "cpu",
    )
```

imgsz: 比如下图这种，图片又大，目标又是一丁点，这种就尽量别压缩图片尺寸了，再压缩就看不见目标了，这种情况就建议 imgsz 尽量设置大点。那如果你面对的数据集是图片尺寸很小，目标也很小的情况，那怎么办，那说明你目前的数据集是一坨屎，换一个吧，错的又不总是你。
![[Pasted image 20251222100052.png]]


batch: 假如待训练的图片很多，有成千上万，全部打包投喂给模型，就会占用显存大量的空间，而更新参数这个步骤，本身又会产生一大堆的数据，所以显存一下子可能就不够用了。优秀的cook这时候就会想，既然一次性全部丢进去不行，那为什么不分批次丢进去呢。现实中就是这么做的，比如一共12张图片，那就先拿4张，进行缩放等处理，然后打包投喂；再拿4张继续，以此类推。所有投喂都完成了，就算完成了一轮。拼到一起喂给模型的图片，就叫一个批次，一个批次里图片的数量就叫做批量(batch size)。每一轮训练，实际上就是在给模型喂一个又一个批次，喂一个批次，模型更新一次参数，比如上面 batch=2 就表示一个批次里2张图片，完成一个批次的投喂。


![[Pasted image 20251222100117.png]]

![[Pasted image 20251222100130.png]]


可以通过 batch=-1，让YOLO自动帮你找一个相对合适的 batch 值，先训练一轮，就能看到日志中YOLO给你提供的合适batch大小，这样你后续就可以直接把这个推荐大小设置到batch参数里。
![[Pasted image 20251222100146.png]]


cache=”ram”，所有训练的图片，都是以文件的形式存放在你硬盘里。当yolo决定好一个批次要用哪些图片后，它就会把这些图片从硬盘加载到内存里，缩放一下，打包一下，再转移到显存里喂给模型。这时候就有个问题，就是每个批次都要从硬盘加载图片，加载这个操作是很费时间的，假如上个批次已经把参数更新好了，下个批次的图片却还在龟速加载中，那你的模型在新批次到来之前，就只能干等着什么都干不了。

![[Pasted image 20251222100507.png]]

![[Pasted image 20251222100521.png]]


缓存的核心思想就是，如果一个东西你经常要用，那你就把它放的近一点。对于模型而言，图片放在内存里，是不是比放在硬盘里要更近点，<font color=green>cache=”ram” 大概率可以提高训练的效率，唯一的缺点就是所有缩放后的图片都会放到内存里，所以内存要足够大才能容纳这些图片</font>，数据集里的图片越多，那么就对内存容量的要求就越高。
![[Pasted image 20251222100623.png]]


workers=1，每次打包的图片，都是随机的，这样做的目的是为了增强模型的泛化能力。比如某个批次要打包猫这张猫的图片，模型会给它随机放大或缩小一些，接着给它随机旋转一个角度，再给它调一调颜色，再给它从中间裁剪一下，像这种对图片的随机变化操作，就叫做数据增强。增强后的图片，还是预设的 640x640 尺寸，接着就可以把它们拼到一起，获取一个整齐的数据块，然后数据块喂给模型，喂好后，就完成了一个批次的训练。

总结就是，打包是随机的，我们没法提前预测打包，而打包本身也有一堆操作，如果打包慢了跟不上投喂，同样会让模型干等着。解决这个问题的思路是，多开几个进程来打包，打个比方，就是你一个人打包忙不过来，那就多雇几个人来打包，
![[Pasted image 20251222100640.png]]


如果你对速度还不满意，我也给你提供一个邪修路线：
![[Pasted image 20251222100656.png]]



## 训练入门-自定义数据集

本小节清单：

- 1、有没有现成的数据集；
- 2、怎么获取图片；
- 3、怎么获取标签；
- 4、怎么划分数据集；
- 5、怎么训练自己的模型；
- 6、训练好了，然后呢？


1、现成的数据集:

google搜索: roboflow universe，最终得到如下网站: https://universe.roboflow.com/

![[Pasted image 20251222100912.png]]


2、怎么获取图片，视频转图片：

<font color=blue>我需要一些python代码，有一些mp4视频文件存放在这里: d:\ai\make_dataset\vidieos，帮我每隔固定几帧提取一张图片出来，一秒提取几帧作为一个可以调整的参数，图片统一命名为 aaa_xxxxx.jpg 格式，aaa代表视频的名字，xxxxx表示图片的序号，比如视频 001.mp4 生成的图片就是 001_00001.jpg、001_00002.jpg, … 处理每个视频的时候给我进度条，所有图片统一保存到这个文件夹: d:\ai\make_dataset\images，注释写清楚一点，我是python小白。</font>

3、怎么获取标签：定义分类标签，创建标签目录，新建 classes.txt 文件，把我们要训练的新标签写进去，尽量英文。然后按照之前的操作，使用 labelimg 打开标签，操作是一样的。

![[Pasted image 20251222101018.png]]


4、开始锚定图片中的目标，最后保存，即可生成图片对应的标签坐标文件。

![[Pasted image 20251222101223.png]]

![[Pasted image 20251222101233.png]]


5、半自动标注，就是用小部分的图片，先训练出一个学渣模型，然后我们拿学渣模型来预测剩下的未标注过的图片，把预测结果保存成YOLO格式的标签，这些标签就叫做伪标签，我们只需要花点时间手动调一下这些伪标签就行，这就是半自动标注了。

![[Pasted image 20251222101247.png]]

![[Pasted image 20251222101255.png]]


6、先用少量图片做出训练集和验证集，然后训练出学渣模型。之后拷贝并修改之前的预测代码，把模型替换一下，把图片目录替换一下，把预测结果保存到文本文件:

```python
#使用学渣模型来预测未标注的图片
model = YOLO(r"D:\\SW\\AI\\yolov8\\ultralytics-8.3.225\\runs\\detect\\train1\\weights\\best.pt")

model.predict(
		#替换成未标注的图片路径
    source=r"D:\\deeplearning\\make_dataset\\images",
    save=True,
    show=False,
    
    #保存成YOLO格式的预测结果(标注文件)
    save_txt=True,     
)
```

![[Pasted image 20251222105201.png]]

7、最后，图片和标签都准备好了。最后一步就是把它们按照比例随机划分到训练集和验证集目录了，剩下的你可以借助 AI 帮你编写 python 的划分代码了。 

<font color=blue>我现在需要一些 python 代码随机划分一下数据集，images 文件夹里存放着所有.jpg图片文件，labels里存放了所有 .txt 标签文件（YOLO格式），比如 images\001.jpg 对应着 labels\001.txt，划分结果统一保存到 kunkun 文件夹里，用这样的目录结构: kunkun\ images\ train\ val\ test\ labels\ train\ val\ test\ 划分比例设置成可调整的参数，只复制粘贴文件，不要动原本的图片和标签，不要用 sklearn 这个包，划分的时候用进度条提示一下进度，注释写清楚一点，我是python小白。</font>

8、划分好之后，就可以拿着这套数据集，训练自己的模型了。

```python
from ultralytics import YOLO

if __name__ == "__main__":
    model = YOLO(r"../yolo11n.pt")
    model.train(
        data = r"african-wildlife.yaml",
        epochs = 100,
        imgsz = 640,
        batch = 16,     
        cache = "ram",
        workers = 1,
        val = True,     #在训练中是默认打开的
        project = "results",
        name = "mymodel",
    )
```



## 深入验证-初步理解


1、我们玩yolo的终极目标就是，训练出一个又快又准的模型，本期我们重点关注什么是准。还记得前面几期反复提到的 “验证” 这个词吗？验证，就是在给模型的准度打分。学会验证的基本方法，本节将告诉你验证的时候到底在干什么, 以及训练过程中的一堆数字, 训练结束后的一堆曲线都是什么意思, 为你以后评价模型、挑选模型、改进模型提供最核心的依据。废话不多说，我们冲！

![[Pasted image 20251222105313.png]]


2、但相似度这个描述还是模糊了点，需要一个具体的分数值来描述:

![[Pasted image 20251222105325.png]]


## 深入验证-预测对错

1、目标检测领域，通常使用一个叫 IoU 的算法来评价两个框的接近程度。
- (1) 预测结果和真实结果有一点偏离该怎么分?
- (2) 多预测了几个, 怎么打分?
- (3) 漏预测了, 怎么打分?

![[Pasted image 20251222105353.png]]


2、IoU 阈值，能影响预测结果, 通常 IoU 阈值为 0.5, 表示大于等于0.5的算正确预测, 小于0.5的算错误预测.


## 深入验证-统计TPFPFN

三、统计工作TP、FP、FN

1、TP 就是 True Positive, 即正确的预测结果, 而 FP 就是 False Positive, 即可错误的预测结果.

![[Pasted image 20251222105431.png]]



## 深入验证-计算PRF1

TP,FP,FN还会出现特殊情况, 这种情况怎么办? 回答问题的思路是: 一个真实的结果只能被找到一次, 一个预测结果只能找到一个目标. 所以,你应该知道下面这种情况不是什么好事了.

![[Pasted image 20251222105457.png]]


为了解决上述问题, 于是进一步计算出了P,R,F1, 为了方便理解, P可以理解成predict, R可以理解为Real.
![[Pasted image 20251222105516.png]]



## 深入验证-预测过程(后处理)

![[Pasted image 20251222105531.png]]

![[Pasted image 20251222105543.png]]

```python
from ultralytics import YOLO

model = YOLO(r"../yolo11n.pt")

model.predict(
    source=r"ultralytics/assets",
    save=True,
    show=False,
    
    #通过修改下面的3个参数来探究对预测框个数的影响
    conf=0.25,
    iou=0.7,
    max_det=300,
)
```





# YOLO应用扩展


## 其他检测

模型链接: [[yolo-face]]

```cpp
// 人脸识别
yolo task=detect mode=predict model=yolov8n-face.pt conf=0.25 \\
		imgsz=1280 line_thickness=1 max_det=1000 source=examples/face.jpg

// 人物识别,判断画面中是否有人物
yolo task=detect mode=predict model=yolov8n-face.pt conf=0.25 \\
		imgsz=1280 line_thickness=1 max_det=1000 source=examples/person.jpg
		
// 足球球员运动员识别
yolo task=detect mode=predict model=yolov8m-football.pt conf=0.25 \\
		imgsz=1280 line_thickness=1 source=examples/football.jpg
		
// 停车场车位识别(识别车位是否被占用)
yolo task=detect mode=predict model=yolov8m-parking.pt conf=0.25 \\
		imgsz=1280 line_thickness=1 source=examples/parking.jpg
		
// 高空无人机识别
yolo task=detect mode=predict model=yolov8m-drone.pt conf=0.25 \\
		imgsz=1280 line_thickness=1 source=examples/drone.jpg
```

1、YOLO官方支持的基本检测类型：

- Oriented Object Detection: 旋转目标检测
- Pose Estimation: 姿态估计(骨架姿态)
- Instance Segmentation: 实例分隔(轮廓掩码)
- Image Classification: 图像分类(单目标分类)

---

**Ultralytics YOLOv8+ 系列中的 “Solutions API”:**

```cpp
yolo solutions help     // 查看方案清单
blur      ---> 检测后对目标区域打马赛克（隐私保护，人脸、车牌等）
workout   ---> 结合pose分析运动动作，比如俯卧撑/深蹲计数
heatmap   ---> 目标移动热力图，比如商场客流热点分析，视频监控统计等
isegment  ---> 实时实例分割，精准分割人、物体的轮廓区域
visioneye ---> 监控型检测(摄像头检测+报警)，比如安防监控、异常检测
speed     ---> 检测运动目标速度，比如车辆测速、人流移动速度分析
queue     ---> 检测并统计排队人数
inference ---> 普通推理任务，基础目标检测
trackzone ---> 区域追踪+计数，比如进出区域统计、人流量分析等

// 示例CLI: 目标检测 + 计数
yolo solutions count model=yolov8n.pt source="video.mp4"

// 示例CLI: 区域追踪（进出计数）
yolo solutions trackzone model=yolov8n.pt source="video.mp4"

// 示例CLI: 姿态动作分析（workout）
yolo solutions workout model=yolov8n-pose.pt source="gym.mp4"

// 示例CLI: 车辆速度检测
yolo solutions speed model=yolov8n.pt source="traffic.mp4"

// 示例CLI: 隐私保护（模糊化）检测后自动打码，比如人脸模糊
yolo solutions blur model=yolov8n.pt source="street.mp4"

// 示例CLI: 监控报警（VisionEye）
yolo solutions visioneye model=yolov8n.pt source=0
```

几乎所有 solution 都支持以下通用参数：

```cpp
model=                // 指定模型文件
source=               // 图片文件、视频文件、或摄像头索引(0)
show=True             // 是否实时显示窗口
save=True             // 是否保存输出结果
conf=0.5              // 检测置信度阈值
device=0              // 指定GPU或CPU
```

每个检测结果输出项:

- obb输出: (x_center, y_center, width, height, angle, confidence, class)
    - x_center,y_center: 旋转框中心点坐标
    - width,height: 框的宽和高
    - angle: 框的旋转角度(单位: 弧度或角度)
    - confidence: 置信度
    - class: 目标类别
    - oob应用举例: 比如判断目标物体是否倒伏了、是否对齐等等。
- pose输出: (x,y,w,h), confidence, class, keypoints
    - (x,y,w,h): 检测框的位置
    - confidence: 置信度(检测到人体/物体的概率)
    - class: 类别，比如 person
    - keypoints: 每个关键点的(x,y,score)，其中score表示该关键点被识别出的置信度
    - 应用场景: 人体动作识别、行为分析；舞蹈运动教学；手势识别动作控制；模拟人类动作、姿态控制；虚拟现实实时人体跟踪等等。
- segment输出: (x,y,w,h), confidence, class, mask
    - (x,y,w,h): 检测框的位置
    - confidence: 置信度(检测到人体/物体的概率)
    - class: 类别，比如 person
    - mask: 分割掩码(每个像素属于该目标的概率)
    - 应用方向:
        - 自动驾驶车道线、车辆、行人、路牌分割，提供像素级边界用于路径规划；
        - 零件缺陷、边缘分割，识别瑕疵、裂纹、划痕；
        - 肿瘤、器官、病灶分割，计算病变区域面积体积；
        - 植株分割，果实计数，用于自动化采摘和长势分析；
        - 用于抠图、背景替换、虚拟试衣等；
        - 建筑物、道路、水体提取，用于卫星图像中分割地物；
    - 预训练模型: [[yolov8n-seg.pt]]
- tracking输出:
    - 为Tracking: 检测结果分配唯一ID，实现连续帧跟踪；
    - Counting: 统计画面中出现的目标数量；
    - ReID重识别: 基于外观特征识别目标身份；

## 嵌入式平台

YOLOv8目标检测在RK3588部署全过程: [[140062461]]

轻量级C实现路线（嵌入式可用）

|框架|语言|特点|是否支持ONNX|适合C移植？|
|---|---|---|---|---|
|**ncnn**|C++（带C接口）|腾讯开源，极轻量、支持ARM/嵌入式|✅ 直接加载 .onnx|✅ 非常适合移植|
|**MNN**|C++/C|阿里巴巴出品，跨平台、性能优|✅|✅|
|**Tengine**|C|专为嵌入式设计，结构最简单|✅|✅ 强烈推荐|
|**ONNX Runtime C API**|C|官方出品，功能最全，但体积较大|||

## 笔记本摄像头

1、在笔记本Windows 10 上，通过实时捕获摄像头把画面输入到yolo，并把输出视频流显示到屏幕上。

2、先安装 OpenCV 环境:

```cpp
pip install ultralytics opencv-python
```

3、最小可运行示例 Python 代码:

```python
from ultralytics import YOLO
import cv2

# 1.加载模型（你可以换成 yolov8n.pt、yolov11n.pt 等）
model = YOLO("yolo11n.pt")

# 2.打开摄像头（0 表示默认摄像头）
cap = cv2.VideoCapture(0)

# 检查是否打开成功
if not cap.isOpened():
    print("无法打开摄像头")
    exit()

# 3.循环读取帧并检测
while True:
    ret, frame = cap.read()
    if not ret:
        print("无法读取视频帧")
        break

    # YOLO 推理（可加参数 stream=True 提升帧率）
    results = model(frame, verbose=False)

    # 获取带检测框的图像
    annotated_frame = results[0].plot()

    # 显示结果
    cv2.imshow("YOLO 摄像头检测", annotated_frame)

    # 按下 q 退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 4.清理资源
cap.release()
cv2.destroyAllWindows()
```

---

方式二、嵌入网页显示（Flask + OpenCV）

1、如果想在浏览器实时查看，需要安装flask:

```python
pip install flask
```

2、然后 Python 例程:

```python
from ultralytics import YOLO
import cv2
from flask import Flask, Response

app = Flask(__name__)
model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(0)

def generate():
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        results = model(frame)
        annotated = results[0].plot()
        _, buffer = cv2.imencode('.jpg', annotated)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\\r\\n'
               b'Content-Type: image/jpeg\\r\\n\\r\\n' + frame_bytes + b'\\r\\n')

@app.route('/video')
def video_feed():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

3、运行后，在浏览器中打开: http://localhost:8080/video
即可看到YOLO 实时检测的摄像头视频流。model(frame, stream=True) 模式下使用(stream=True)，可以降低延迟。



# Bottom

超轻量级嵌入式环境

在嵌入式设备上部署推理环境

其他类型任务








