# 修复 CPU 模式支持

## 问题

代码中硬编码了 `.cuda()` 调用，导致在 CPU 模式下运行失败：

```
AssertionError: Torch not compiled with CUDA enabled
```

## 修复的文件

### 1. `loss/weight_ce_loss.py`
- **问题**: 第 23 行使用 `.cuda()`
- **修复**: 改为 `.to(device)`，自动检测设备

### 2. `loss/text_focus_loss.py`
- **问题**: 多处使用 `.cuda()`
  - 第 56 行: `Transformer().cuda()`
  - 第 66 行: `torch.Tensor(length).long().cuda()`
  - 第 78 行: `torch.Tensor(text_gt).long().cuda()`
  - 第 80 行: `torch.from_numpy(input_tensor).long().cuda()`
- **修复**: 全部改为 `.to(device)`，并添加 `map_location=device` 用于模型加载

### 3. `loss/transformer.py`
- **问题**: 多处使用 `.cuda()`
  - 第 292 行: `subsequent_mask(text_max_length).cuda()`
  - 第 369 行: `torch.zeros(text_embedding.shape).cuda().cuda()`
- **修复**: 
  - 使用 `.to(text.device)` 或 `.to(text_embedding.device)` 自动匹配输入张量的设备

## 修复方法

### 自动设备检测

在每个文件中添加设备检测：

```python
# 自动检测设备（支持 CPU 和 GPU）
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
```

### 替换硬编码的 .cuda()

**之前**:
```python
tensor = torch.Tensor(data).cuda()
```

**之后**:
```python
tensor = torch.Tensor(data).to(device)
# 或者，如果已有张量，使用其设备：
tensor = torch.Tensor(data).to(input_tensor.device)
```

### 模型加载

**之前**:
```python
model.load_state_dict(torch.load('model.pth'))
```

**之后**:
```python
model.load_state_dict(torch.load('model.pth', map_location=device))
```

## 验证

修复后可以正常运行：

```bash
source .venv37/bin/activate
python main.py --batch_size=1 --STN --exp_name demo --text_focus --demo --demo_dir ./demo --resume checkpoint/model_best.pth
```

## 注意事项

1. **性能**: CPU 模式会比 GPU 慢很多，但可以正常运行
2. **兼容性**: 修复后的代码同时支持 CPU 和 GPU
3. **设备匹配**: 使用 `.to(tensor.device)` 确保张量在同一设备上

## 相关文件

- `loss/weight_ce_loss.py` - 权重交叉熵损失
- `loss/text_focus_loss.py` - 文本聚焦损失
- `loss/transformer.py` - Transformer 模型

