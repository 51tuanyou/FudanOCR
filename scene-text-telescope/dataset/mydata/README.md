# 模型权重文件存放目录

这个目录用于存放预训练的模型权重文件。

## 必需的文件

### 1. CRNN 识别器权重
- **文件名**: `crnn.pth`
- **路径**: `./dataset/mydata/crnn.pth`
- **用途**: 用于文本识别，在训练、测试和 demo 模式中都需要
- **下载**: 从 [BaiduYunDisk](https://pan.baidu.com/s/1P_SCcQG74fiQfTnfidpHEw) (密码: stt6) 或 [Dropbox](https://www.dropbox.com/sh/f294n405ngbnujn/AABUO6rv_5H5MvIvCblcf-aKa?dl=0) 下载

**注意**: 这只是识别器权重。Demo 测试还需要超分辨率模型权重（见下方说明）。

### 2. Transformer 识别器权重（可选）
- **文件名**: `pretrain_transformer.pth`
- **路径**: `./dataset/mydata/pretrain_transformer.pth`
- **用途**: 用于文本聚焦损失计算（仅在训练时使用）
- **下载**: 同上

## 目录结构

```
dataset/mydata/
├── crnn.pth                    # CRNN 识别器权重（必需）
├── pretrain_transformer.pth    # Transformer 权重（可选，仅训练需要）
├── train1/                     # 训练数据集（LMDB格式，可选）
├── train2/                     # 训练数据集（LMDB格式，可选）
└── test/                       # 测试数据集（可选）
    ├── easy/
    ├── medium/
    └── hard/
```

## 注意事项

1. **对于 Demo/测试**: 
   - 需要 `crnn.pth`（识别器权重，放在此目录）
   - **还需要超分辨率模型权重**（如 `model_best.pth`，放在 `checkpoint/` 目录，通过 `--resume` 参数指定）
   
2. **对于训练**: 
   - 需要 `crnn.pth` 和 `pretrain_transformer.pth`（放在此目录）
   - 需要训练数据集（train1, train2 等）
   
3. 确保文件路径正确，程序会从 `config/super_resolution.yaml` 中读取 CRNN 路径配置

## Demo 测试需要的完整文件清单

Demo 模式需要两个模型文件：

1. **超分辨率模型权重**（如 `model_best.pth`）
   - 位置: `checkpoint/model_best.pth` 或自定义路径
   - 通过 `--resume` 参数指定，例如：
     ```bash
     python main.py --resume checkpoint/model_best.pth --demo --demo_dir ./demo
     ```
   - 下载: 从 README.md 中的链接下载预训练模型

2. **CRNN 识别器权重** (`crnn.pth`)
   - 位置: `./dataset/mydata/crnn.pth`（此目录）
   - 自动从配置文件加载，无需手动指定

## 验证文件是否存在

运行以下命令检查文件：

```bash
ls -lh dataset/mydata/crnn.pth
```

如果文件存在，应该能看到文件大小（通常几十到几百MB）。

