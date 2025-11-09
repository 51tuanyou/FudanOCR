# Scene Text Telescope 图片识别示例使用说明

## 简介

Scene Text Telescope 是一个用于场景文本图像超分辨率的工具，可以提升低分辨率文本图像的质量，然后进行文本识别。

## 快速开始

### 1. 安装依赖

```bash
cd scene-text-telescope
pip install -r requirement.txt
```

### 2. 准备模型权重（必需）

Demo 测试需要**两个**模型文件：

1. **超分辨率模型权重**（如 `model_best.pth`）
   - 下载: [预训练模型](https://drive.google.com/file/d/1a-BNCC1pFczz4AkY8sJatg3GpeX1MCCr/view?usp=sharing)
   - 位置: `checkpoint/model_best.pth` 或自定义路径
   - 使用: 通过 `--resume` 参数指定

2. **CRNN 识别器权重** (`crnn.pth`)
   - 下载: [BaiduYunDisk](https://pan.baidu.com/s/1P_SCcQG74fiQfTnfidpHEw) (密码: stt6) 或 [Dropbox](https://www.dropbox.com/sh/f294n405ngbnujn/AABUO6rv_5H5MvIvCblcf-aKa?dl=0)
   - 位置: `dataset/mydata/crnn.pth`
   - 使用: 自动从配置文件加载

### 3. 使用示例脚本

#### 方式一：识别单张图片

```bash
python demo_example.py --image_path path/to/your/image.jpg --resume checkpoint/your_model.pth
```

#### 方式二：批量识别目录中的图片

```bash
# 首先将图片放入 demo 目录
mkdir -p demo
cp your_images/*.jpg demo/

# 运行识别
python demo_example.py --demo_dir ./demo --resume checkpoint/your_model.pth
```

### 4. 使用原始命令（高级用法）

如果需要更多控制，可以使用原始的 main.py：

```bash
python main.py \
    --batch_size=1 \
    --STN \
    --exp_name demo_example \
    --text_focus \
    --demo \
    --demo_dir ./demo \
    --resume checkpoint/your_model.pth \
    --arch tbsrn
```

## 参数说明

### demo_example.py 参数

- `--image_path`: 单张图片路径
- `--demo_dir`: 图片目录路径（默认: ./demo）
- `--exp_name`: 实验名称（默认: demo_example）
- `--resume`: 模型权重路径
- `--arch`: 模型架构（默认: tbsrn）
  - 可选: tbsrn, tsrn, bicubic, srcnn, vdsr, srres, esrgan, rdn, edsr, lapsrn
- `--text_focus`: 启用文本聚焦模式（默认: True）
- `--STN`: 使用空间变换网络（默认: True）
- `--batch_size`: 批次大小（默认: 1）
- `--rec`: 识别器类型（默认: crnn）

## 示例输出

运行后，程序会：
1. 对每张图片进行超分辨率处理
2. 使用 CRNN 识别器识别文本
3. 输出识别结果，格式为：`低分辨率识别结果 ===> 超分辨率后识别结果`

例如：
```
['text'] ===> ['TEXT']
```

## 注意事项

1. **模型权重**: 如果不指定 `--resume`，程序会使用默认配置，可能无法正常工作。建议下载预训练模型。

2. **图片格式**: 支持的图片格式包括：.png, .jpg, .jpeg, .bmp, .tiff

3. **图片尺寸**: 程序会自动将图片调整为 64x16 像素进行处理

4. **GPU/CPU**: 如果有 GPU，程序会自动使用 GPU 加速。如果没有 GPU，会在 CPU 上运行（速度较慢）

5. **依赖版本**: 注意 requirement.txt 中指定的版本，特别是 PyTorch 1.2.0，可能需要根据你的环境调整

## 故障排除

### 问题1: 找不到模型文件
```
错误: 模型权重文件不存在
```
**解决方案**: 
- 确保使用 `--resume` 参数指定超分辨率模型路径（如 `checkpoint/model_best.pth`）
- 确保 `crnn.pth` 文件在 `dataset/mydata/` 目录下
- 检查两个模型文件是否都已下载

### 问题2: CUDA 相关错误
```
RuntimeError: CUDA out of memory
```
**解决方案**: 
- 减小 `--batch_size`
- 或者使用 CPU 模式（需要修改代码中的 cuda 设置）

### 问题3: 识别结果为空或不准确
**可能原因**:
- 图片质量太低
- 图片中没有文本
- 模型权重未正确加载

## 更多信息

- 项目主页: [Scene Text Telescope](https://openaccess.thecvf.com/content/CVPR2021/html/Chen_Scene_Text_Telescope_Text-Focused_Scene_Image_Super-Resolution_CVPR_2021_paper.html)
- 原始 README: 查看 `README.md`

