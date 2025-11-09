# Scene Text Telescope 快速开始指南

## 最简单的使用方式

### 步骤 1: 准备环境

```bash
# 安装依赖
pip install -r requirement.txt
```

### 步骤 2: 准备图片

将你要识别的图片放入 `demo/` 目录：

```bash
# 确保 demo 目录存在
mkdir -p demo

# 将图片复制到 demo 目录
cp your_image.jpg demo/
```

### 步骤 3: 运行识别

#### 方式 A: 使用简化脚本（推荐）

```bash
# 识别单张图片
python demo_example.py --image_path your_image.jpg --resume checkpoint/model.pth

# 或批量识别 demo 目录中的所有图片
python demo_example.py --demo_dir ./demo --resume checkpoint/model.pth
```

#### 方式 B: 使用原始命令

```bash
python main.py \
    --batch_size=1 \
    --STN \
    --exp_name demo \
    --text_focus \
    --demo \
    --demo_dir ./demo \
    --resume checkpoint/model.pth
```

## 完整示例

假设你有一张名为 `test.jpg` 的图片：

```bash
# 1. 将图片放入 demo 目录
cp test.jpg demo/

# 2. 运行识别（如果有预训练模型）
python demo_example.py --demo_dir ./demo --resume checkpoint/tbsrn.pth

# 3. 查看输出
# 程序会输出识别结果，格式为：
# ['低分辨率识别结果'] ===> ['超分辨率后识别结果']
```

## 注意事项

1. **模型权重**: Demo 测试需要**两个**模型文件：
   - **超分辨率模型权重**（如 `model_best.pth`）
     - 下载链接在原始 README.md 中
     - 放在 `checkpoint/` 目录，通过 `--resume` 参数指定
   - **CRNN 识别器权重** (`crnn.pth`)
     - 放在 `dataset/mydata/` 目录
     - 自动从配置文件加载

2. **如果没有模型权重**: 程序无法正常工作，必须下载这两个模型文件

3. **图片格式**: 支持 .jpg, .png, .jpeg, .bmp, .tiff

## 输出说明

程序会输出：
- 每张图片的处理进度
- 低分辨率图片的识别结果
- 超分辨率后图片的识别结果
- 处理速度（fps）

示例输出：
```
100%|████████████| 1/1 [00:01<00:00,  1.23s/it]
['text'] ===> ['TEXT']
fps=0.81
```

## 获取帮助

查看详细文档：
- `EXAMPLE_USAGE.md` - 详细使用说明
- `README.md` - 项目原始说明

