# Demo 结果说明

## 结果位置

运行 demo 后，所有结果会保存在：

```
checkpoint/{exp_name}/demo_results/
```

例如，如果你使用 `--exp_name demo`，结果在：
```
checkpoint/demo/demo_results/
```

## 结果内容

### 1. 超分辨率图像

**位置**: `checkpoint/demo/demo_results/sr_*.jpg` (或 .png)

- 每张输入图片都会生成对应的超分辨率版本
- 文件名格式: `sr_原文件名`
- 例如: `sr_test.jpg` 是 `test.jpg` 的超分辨率版本

### 2. 低分辨率图像（对比用）

**位置**: `checkpoint/demo/demo_results/lr_*.jpg`

- 保存处理后的低分辨率图像，用于对比
- 文件名格式: `lr_原文件名`

### 3. 结果摘要文件

**位置**: `checkpoint/demo/demo_results/summary.txt`

包含：
- 处理统计信息（图片数、速度、耗时）
- 每张图片的详细识别结果
  - 低分辨率识别结果
  - 超分辨率识别结果

### 4. 日志文件

**位置**: `checkpoint/demo/log.txt`

包含完整的运行日志和识别结果。

## 查看结果

### 方式 1: 查看结果摘要

```bash
cat checkpoint/demo/demo_results/summary.txt
```

### 方式 2: 查看图像结果

```bash
# 查看所有结果图像
ls -lh checkpoint/demo/demo_results/

# 使用图片查看器打开
open checkpoint/demo/demo_results/sr_test.jpg
```

### 方式 3: 查看日志

```bash
# 查看完整日志
cat checkpoint/demo/log.txt

# 查看最后几行
tail -20 checkpoint/demo/log.txt
```

## 结果示例

### 控制台输出

```
test.jpg:
  低分辨率识别: hello
  超分辨率识别: hello

============================================================
处理完成！
处理图片数: 1
处理速度: 0.50 fps
结果保存目录: checkpoint/demo/demo_results
结果摘要文件: checkpoint/demo/demo_results/summary.txt
============================================================
```

### summary.txt 内容示例

```
============================================================
Demo 识别结果摘要
============================================================

处理图片数: 1
处理速度: 0.50 fps
总耗时: 2.00 秒

------------------------------------------------------------
详细结果:
------------------------------------------------------------

图片: test.jpg
  低分辨率识别: hello
  超分辨率识别: hello
```

## 结果文件结构

```
checkpoint/demo/
├── demo_results/
│   ├── sr_test.jpg          # 超分辨率图像
│   ├── lr_test.jpg          # 低分辨率图像（对比）
│   └── summary.txt           # 结果摘要
├── log.txt                   # 完整日志
└── events.out.tfevents.*     # TensorBoard 日志
```

## 注意事项

1. **图像保存**: 所有处理后的图像都会自动保存
2. **结果对比**: 可以对比 `lr_` 和 `sr_` 图像查看超分辨率效果
3. **识别文本**: 在 `summary.txt` 和 `log.txt` 中都有记录
4. **自动创建**: 结果目录会自动创建，无需手动创建

## 如果看不到结果

1. **检查是否运行完成**: 确保 demo 命令执行完成
2. **检查目录**: `ls -la checkpoint/demo/demo_results/`
3. **检查日志**: `cat checkpoint/demo/log.txt` 查看是否有错误
4. **重新运行**: 如果目录不存在，重新运行 demo 命令

