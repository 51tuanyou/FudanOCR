# 图像尺寸说明：HR 和 LR 的生成

## 简短回答

**是的！** 你只需要提供一张原始图片，脚本会自动：
1. 读取你的原始图片（任意尺寸）
2. 自动生成 HR (128×32) 版本
3. 自动生成 LR (64×16) 版本
4. 将两个版本都保存到 LMDB 数据库中

## 详细说明

### 1. 你只需要提供一张图片

当你使用 `add_images_to_lmdb.py` 脚本时：

```bash
python add_images_to_lmdb.py dataset/mydata/train1 example_new_images.txt
```

脚本会：
- 读取你提供的原始图片（可以是任意尺寸，如 800×200, 500×100 等）
- **自动调整**为 HR (128×32) 和 LR (64×16)
- 保存到 LMDB

### 2. 自动生成过程

从 `add_images_to_lmdb.py` 代码可以看到：

```python
# 读取原始图片
img = Image.open(io.BytesIO(imageBin))

# 自动生成高分辨率版本 (128×32)
img_hr = img.resize((128, 32), Image.BICUBIC)
hr_buf = io.BytesIO()
img_hr.save(hr_buf, format='PNG')
hr_data = hr_buf.getvalue()

# 自动生成低分辨率版本 (64×16)
img_lr = img.resize((64, 16), Image.BICUBIC)
lr_buf = io.BytesIO()
img_lr.save(lr_buf, format='PNG')
lr_data = lr_buf.getvalue()

# 保存到 LMDB
txn.put(hr_key, hr_data)  # 保存 HR
txn.put(lr_key, lr_data)  # 保存 LR
```

### 3. 实际数据集中的情况

**注意**：从实际查看 train1 数据集发现，现有数据中的 HR 和 LR 图像尺寸**不是**标准的 128×32 和 64×16，而是各种不同的尺寸（如 332×46）。

这说明：
- **原始数据集**可能存储了不同尺寸的图像
- **训练时**，代码会动态调整大小（见 `dataset.py` 中的 `resizeNormalize`）
- **添加新数据时**，脚本会统一调整为标准尺寸（128×32 和 64×16）

### 4. 训练时的处理

在训练时，`dataset.py` 中的 `resizeNormalize` 会进一步处理：

```python
# 训练时会再次调整到配置的尺寸
transform = resizeNormalize((imgW, imgH), self.mask)
# 其中 imgW=128, imgH=32 (从配置文件读取)
```

所以：
- **存储时**：可以存储标准尺寸（128×32, 64×16）或原始尺寸
- **训练时**：会统一调整到配置的尺寸

### 5. 推荐做法

#### 方式 1: 使用脚本自动调整（推荐）

```bash
# 提供任意尺寸的原始图片
python add_images_to_lmdb.py dataset/mydata/train1 my_images.txt
```

脚本会自动：
- 调整为 HR (128×32)
- 调整为 LR (64×16)
- 保存到 LMDB

**优点**：
- 简单方便
- 统一尺寸
- 符合训练要求

#### 方式 2: 手动预处理（如果需要保持原始尺寸）

如果你想保持原始尺寸，需要修改脚本，但**不推荐**，因为：
- 训练时需要统一尺寸
- 不同尺寸可能导致训练不稳定

### 6. 完整流程示例

```bash
# 1. 准备原始图片（任意尺寸）
mkdir -p new_images
cp your_image.jpg new_images/sample1.jpg  # 可以是 800×200, 500×100 等任意尺寸

# 2. 创建列表文件
cat > my_images.txt << EOF
./new_images/sample1.jpg HELLO
EOF

# 3. 添加数据（脚本自动生成 HR 和 LR）
source .venv37/bin/activate
python add_images_to_lmdb.py dataset/mydata/train1 my_images.txt

# 输出：
# 当前样本数: 14573
# 已处理 1/1 个图片...
# 完成!
# 成功添加: 1 个样本
# 总样本数: 14573 -> 14574
```

### 7. 验证添加的数据

```python
import lmdb
from PIL import Image
import io

env = lmdb.open('./dataset/mydata/train1', readonly=True)
with env.begin() as txn:
    # 查看最后添加的样本（假设是第 14574 个）
    hr_key = b'image_hr-000014574'
    lr_key = b'image_lr-000014574'
    
    hr_data = txn.get(hr_key)
    lr_data = txn.get(lr_key)
    
    if hr_data:
        img_hr = Image.open(io.BytesIO(hr_data))
        print(f'HR 尺寸: {img_hr.size[0]}x{img_hr.size[1]}')  # 应该是 128x32
    
    if lr_data:
        img_lr = Image.open(io.BytesIO(lr_data))
        print(f'LR 尺寸: {img_lr.size[0]}x{img_lr.size[1]}')  # 应该是 64x16
env.close()
```

## 总结

✅ **是的，只需要提供一张原始图片**

脚本会自动：
1. ✅ 读取你的原始图片（任意尺寸）
2. ✅ 生成 HR (128×32) 版本
3. ✅ 生成 LR (64×16) 版本
4. ✅ 保存两个版本到 LMDB

**你不需要**：
- ❌ 手动调整图片尺寸
- ❌ 创建两个版本的图片
- ❌ 担心图片尺寸问题

**只需要**：
- ✅ 提供原始图片文件
- ✅ 提供对应的文本标签
- ✅ 运行脚本即可

