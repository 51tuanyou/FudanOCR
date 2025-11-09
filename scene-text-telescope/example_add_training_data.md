# 添加训练数据示例

## 示例：添加 5 条样本数据

### 步骤 1: 准备图片文件

创建目录并准备图片：

```bash
cd scene-text-telescope
mkdir -p new_images

# 将你的图片复制到这个目录
# 例如：
# cp /path/to/your/image1.jpg new_images/sample1.jpg
# cp /path/to/your/image2.jpg new_images/sample2.jpg
# ...
```

### 步骤 2: 创建图片列表文件

创建 `example_new_images.txt` 文件（已创建）：

```
./new_images/sample1.jpg HELLO
./new_images/sample2.jpg 2024
./new_images/sample3.jpg "NEW YORK"
./new_images/sample4.jpg ABC123
./new_images/sample5.jpg TEST
```

**格式说明**：
- 每行一个样本
- 格式：`图片路径 标签文本`
- 如果标签包含空格，需要用引号括起来
- 支持相对路径和绝对路径

### 步骤 3: 添加数据到 LMDB

```bash
source .venv37/bin/activate

# 添加到 train1
python add_images_to_lmdb.py dataset/mydata/train1 example_new_images.txt

# 或添加到 train2
python add_images_to_lmdb.py dataset/mydata/train2 example_new_images.txt
```

### 步骤 4: 验证

```bash
# 检查样本数是否增加
python check_dataset.py

# 查看最后几个样本
python view_lmdb.py dataset/mydata/train1 5
```

## 完整示例数据

### 示例文件内容

文件：`example_new_images.txt`

```
# 注释：这是新训练数据示例
# 格式：图片路径 标签

# 示例1: 简单英文单词
./new_images/sample1.jpg HELLO

# 示例2: 数字
./new_images/sample2.jpg 2024

# 示例3: 包含空格的标签
./new_images/sample3.jpg "NEW YORK"

# 示例4: 混合字符
./new_images/sample4.jpg ABC123

# 示例5: 短文本
./new_images/sample5.jpg TEST
```

### 实际使用示例

假设你有以下图片和标签：

| 图片文件 | 标签 | 说明 |
|---------|------|------|
| `street_sign_001.jpg` | `STOP` | 停止标志 |
| `shop_name_001.jpg` | `COFFEE` | 咖啡店招牌 |
| `license_plate_001.jpg` | `ABC123` | 车牌号 |
| `date_001.jpg` | `2024-01-15` | 日期 |
| `address_001.jpg` | `123 MAIN ST` | 地址 |

创建 `my_new_images.txt`：

```
./new_images/street_sign_001.jpg STOP
./new_images/shop_name_001.jpg COFFEE
./new_images/license_plate_001.jpg ABC123
./new_images/date_001.jpg 2024-01-15
./new_images/address_001.jpg "123 MAIN ST"
```

然后运行：

```bash
source .venv37/bin/activate
python add_images_to_lmdb.py dataset/mydata/train1 my_new_images.txt
```

## 图片要求

### 格式要求
- **支持的格式**: JPG, PNG, BMP, TIFF 等常见图像格式
- **图像质量**: 清晰可读的文本图像
- **内容**: 包含文本的场景图像

### 尺寸要求
- **原始尺寸**: 不限制，脚本会自动调整
- **处理后尺寸**:
  - HR (高分辨率): 128×32 像素
  - LR (低分辨率): 64×16 像素

### 标签要求
- **字符类型**: 支持字母、数字、常见标点符号
- **编码**: UTF-8
- **长度**: 建议不超过 100 个字符

## 注意事项

1. **备份数据**: 添加前建议备份
   ```bash
   cp -r dataset/mydata/train1 dataset/mydata/train1_backup
   ```

2. **图片路径**: 确保图片路径正确，可以使用绝对路径或相对路径

3. **标签格式**: 
   - 简单标签：`HELLO`
   - 包含空格：`"NEW YORK"` 或 `NEW_YORK`
   - 特殊字符：直接使用，如 `ABC-123`

4. **验证数据**: 添加后务必验证
   ```bash
   python check_dataset.py
   ```

## 批量添加示例

如果有大量图片，可以批量生成列表文件：

```python
import os

# 假设图片在 new_images 目录，文件名包含标签
image_dir = './new_images'
output_file = 'batch_images.txt'

with open(output_file, 'w', encoding='utf-8') as f:
    for filename in os.listdir(image_dir):
        if filename.lower().endswith(('.jpg', '.png', '.jpeg')):
            # 从文件名提取标签（根据你的命名规则）
            label = filename.split('_')[0].upper()  # 示例：从文件名提取
            img_path = os.path.join(image_dir, filename)
            f.write(f"{img_path} {label}\n")

print(f"已生成 {output_file}")
```

然后使用：
```bash
python add_images_to_lmdb.py dataset/mydata/train1 batch_images.txt
```

