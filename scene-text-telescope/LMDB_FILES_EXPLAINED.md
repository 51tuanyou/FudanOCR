# LMDB 文件说明 (data.mdb 和 lock.mdb)

## 概述

LMDB (Lightning Memory-Mapped Database) 是一个高性能的键值存储数据库。在 `scene-text-telescope` 项目中，训练数据以 LMDB 格式存储，每个数据集目录包含两个文件：

- **`data.mdb`** - 主数据文件
- **`lock.mdb`** - 锁文件

## 文件详细说明

### 1. data.mdb（主数据文件）

#### 作用
- **存储所有实际数据**：包含所有的图像和标签数据
- **键值对存储**：以键值对形式存储数据
- **内存映射**：使用内存映射技术，提供高效的读写性能

#### 存储的内容

根据代码 `dataset/dataset.py`，`data.mdb` 中存储的数据包括：

1. **图像数据**：
   - `image_hr-%09d` - 高分辨率图像（128×32像素）
   - `image_lr-%09d` - 低分辨率图像（64×16像素）
   - 或 `image-%09d` - 单张图像（某些数据集格式）

2. **标签数据**：
   - `label-%09d` - 对应的文本标签

3. **元数据**：
   - `num-samples` - 数据集中的样本总数

#### 数据格式示例

```
键: b'image_hr-000000001'  → 值: 高分辨率图像的二进制数据
键: b'image_lr-000000001'  → 值: 低分辨率图像的二进制数据
键: b'label-000000001'     → 值: b'文本内容'
键: b'num-samples'         → 值: b'17367'
```

#### 文件大小

- **train1/data.mdb**: ~84 MB（14,573 个样本）
- **train2/data.mdb**: ~19 MB（2,794 个样本）

文件大小取决于：
- 样本数量
- 图像分辨率
- 图像压缩质量

### 2. lock.mdb（锁文件）

#### 作用
- **并发控制**：管理多个进程/线程同时访问数据库时的并发控制
- **数据一致性**：确保在写入操作时数据的一致性
- **防止数据损坏**：防止多个写入操作同时进行导致的数据损坏

#### 工作原理

1. **写入锁**：当有进程要写入数据时，会获取写入锁
2. **读取锁**：多个进程可以同时读取数据（共享锁）
3. **互斥锁**：写入时，其他进程必须等待

#### 文件大小

- **lock.mdb**: 通常很小（约 8KB）
- 只包含锁信息，不包含实际数据

#### 在代码中的使用

从 `dataset/dataset.py` 可以看到，代码在打开 LMDB 时设置了：

```python
self.env = lmdb.open(
    root,
    max_readers=1,      # 最大读取者数量
    readonly=True,      # 只读模式
    lock=False,         # 不使用锁（只读时）
    readahead=False,
    meminit=False
)
```

**注意**：在只读模式下，`lock=False` 表示不需要锁文件，但文件仍然存在。

## 文件关系

```
数据集目录/
├── data.mdb  ← 存储所有实际数据（图像、标签等）
└── lock.mdb  ← 管理并发访问（通常很小，8KB左右）
```

## 实际使用场景

### 训练时（只读）

```python
# 打开 LMDB 数据库（只读模式）
env = lmdb.open('./dataset/mydata/train1', readonly=True, lock=False)

# 开始事务（只读）
with env.begin(write=False) as txn:
    # 读取样本数
    nSamples = int(txn.get(b'num-samples'))
    
    # 读取图像
    img_data = txn.get(b'image_hr-000000001')
    
    # 读取标签
    label = txn.get(b'label-000000001').decode()
```

### 创建数据集时（写入）

```python
# 打开 LMDB 数据库（写入模式）
env = lmdb.open(outputPath, map_size=1099511627776)

# 写入数据
with env.begin(write=True) as txn:
    txn.put(b'image-000000001', image_binary_data)
    txn.put(b'label-000000001', b'text label')
```

## 文件管理

### 是否可以删除？

- **data.mdb**: ❌ **绝对不能删除** - 包含所有训练数据
- **lock.mdb**: ⚠️ **通常可以删除** - 如果数据库已关闭，锁文件可以删除，下次打开时会自动重建

### 文件备份

如果需要备份数据集：
```bash
# 备份整个目录（包括两个文件）
cp -r dataset/mydata/train1 dataset/mydata/train1_backup

# 或只备份数据文件（lock.mdb 可以忽略）
cp dataset/mydata/train1/data.mdb dataset/mydata/train1_backup/
```

### 文件损坏

如果 `data.mdb` 损坏：
- ❌ 数据可能丢失
- ✅ 建议从原始数据重新创建 LMDB

如果 `lock.mdb` 损坏：
- ✅ 通常可以删除，重新打开数据库时会自动重建
- ⚠️ 如果数据库正在使用，删除可能导致问题

## 性能特点

### LMDB 的优势

1. **高性能**：
   - 使用内存映射，读写速度快
   - 适合大量小文件的存储

2. **低开销**：
   - 不需要额外的数据库服务器
   - 文件系统级别的存储

3. **并发安全**：
   - 内置锁机制
   - 支持多进程/多线程访问

### 在项目中的使用

从代码可以看到，项目使用 LMDB 存储训练数据的好处：

1. **快速加载**：训练时可以快速随机访问任意样本
2. **节省空间**：比单独存储图像文件更节省空间
3. **便于管理**：所有数据集中在一个文件中

## 检查文件

### 查看文件信息

```bash
# 查看文件大小
ls -lh dataset/mydata/train1/
# 输出：
# data.mdb  84M  (主数据文件)
# lock.mdb  8.0K (锁文件)
```

### 使用 Python 检查内容

```python
import lmdb

# 打开数据库
env = lmdb.open('./dataset/mydata/train1', readonly=True)

# 查看所有键
with env.begin() as txn:
    cursor = txn.cursor()
    for key, value in cursor:
        print(f"Key: {key}, Value size: {len(value)} bytes")
```

## 总结

| 文件 | 作用 | 大小 | 重要性 | 可删除 |
|------|------|------|--------|--------|
| **data.mdb** | 存储所有训练数据（图像、标签） | 大（MB级） | ⭐⭐⭐⭐⭐ | ❌ 不能 |
| **lock.mdb** | 管理并发访问控制 | 小（KB级） | ⭐⭐ | ⚠️ 可以（数据库关闭时） |

### 关键要点

1. **data.mdb 是核心**：包含所有实际数据，绝对不能删除
2. **lock.mdb 是辅助**：用于并发控制，通常很小
3. **两个文件配合工作**：共同构成完整的 LMDB 数据库
4. **只读模式**：训练时通常只读取，不需要锁文件，但文件仍然存在

## 相关代码位置

- **数据集加载**: `dataset/dataset.py` - `lmdbDataset_real` 类
- **数据集创建**: `dataset/create_lmdb.py` - `createDataset` 函数
- **数据集检查**: `check_dataset.py` - 检查样本数量

