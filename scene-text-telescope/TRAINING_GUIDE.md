# Scene Text Telescope 训练完整指南

## 目录

1. [环境准备](#环境准备)
2. [数据准备](#数据准备)
3. [配置文件说明](#配置文件说明)
4. [训练命令](#训练命令)
5. [训练监控](#训练监控)
6. [恢复训练](#恢复训练)
7. [常见问题](#常见问题)

## 环境准备

### 1. 安装依赖

```bash
cd scene-text-telescope
pip install -r requirement.txt
```

### 2. 检查 GPU/CPU 环境

**检查 GPU 是否可用**（推荐使用GPU，速度更快）：

```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU count:', torch.cuda.device_count())"
```

**如果没有 GPU**，代码会自动使用 CPU，但训练速度会非常慢。建议：
- 使用较小的批次大小（batch_size=1 或 2）
- 减少 workers 数量
- 仅用于测试或小规模训练

## 数据准备

### 1. 下载数据集和模型权重

从以下链接下载所有必需资源：
- [BaiduYunDisk](https://pan.baidu.com/s/1P_SCcQG74fiQfTnfidpHEw) (密码: stt6)
- [Dropbox](https://www.dropbox.com/sh/f294n405ngbnujn/AABUO6rv_5H5MvIvCblcf-aKa?dl=0)

### 2. 组织数据目录结构

将下载的资源按照以下结构组织：

```
scene-text-telescope/
├── dataset/
│   └── mydata/
│       ├── train1/              # 训练数据集1 (LMDB格式)
│       ├── train2/              # 训练数据集2 (LMDB格式)
│       ├── test/                 # 测试数据集
│       │   ├── easy/            # 简单难度测试集
│       │   ├── medium/          # 中等难度测试集
│       │   └── hard/            # 困难难度测试集
│       ├── crnn.pth             # CRNN 识别器预训练权重（必需）
│       └── pretrain_transformer.pth  # Transformer 预训练权重（必需，用于文本聚焦损失）
└── checkpoint/                   # 训练输出目录（自动创建）
    └── {exp_name}/              # 实验名称目录
        ├── model_best.pth       # 最佳模型
        ├── checkpoint.pth       # 定期保存的检查点
        ├── log.txt              # 训练日志
        └── events.out.tfevents  # TensorBoard 日志
```

### 3. 验证数据

检查数据是否正确放置：

```bash
# 检查训练数据
ls -lh dataset/mydata/train1/
ls -lh dataset/mydata/train2/

# 检查测试数据
ls -lh dataset/mydata/test/easy/
ls -lh dataset/mydata/test/medium/
ls -lh dataset/mydata/test/hard/

# 检查模型权重
ls -lh dataset/mydata/crnn.pth
ls -lh dataset/mydata/pretrain_transformer.pth
```

## 配置文件说明

训练配置在 `config/super_resolution.yaml` 中，主要参数：

```yaml
TRAIN:
  train_data_dir: ['./dataset/mydata/train1', './dataset/mydata/train2']  # 训练数据路径
  batch_size: 512              # 批次大小（可根据GPU内存调整）
  width: 128                    # 输出图像宽度
  height: 32                    # 输出图像高度
  epochs: 50000                 # 训练轮数
  cuda: True                    # 使用CUDA
  ngpu: 4                       # GPU数量（多GPU训练）
  workers: 8                    # 数据加载线程数
  lr: 0.0001                    # 学习率
  saveInterval: 200             # 保存检查点的间隔（迭代次数）
  displayInterval: 50          # 显示训练信息的间隔
  valInterval: 1000            # 验证间隔（迭代次数）
  
  VAL:
    val_data_dir: [             # 验证数据路径
      './dataset/mydata/test/easy',
      './dataset/mydata/test/medium',
      './dataset/mydata/test/hard',
    ]
    crnn_pretrained: './dataset/mydata/crnn.pth'  # CRNN权重路径
```

## 训练命令

### CPU 训练（无GPU）

如果没有GPU，代码会自动使用CPU，但需要调整参数：

#### 方式一：使用CPU训练脚本（推荐）

```bash
# 使用专门的CPU训练脚本
bash train_cpu_example.sh
```

#### 方式二：直接运行命令

```bash
# CPU训练 - 使用很小的批次大小
python main.py \
    --batch_size=1 \
    --STN \
    --exp_name my_training_cpu \
    --text_focus \
    --arch tbsrn
```

#### 方式三：使用CPU配置文件

```bash
# 修改 main.py 中的配置文件路径，或创建自定义脚本
# 使用 config/super_resolution_cpu.yaml 配置文件
```

**CPU训练注意事项**：
- 批次大小建议设为 1 或 2（避免内存不足）
- 训练速度会非常慢（比GPU慢50-100倍）
- 建议仅用于测试或小规模实验
- 可以修改配置文件 `config/super_resolution.yaml` 中的 `workers: 2` 减少线程数
- 确保系统有足够内存（建议16GB+）
- 代码会自动检测CUDA，如果没有GPU会自动使用CPU

### GPU 训练（推荐）

### 基础训练命令

```bash
CUDA_VISIBLE_DEVICES=0 python main.py \
    --batch_size=16 \
    --STN \
    --exp_name my_training \
    --text_focus \
    --arch tbsrn
```

### 完整参数说明

```bash
CUDA_VISIBLE_DEVICES=0 python main.py \
    --batch_size=16 \              # 批次大小（根据GPU内存调整）
    --STN \                        # 使用空间变换网络（Spatial Transformer Network）
    --exp_name my_training \       # 实验名称（必需，用于保存checkpoint）
    --text_focus \                 # 启用文本聚焦模式（推荐）
    --arch tbsrn \                 # 模型架构：tbsrn, tsrn, srcnn, vdsr, srres, esrgan, rdn, edsr, lapsrn
    --hd_u 32 \                    # 隐藏单元数（可选）
    --srb 5                        # SRB块数量（可选）
```

### 多GPU训练

```bash
# 使用多个GPU（例如：GPU 0, 1, 2, 3）
CUDA_VISIBLE_DEVICES=0,1,2,3 python main.py \
    --batch_size=64 \              # 多GPU时可以增大batch_size
    --STN \
    --exp_name multi_gpu_training \
    --text_focus \
    --arch tbsrn
```

### 不同模型架构训练

```bash
# TBSRN (推荐，文本聚焦效果最好)
CUDA_VISIBLE_DEVICES=0 python main.py \
    --batch_size=16 --STN --exp_name tbsrn_train --text_focus --arch tbsrn

# TSRN
CUDA_VISIBLE_DEVICES=0 python main.py \
    --batch_size=16 --STN --exp_name tsrn_train --text_focus --arch tsrn

# SRCNN
CUDA_VISIBLE_DEVICES=0 python main.py \
    --batch_size=16 --STN --exp_name srcnn_train --text_focus --arch srcnn
```

## 训练监控

### 1. 查看训练日志

训练日志保存在 `checkpoint/{exp_name}/log.txt`：

```bash
# 实时查看日志
tail -f checkpoint/my_training/log.txt

# 查看最近的训练信息
tail -n 100 checkpoint/my_training/log.txt
```

### 2. 使用 TensorBoard 可视化

```bash
# 启动 TensorBoard
tensorboard --logdir checkpoint/my_training

# 然后在浏览器中打开 http://localhost:6006
```

TensorBoard 会显示：
- 损失曲线（MSE loss, Attention loss, Recognition loss）
- 训练进度
- 其他训练指标

### 3. 训练输出示例

```
[2024-01-01 10:00:00] Epoch: [0][1/1000] total_loss 1.234 mse_loss 0.456 attention_loss 0.123 recognition_loss 0.655
[2024-01-01 10:00:05] Epoch: [0][2/1000] total_loss 1.189 mse_loss 0.432 attention_loss 0.115 recognition_loss 0.642
...
[2024-01-01 10:30:00] ======================================================
[2024-01-01 10:30:00] evaling easy
[2024-01-01 10:30:15] best_easy = 45.23%*
[2024-01-01 10:30:15] evaling medium
[2024-01-01 10:30:30] best_medium = 38.56%*
[2024-01-01 10:30:30] evaling hard
[2024-01-01 10:30:45] best_hard = 32.12%*
[2024-01-01 10:30:45] saving best model
```

## 恢复训练

### 从检查点恢复训练

如果训练中断，可以从保存的检查点恢复：

```bash
CUDA_VISIBLE_DEVICES=0 python main.py \
    --batch_size=16 \
    --STN \
    --exp_name my_training \
    --text_focus \
    --arch tbsrn \
    --resume checkpoint/my_training/checkpoint.pth  # 指定检查点路径
```

### 从最佳模型继续训练

```bash
CUDA_VISIBLE_DEVICES=0 python main.py \
    --batch_size=16 \
    --STN \
    --exp_name my_training \
    --text_focus \
    --arch tbsrn \
    --resume checkpoint/my_training/model_best.pth
```

## 训练后的模型使用

训练完成后，最佳模型保存在 `checkpoint/{exp_name}/model_best.pth`，可以用于：

### 1. 测试

```bash
CUDA_VISIBLE_DEVICES=0 python main.py \
    --batch_size=16 \
    --STN \
    --exp_name my_training \
    --text_focus \
    --resume checkpoint/my_training/model_best.pth \
    --test \
    --test_data_dir ./dataset/mydata/test
```

### 2. Demo 识别

```bash
CUDA_VISIBLE_DEVICES=0 python main.py \
    --batch_size=1 \
    --STN \
    --exp_name my_training \
    --text_focus \
    --resume checkpoint/my_training/model_best.pth \
    --demo \
    --demo_dir ./demo
```

## 常见问题

### 1. CUDA Out of Memory / CPU 内存不足

**问题**: `RuntimeError: CUDA out of memory` 或 CPU 内存不足

**解决方案**:
- 减小 `--batch_size`（GPU: 从 16 改为 8 或 4；CPU: 使用 1）
- 在配置文件中减小 `workers` 数量（CPU训练建议设为 2-4）
- 使用更小的模型架构
- CPU训练时确保有足够的系统内存（建议16GB+）

### 2. 找不到训练数据

**问题**: `cannot creat lmdb from ./dataset/mydata/train1`

**解决方案**:
- 检查数据路径是否正确
- 确保数据是 LMDB 格式
- 检查文件权限

### 3. 训练速度慢

**解决方案**:
- 增加 `workers` 数量（但不要超过 CPU 核心数）
- 使用多GPU训练
- 确保数据在SSD上，而不是机械硬盘

### 4. 损失不下降

**可能原因**:
- 学习率太大或太小（默认 0.0001）
- 批次大小不合适
- 数据质量问题

### 5. 验证准确率不提升

**建议**:
- 检查验证数据是否正确
- 增加训练轮数
- 尝试不同的模型架构
- 调整学习率

## 训练参数调优建议

### 批次大小 (batch_size)
- **CPU**: 1-2（避免内存不足）
- **单GPU (8GB)**: 4-8
- **单GPU (16GB+)**: 8-16
- **多GPU**: 16-64

### 学习率 (lr)
- **默认**: 0.0001
- **如果损失不下降**: 尝试 0.0005 或 0.00005
- **如果训练不稳定**: 减小学习率

### 模型架构选择
- **TBSRN**: 文本聚焦效果最好，推荐用于文本识别任务
- **TSRN**: 类似 TBSRN，但结构略有不同
- **其他架构**: 通用超分辨率，文本聚焦效果较差

## 训练时间估算

根据硬件配置，训练时间大致如下：

- **CPU (现代多核)**: 约 2-4 周（50000 epochs，非常慢，不推荐）
- **单GPU (RTX 3090)**: 约 2-3 天（50000 epochs）
- **4x GPU (RTX 3090)**: 约 12-18 小时
- **单GPU (GTX 1080)**: 约 5-7 天

实际时间取决于：
- 数据集大小
- 批次大小
- 模型架构复杂度
- GPU/CPU 性能

**强烈建议使用GPU训练**，CPU训练速度太慢，仅适合小规模测试。

## 检查训练结果

训练完成后，检查以下文件：

```bash
# 检查最佳模型
ls -lh checkpoint/my_training/model_best.pth

# 查看训练日志
cat checkpoint/my_training/log.txt | tail -n 50

# 查看保存的模型信息
python -c "import torch; ckpt = torch.load('checkpoint/my_training/model_best.pth'); print(ckpt.keys())"
```

## 下一步

训练完成后，可以：
1. 使用训练好的模型进行测试（见 `EXAMPLE_USAGE.md`）
2. 使用模型进行图片识别（见 `QUICKSTART.md`）
3. 分析训练日志和 TensorBoard 结果
4. 根据结果调整超参数重新训练

