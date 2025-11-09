# 如何打开和添加图片到 LMDB 数据集

## 一、如何打开/查看 MDB 文件

### 方法 1: 使用 Python + lmdb 库（推荐）

#### 安装依赖
```bash
source .venv37/bin/activate
pip install lmdb
```

#### 查看 LMDB 内容

创建脚本 `view_lmdb.py`:

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查看 LMDB 数据集内容
"""
import lmdb
from PIL import Image
import io

def view_lmdb(lmdb_path, max_samples=5):
    """查看 LMDB 数据集的前几个样本"""
    env = lmdb.open(lmdb_path, readonly=True, lock=False)
    
    with env.begin() as txn:
        # 获取样本数
        num_samples = int(txn.get(b'num-samples'))
        print(f"总样本数: {num_samples}")
        print(f"显示前 {min(max_samples, num_samples)} 个样本:\n")
        
        # 查看前几个样本
        for i in range(1, min(max_samples + 1, num_samples + 1)):
            print(f"样本 {i}:")
            
            # 尝试读取高分辨率图像
            hr_key = f'image_hr-{i:09d}'.encode()
            lr_key = f'image_lr-{i:09d}'.encode()
            label_key = f'label-{i:09d}'.encode()
            
            # 读取标签
            label = txn.get(label_key)
            if label:
                print(f"  标签: {label.decode()}")
            
            # 读取图像
            hr_data = txn.get(hr_key)
            lr_data = txn.get(lr_key)
            
            if hr_data:
                print(f"  高分辨率图像: {len(hr_data)} bytes")
            if lr_data:
                print(f"  低分辨率图像: {len(lr_data)} bytes")
            
            # 如果没有 HR/LR，尝试读取单张图像
            if not hr_data:
                img_key = f'image-{i:09d}'.encode()
                img_data = txn.get(img_key)
                if img_data:
                    print(f"  图像: {len(img_data)} bytes")
            
            print()
    
    env.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("用法: python view_lmdb.py <lmdb_path> [max_samples]")
        sys.exit(1)
    
    lmdb_path = sys.argv[1]
    max_samples = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    view_lmdb(lmdb_path, max_samples)
```

使用方法：
```bash
source .venv37/bin/activate
python view_lmdb.py dataset/mydata/train1 10
```

#### 提取图像

创建脚本 `extract_images.py`:

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从 LMDB 中提取图像
"""
import lmdb
from PIL import Image
import io
import os

def extract_images(lmdb_path, output_dir, num_samples=10):
    """从 LMDB 中提取图像"""
    env = lmdb.open(lmdb_path, readonly=True, lock=False)
    os.makedirs(output_dir, exist_ok=True)
    
    with env.begin() as txn:
        num_total = int(txn.get(b'num-samples'))
        num_extract = min(num_samples, num_total)
        
        for i in range(1, num_extract + 1):
            # 读取高分辨率图像
            hr_key = f'image_hr-{i:09d}'.encode()
            lr_key = f'image_lr-{i:09d}'.encode()
            label_key = f'label-{i:09d}'.encode()
            
            label = txn.get(label_key)
            label_str = label.decode() if label else f'sample_{i}'
            
            # 提取高分辨率图像
            hr_data = txn.get(hr_key)
            if hr_data:
                img = Image.open(io.BytesIO(hr_data))
                img.save(os.path.join(output_dir, f'{i:09d}_hr_{label_str}.png'))
                print(f"已提取: {i:09d}_hr_{label_str}.png")
            
            # 提取低分辨率图像
            lr_data = txn.get(lr_key)
            if lr_data:
                img = Image.open(io.BytesIO(lr_data))
                img.save(os.path.join(output_dir, f'{i:09d}_lr_{label_str}.png'))
    
    env.close()
    print(f"\n已提取 {num_extract} 个样本到 {output_dir}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("用法: python extract_images.py <lmdb_path> <output_dir> [num_samples]")
        sys.exit(1)
    
    lmdb_path = sys.argv[1]
    output_dir = sys.argv[2]
    num_samples = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    extract_images(lmdb_path, output_dir, num_samples)
```

### 方法 2: 使用命令行工具（如果有）

```bash
# 安装 mdb-utils (如果可用)
# macOS: brew install mdb-utils (可能不可用)
# Linux: apt-get install mdb-tools
```

**注意**: LMDB 不是标准的 MDB 格式，不能直接用 Microsoft Access 工具打开。

## 二、添加新图片到训练数据集

### 方案 1: 创建新的 LMDB 数据集（推荐）

#### 步骤 1: 准备图片和标签

创建目录结构：
```
my_new_images/
├── images/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
└── labels.txt
```

`labels.txt` 格式：
```
image1.jpg text1
image2.jpg text2
...
```

#### 步骤 2: 创建添加图片的脚本

创建 `add_images_to_lmdb.py`:

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
添加新图片到现有的 LMDB 数据集
"""
import os
import lmdb
import cv2
from PIL import Image
import numpy as np

def checkImageIsValid(imageBin):
    """检查图像是否有效"""
    if imageBin is None:
        return False
    imageBuf = np.fromstring(imageBin, dtype=np.uint8)
    img = cv2.imdecode(imageBuf, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return False
    imgH, imgW = img.shape[0], img.shape[1]
    if imgH * imgW == 0:
        return False
    return True

def add_images_to_lmdb(lmdb_path, image_paths, labels, create_hr_lr=True):
    """
    添加新图片到现有的 LMDB 数据集
    
    Args:
        lmdb_path: LMDB 数据集路径
        image_paths: 新图片路径列表
        labels: 对应的标签列表
        create_hr_lr: 是否创建 HR 和 LR 版本
    """
    assert len(image_paths) == len(labels), "图片和标签数量必须一致"
    
    # 打开现有数据库（写入模式）
    env = lmdb.open(lmdb_path, map_size=1099511627776)
    
    # 获取当前样本数
    with env.begin() as txn:
        num_samples = int(txn.get(b'num-samples'))
        print(f"当前样本数: {num_samples}")
    
    # 添加新样本
    new_count = 0
    with env.begin(write=True) as txn:
        for i, (img_path, label) in enumerate(zip(image_paths, labels)):
            if not os.path.exists(img_path):
                print(f"警告: 图片不存在 {img_path}")
                continue
            
            # 读取图像
            with open(img_path, 'rb') as f:
                imageBin = f.read()
            
            # 检查图像有效性
            if not checkImageIsValid(imageBin):
                print(f"警告: 无效图像 {img_path}")
                continue
            
            # 创建 HR 和 LR 版本
            if create_hr_lr:
                # 读取图像并调整大小
                img = Image.open(io.BytesIO(imageBin))
                
                # 高分辨率: 128x32
                img_hr = img.resize((128, 32), Image.BICUBIC)
                hr_buf = io.BytesIO()
                img_hr.save(hr_buf, format='PNG')
                hr_data = hr_buf.getvalue()
                
                # 低分辨率: 64x16
                img_lr = img.resize((64, 16), Image.BICUBIC)
                lr_buf = io.BytesIO()
                img_lr.save(lr_buf, format='PNG')
                lr_data = lr_buf.getvalue()
                
                # 写入数据
                new_idx = num_samples + new_count + 1
                hr_key = f'image_hr-{new_idx:09d}'.encode()
                lr_key = f'image_lr-{new_idx:09d}'.encode()
                label_key = f'label-{new_idx:09d}'.encode()
                
                txn.put(hr_key, hr_data)
                txn.put(lr_key, lr_data)
                txn.put(label_key, label.encode())
            else:
                # 只存储原始图像
                new_idx = num_samples + new_count + 1
                img_key = f'image-{new_idx:09d}'.encode()
                label_key = f'label-{new_idx:09d}'.encode()
                
                txn.put(img_key, imageBin)
                txn.put(label_key, label.encode())
            
            new_count += 1
            if (i + 1) % 100 == 0:
                print(f"已添加 {i + 1}/{len(image_paths)} 个样本")
        
        # 更新样本总数
        new_total = num_samples + new_count
        txn.put(b'num-samples', str(new_total).encode())
    
    env.close()
    print(f"\n完成! 添加了 {new_count} 个新样本")
    print(f"总样本数: {num_samples} -> {new_total}")

if __name__ == '__main__':
    import sys
    import io
    
    if len(sys.argv) < 3:
        print("用法: python add_images_to_lmdb.py <lmdb_path> <image_dir> <labels_file>")
        print("或: python add_images_to_lmdb.py <lmdb_path> <image_list.txt>")
        sys.exit(1)
    
    lmdb_path = sys.argv[1]
    
    # 读取图片和标签
    image_paths = []
    labels = []
    
    if len(sys.argv) == 4:
        # 方式1: 提供图片目录和标签文件
        image_dir = sys.argv[2]
        labels_file = sys.argv[3]
        
        with open(labels_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(' ', 1)
                if len(parts) == 2:
                    img_name, label = parts
                    img_path = os.path.join(image_dir, img_name)
                    if os.path.exists(img_path):
                        image_paths.append(img_path)
                        labels.append(label)
    else:
        # 方式2: 提供包含图片路径和标签的文件
        list_file = sys.argv[2]
        with open(list_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(' ', 1)
                if len(parts) == 2:
                    img_path, label = parts
                    if os.path.exists(img_path):
                        image_paths.append(img_path)
                        labels.append(label)
    
    print(f"准备添加 {len(image_paths)} 个样本到 {lmdb_path}")
    add_images_to_lmdb(lmdb_path, image_paths, labels, create_hr_lr=True)
```

### 方案 2: 创建全新的数据集（包含旧数据和新数据）

#### 步骤 1: 从现有 LMDB 提取所有数据

创建 `rebuild_lmdb_with_new_images.py`:

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重建 LMDB 数据集，包含原有数据和新图片
"""
import os
import lmdb
from PIL import Image
import io

def rebuild_lmdb_with_new_images(old_lmdb_path, new_lmdb_path, 
                                  new_image_paths, new_labels):
    """
    从旧 LMDB 提取数据，添加新图片，创建新的 LMDB
    """
    # 打开旧数据库
    old_env = lmdb.open(old_lmdb_path, readonly=True)
    
    # 创建新数据库
    new_env = lmdb.open(new_lmdb_path, map_size=1099511627776)
    
    # 从旧数据库复制数据
    with old_env.begin() as old_txn:
        num_old = int(old_txn.get(b'num-samples'))
        print(f"从旧数据集复制 {num_old} 个样本...")
        
        with new_env.begin(write=True) as new_txn:
            for i in range(1, num_old + 1):
                # 复制高分辨率图像
                hr_key = f'image_hr-{i:09d}'.encode()
                hr_data = old_txn.get(hr_key)
                if hr_data:
                    new_txn.put(hr_key, hr_data)
                
                # 复制低分辨率图像
                lr_key = f'image_lr-{i:09d}'.encode()
                lr_data = old_txn.get(lr_key)
                if lr_data:
                    new_txn.put(lr_key, lr_data)
                
                # 复制标签
                label_key = f'label-{i:09d}'.encode()
                label_data = old_txn.get(label_key)
                if label_data:
                    new_txn.put(label_key, label_data)
    
    old_env.close()
    
    # 添加新图片（使用之前创建的 add_images_to_lmdb 函数）
    # ... (代码类似)
    
    new_env.close()
    print("完成!")

# 使用 createDataset 函数创建新数据集
from dataset.create_lmdb import createDataset

# 收集所有图片路径和标签
all_image_paths = []
all_labels = []

# 1. 从旧 LMDB 提取
# ... (提取代码)

# 2. 添加新图片
all_image_paths.extend(new_image_paths)
all_labels.extend(new_labels)

# 3. 创建新 LMDB
createDataset(new_lmdb_path, all_image_paths, all_labels)
```

### 方案 3: 使用项目自带的 createDataset 函数

最简单的方法是使用项目中的 `createDataset` 函数：

```python
from dataset.create_lmdb import createDataset

# 准备图片路径和标签列表
image_paths = [
    'path/to/image1.jpg',
    'path/to/image2.jpg',
    # ...
]

labels = [
    'text1',
    'text2',
    # ...
]

# 创建新的 LMDB 数据集
output_path = './dataset/mydata/train3'  # 新数据集
createDataset(output_path, image_paths, labels)
```

然后在配置文件中添加：
```yaml
train_data_dir: [
    './dataset/mydata/train1',
    './dataset/mydata/train2',
    './dataset/mydata/train3',  # 新添加的数据集
]
```

## 三、完整示例：添加新图片

### 示例 1: 添加单张图片

```python
import lmdb
from PIL import Image
import io

def add_single_image(lmdb_path, image_path, label):
    """添加单张图片到 LMDB"""
    env = lmdb.open(lmdb_path, map_size=1099511627776)
    
    # 获取当前样本数
    with env.begin() as txn:
        num_samples = int(txn.get(b'num-samples'))
    
    # 读取并处理图像
    img = Image.open(image_path)
    img_hr = img.resize((128, 32), Image.BICUBIC)
    img_lr = img.resize((64, 16), Image.BICUBIC)
    
    # 转换为字节
    hr_buf = io.BytesIO()
    img_hr.save(hr_buf, format='PNG')
    hr_data = hr_buf.getvalue()
    
    lr_buf = io.BytesIO()
    img_lr.save(lr_buf, format='PNG')
    lr_data = lr_buf.getvalue()
    
    # 写入数据库
    new_idx = num_samples + 1
    with env.begin(write=True) as txn:
        txn.put(f'image_hr-{new_idx:09d}'.encode(), hr_data)
        txn.put(f'image_lr-{new_idx:09d}'.encode(), lr_data)
        txn.put(f'label-{new_idx:09d}'.encode(), label.encode())
        txn.put(b'num-samples', str(new_idx).encode())
    
    env.close()
    print(f"已添加图片，新样本数: {new_idx}")

# 使用
add_single_image('./dataset/mydata/train1', 'new_image.jpg', 'NEW TEXT')
```

### 示例 2: 批量添加图片

```python
def add_batch_images(lmdb_path, image_dir, labels_file):
    """批量添加图片"""
    # 读取标签文件
    image_paths = []
    labels = []
    
    with open(labels_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(' ', 1)
            if len(parts) == 2:
                img_name, label = parts
                img_path = os.path.join(image_dir, img_name)
                if os.path.exists(img_path):
                    image_paths.append(img_path)
                    labels.append(label)
    
    # 使用之前创建的 add_images_to_lmdb 函数
    add_images_to_lmdb(lmdb_path, image_paths, labels)
```

## 四、注意事项

### 1. 数据格式要求

- **图像格式**: JPG, PNG 等常见格式
- **标签格式**: UTF-8 编码的文本字符串
- **图像尺寸**: 建议预处理为合适的大小（HR: 128×32, LR: 64×16）

### 2. 备份数据

在修改 LMDB 之前，**务必备份**：

```bash
# 备份整个数据集目录
cp -r dataset/mydata/train1 dataset/mydata/train1_backup
```

### 3. 验证数据

添加后验证数据：

```bash
source .venv37/bin/activate
python check_dataset.py
```

### 4. 更新样本数

添加新数据后，`num-samples` 会自动更新，但建议验证：

```python
import lmdb
env = lmdb.open('./dataset/mydata/train1', readonly=True)
with env.begin() as txn:
    num = int(txn.get(b'num-samples'))
    print(f"总样本数: {num}")
env.close()
```

## 五、推荐工作流程

1. **准备新图片和标签**
   ```
   new_images/
   ├── images/
   └── labels.txt
   ```

2. **创建新的 LMDB 数据集**（使用 train3）
   ```python
   from dataset.create_lmdb import createDataset
   createDataset('./dataset/mydata/train3', image_paths, labels)
   ```

3. **更新配置文件**
   ```yaml
   train_data_dir: [
       './dataset/mydata/train1',
       './dataset/mydata/train2',
       './dataset/mydata/train3',  # 新数据集
   ]
   ```

4. **验证数据集**
   ```bash
   python check_dataset.py
   ```

5. **开始训练**

这种方式最安全，不会影响原有数据。

