# 修复 Demo 函数中的图像文件过滤

## 问题

Demo 函数尝试处理目录中的所有文件，包括非图像文件（如 README.md），导致错误：

```
PIL.UnidentifiedImageError: cannot identify image file './demo/README.md'
```

## 修复的文件

### `interfaces/super_resolution.py`

**修复内容**:
1. 添加图像文件扩展名过滤
2. 只处理支持的图像格式
3. 添加异常处理，跳过无法处理的文件
4. 修复图像计数

## 修复方法

### 之前
```python
for im_name in tqdm(os.listdir(self.args.demo_dir)):
    images_lr = transform_(os.path.join(self.args.demo_dir, im_name))
    # ...
sum_images = len(os.listdir(self.args.demo_dir))
```

### 之后
```python
# 支持的图像格式
image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif', '.webp'}
# 过滤出图像文件
image_files = [f for f in os.listdir(self.args.demo_dir) 
              if os.path.splitext(f.lower())[1] in image_extensions]

for im_name in tqdm(image_files):
    try:
        images_lr = transform_(os.path.join(self.args.demo_dir, im_name))
    except Exception as e:
        logging.warning(f'跳过文件 {im_name}: {e}')
        continue
    # ...
sum_images = len(image_files)
```

## 支持的图像格式

- `.jpg`, `.jpeg` - JPEG 图像
- `.png` - PNG 图像
- `.bmp` - BMP 图像
- `.tiff`, `.tif` - TIFF 图像
- `.gif` - GIF 图像
- `.webp` - WebP 图像

## 改进

1. **文件过滤**: 只处理图像文件，跳过其他文件
2. **异常处理**: 如果某个图像文件无法处理，会跳过并记录警告
3. **准确计数**: 只统计实际处理的图像文件数量

## 验证

修复后可以正常运行：

```bash
source .venv37/bin/activate
python main.py --batch_size=1 --STN --exp_name demo --text_focus --demo --demo_dir ./demo --resume checkpoint/model_best.pth
```

现在 demo 目录中可以包含 README.md 等非图像文件，不会被处理。

