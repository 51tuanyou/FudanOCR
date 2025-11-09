# create_lmdb.py 是否自动生成 HR 和 LR？

## 简短回答

**❌ 不会！** `createDataset` 函数**不会**自动生成 HR 和 LR 版本。

## 详细说明

### `createDataset` 函数的行为

查看 `dataset/create_lmdb.py` 第 184-233 行的 `createDataset` 函数：

```python
def createDataset(outputPath, imagePathList, labelList, ...):
    # ...
    imageKey = 'image-%09d' % cnt
    cache[imageKey] = imageBin  # 只保存原始图像
    cache[labelKey] = label.encode()
    # ...
```

**关键点**：
- ❌ 只保存原始图像（`image-%09d`）
- ❌ **不生成** HR (128×32) 版本
- ❌ **不生成** LR (64×16) 版本
- ✅ 直接保存原始图像的二进制数据

### 训练时的要求

但是，从 `dataset/dataset.py` 的 `lmdbDataset_real` 类可以看到，训练时**需要** HR 和 LR 版本：

```python
img_HR_key = b'image_hr-%09d' % index  # 需要 image_hr
img_lr_key = b'image_lr-%09d' % index  # 需要 image_lr
```

## 解决方案

### 方案 1: 使用 `add_images_to_lmdb.py`（推荐）

这个脚本**会自动生成** HR 和 LR：

```bash
python add_images_to_lmdb.py dataset/mydata/train1 my_images.txt
```

### 方案 2: 使用增强版函数

已创建 `dataset/create_lmdb_with_hr_lr.py`，包含 `createDataset_with_hr_lr` 函数：

```python
from dataset.create_lmdb_with_hr_lr import createDataset_with_hr_lr

# 使用
createDataset_with_hr_lr(
    './dataset/mydata/train3',
    image_paths,
    labels,
    hr_size=(128, 32),  # HR 尺寸
    lr_size=(64, 16)    # LR 尺寸
)
```

### 方案 3: 修改原函数

如果需要，可以修改 `create_lmdb.py` 中的 `createDataset` 函数，添加 HR/LR 生成逻辑。

## 对比总结

| 函数/脚本 | 自动生成 HR/LR | 存储格式 | 推荐度 |
|----------|---------------|---------|--------|
| **`createDataset`** | ❌ 否 | `image-%09d` | ⭐⭐ |
| **`add_images_to_lmdb.py`** | ✅ 是 | `image_hr-%09d`, `image_lr-%09d` | ⭐⭐⭐⭐⭐ |
| **`createDataset_with_hr_lr`** | ✅ 是 | `image_hr-%09d`, `image_lr-%09d` | ⭐⭐⭐⭐ |

## 推荐做法

### 添加数据到现有数据集

**使用 `add_images_to_lmdb.py`**：
```bash
python add_images_to_lmdb.py dataset/mydata/train1 my_images.txt
```

### 创建全新数据集

**使用 `createDataset_with_hr_lr`**：
```python
from dataset.create_lmdb_with_hr_lr import createDataset_with_hr_lr

createDataset_with_hr_lr(
    './dataset/mydata/train3',
    image_paths,
    labels
)
```

## 验证

创建后验证数据格式：

```python
import lmdb
env = lmdb.open('./dataset/mydata/train1', readonly=True)
with env.begin() as txn:
    hr_key = b'image_hr-000000001'
    lr_key = b'image_lr-000000001'
    
    if txn.get(hr_key) and txn.get(lr_key):
        print("✅ 包含 HR 和 LR")
    else:
        print("❌ 缺少 HR 或 LR")
env.close()
```

