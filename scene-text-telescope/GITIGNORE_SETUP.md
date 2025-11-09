# .gitignore 设置说明

## 已排除的文件类型

### 1. 模型权重文件
- `*.pth` - PyTorch 模型权重
- `*.pt` - PyTorch 模型
- `*.ckpt` - Checkpoint 文件
- `*.pkl` - Pickle 文件（如 confuse.pkl）
- `*.h5`, `*.hdf5` - HDF5 格式
- `*.pb` - Protocol Buffer
- `*.onnx` - ONNX 模型
- `*.tflite` - TensorFlow Lite

### 2. Checkpoint 目录
- `checkpoint/` - 包含所有训练模型、日志、TensorBoard 文件

### 3. 数据集文件
- `dataset/mydata/train*/` - 训练数据集（LMDB）
- `dataset/mydata/test*/` - 测试数据集
- `dataset/mydata/*.pth` - 数据集中的模型权重
- `dataset/mydata/*.pkl` - 数据集中的 Pickle 文件
- `*.mdb` - LMDB 数据库文件
- `*.lock` - LMDB 锁文件

### 4. 结果和样本
- `demo_results/` - Demo 运行结果
- `extracted_samples/` - 提取的样本

### 5. Python 相关
- `__pycache__/` - Python 缓存
- `*.pyc`, `*.pyo` - 编译的 Python 文件
- `.venv/`, `.venv37/` - 虚拟环境

### 6. 日志和临时文件
- `*.log` - 日志文件
- `*.tmp`, `*.temp` - 临时文件
- `events.out.tfevents.*` - TensorBoard 日志

## 如果文件已经被 Git 跟踪

如果某些大文件已经被 Git 跟踪，需要先从 Git 中移除（但保留本地文件）：

```bash
# 移除已跟踪的大文件
git rm --cached checkpoint/model_best.pth
git rm --cached dataset/mydata/crnn.pth
git rm --cached dataset/mydata/pretrain_transformer.pth
git rm --cached dataset/mydata/train1/data.mdb
git rm --cached dataset/mydata/train1/lock.mdb
git rm --cached dataset/mydata/train2/data.mdb
git rm --cached dataset/mydata/train2/lock.mdb

# 或者移除整个目录
git rm -r --cached checkpoint/
git rm -r --cached dataset/mydata/train*/
git rm -r --cached dataset/mydata/test*/

# 提交更改
git add .gitignore
git commit -m "Add .gitignore to exclude large model files and datasets"
```

## 检查哪些文件会被忽略

```bash
# 检查特定文件是否被忽略
git check-ignore -v checkpoint/model_best.pth

# 查看所有被忽略的文件
git status --ignored
```

## 保留的文件

以下文件/目录会被保留（不会被忽略）：
- `image/` - 示例图片
- `samples/` - 样本文件
- `document/*.pdf` - 文档（如果需要）
- 所有源代码文件（`.py`）
- 配置文件（`.yaml`, `.txt`）
- 文档文件（`.md`）

## 注意事项

1. **模型权重**: 不要提交到 Git，文件太大
2. **数据集**: LMDB 数据集文件很大，应该排除
3. **Checkpoint**: 训练过程中的 checkpoint 文件很大
4. **虚拟环境**: 不要提交虚拟环境目录

## 推荐做法

1. 在 README 中说明如何下载模型权重
2. 使用 Git LFS（如果必须跟踪大文件）
3. 将模型权重放在云存储（如 Google Drive, Baidu Netdisk）
4. 在文档中提供下载链接

