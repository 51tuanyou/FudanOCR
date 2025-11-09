# create_lmdb.py 和 add_images_to_lmdb.py 的区别

## 关键发现

**`createDataset` 函数不会自动生成 HR 和 LR 版本！**

## 详细对比

### 1. `createDataset` 函数（在 create_lmdb.py 中）

**不会自动生成 HR 和 LR**

```python
def createDataset(outputPath, imagePathList, labelList, ...):
    # ...
    imageKey = 'image-%09d' % cnt
    cache[imageKey] = imageBin  # 只保存原始图像，不生成 HR/LR
    cache[labelKey] = label.encode()
    # ...
```

**特点**：
- ❌ 只保存原始图像（`image-%09d`）
- ❌ 不生成 HR (128×32) 版本
- ❌ 不生成 LR (64×16) 版本
- ✅ 直接保存原始图像的二进制数据

**存储格式**：
```
image-000000001 → 原始图像数据
label-000000001 → 标签文本
```

### 2. `add_images_to_lmdb.py` 脚本

**会自动生成 HR 和 LR**

```python
# 自动生成高分辨率版本 (128×32)
img_hr = img.resize((128, 32), Image.BICUBIC)

# 自动生成低分辨率版本 (64×16)
img_lr = img.resize((64, 16), Image.BICUBIC)

# 保存两个版本
txn.put(hr_key, hr_data)  # image_hr-000000001
txn.put(lr_key, lr_data)  # image_lr-000000001
```

**特点**：
- ✅ 自动生成 HR (128×32) 版本
- ✅ 自动生成 LR (64×16) 版本
- ✅ 保存两个版本到 LMDB

**存储格式**：
```
image_hr-000000001 → HR 图像数据 (128×32)
image_lr-000000001 → LR 图像数据 (64×16)
label-000000001 → 标签文本
```

### 3. `create_from_lmdb` 函数（在 create_lmdb.py 中）

**会生成 HR 和 LR，但用于特殊场景**

```python
def create_from_lmdb():
    # 从已有 LMDB 读取
    image = buf2PIL(txn, imageKey)
    out_image = rand_crop(image)  # 随机裁剪生成 LR
    
    # 保存 HR 和 LR
    cache_out[image_HR_Key] = PIL2buf(image)
    cache_out[image_lr_Key] = PIL2buf(out_image)
```

**特点**：
- ✅ 会生成 HR 和 LR
- ⚠️ 但这是从已有 LMDB 转换，不是从原始图片创建
- ⚠️ LR 是通过随机裁剪生成，不是固定尺寸

## 训练时的要求

从 `dataset/dataset.py` 的 `lmdbDataset_real` 类可以看到，训练时**需要** HR 和 LR 版本：

```python
img_HR_key = b'image_hr-%09d' % index  # 需要 image_hr
img_lr_key = b'image_lr-%09d' % index  # 需要 image_lr
```

## 解决方案

### 方案 1: 使用 `add_images_to_lmdb.py`（推荐）

**优点**：
- ✅ 自动生成 HR 和 LR
- ✅ 统一尺寸 (128×32, 64×16)
- ✅ 符合训练要求

```bash
python add_images_to_lmdb.py dataset/mydata/train1 my_images.txt
```

### 方案 2: 修改 `createDataset` 函数

创建一个新函数，基于 `createDataset` 但添加 HR/LR 生成：

```python
def createDataset_with_hr_lr(outputPath, imagePathList, labelList, 
                             hr_size=(128, 32), lr_size=(64, 16)):
    """创建包含 HR 和 LR 版本的 LMDB 数据集"""
    from PIL import Image
    import io
    
    assert (len(imagePathList) == len(labelList))
    nSamples = len(imagePathList)
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
    env = lmdb.open(outputPath, map_size=1099511627776)
    cache = {}
    cnt = 1
    
    for i in range(nSamples):
        imagePath = imagePathList[i]
        label = labelList[i]
        if len(label) == 0:
            continue
        if not os.path.exists(imagePath):
            print('%s does not exist' % imagePath)
            continue
        
        # 读取并处理图像
        img = Image.open(imagePath)
        
        # 生成 HR 版本
        img_hr = img.resize(hr_size, Image.BICUBIC)
        hr_buf = io.BytesIO()
        img_hr.save(hr_buf, format='PNG')
        hr_data = hr_buf.getvalue()
        
        # 生成 LR 版本
        img_lr = img.resize(lr_size, Image.BICUBIC)
        lr_buf = io.BytesIO()
        img_lr.save(lr_buf, format='PNG')
        lr_data = lr_buf.getvalue()
        
        # 保存
        hr_key = f'image_hr-{cnt:09d}'
        lr_key = f'image_lr-{cnt:09d}'
        label_key = f'label-{cnt:09d}'
        
        cache[hr_key] = hr_data
        cache[lr_key] = lr_data
        cache[label_key] = label.encode()
        
        if cnt % 1000 == 0:
            writeCache(env, cache)
            cache = {}
            print('Written %d / %d' % (cnt, nSamples))
        cnt += 1
    
    nSamples = cnt - 1
    cache['num-samples'] = str(nSamples).encode()
    writeCache(env, cache)
    print('Created dataset with %d samples' % nSamples)
```

### 方案 3: 使用现有的 `create_from_lmdb` 模式

但需要先创建只有原始图像的 LMDB，然后再转换（不推荐，太复杂）。

## 总结对比表

| 函数/脚本 | 生成 HR/LR | 存储格式 | 适用场景 |
|----------|-----------|---------|---------|
| **`createDataset`** | ❌ 否 | `image-%09d` | 通用 CRNN 训练（不需要 HR/LR） |
| **`add_images_to_lmdb.py`** | ✅ 是 | `image_hr-%09d`, `image_lr-%09d` | **推荐：添加数据到现有数据集** |
| **`create_from_lmdb`** | ✅ 是 | `image_HR-%09d`, `image_lr-%09d` | 从已有 LMDB 转换 |

## 推荐做法

### 如果要添加新数据到现有数据集

**使用 `add_images_to_lmdb.py`**：
```bash
python add_images_to_lmdb.py dataset/mydata/train1 my_images.txt
```

### 如果要创建全新的数据集

**修改 `createDataset` 函数**，或使用我创建的增强版本：

```python
# 在 create_lmdb.py 中添加新函数
from dataset.create_lmdb import createDataset_with_hr_lr

# 使用
createDataset_with_hr_lr('./dataset/mydata/train3', image_paths, labels)
```

## 验证数据格式

创建后验证数据格式是否正确：

```python
import lmdb
env = lmdb.open('./dataset/mydata/train1', readonly=True)
with env.begin() as txn:
    # 检查是否有 HR 和 LR
    hr_key = b'image_hr-000000001'
    lr_key = b'image_lr-000000001'
    
    if txn.get(hr_key) and txn.get(lr_key):
        print("✅ 数据格式正确：包含 HR 和 LR")
    else:
        print("❌ 数据格式错误：缺少 HR 或 LR")
env.close()
```

