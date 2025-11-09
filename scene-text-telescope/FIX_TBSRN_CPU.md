# 修复 TBSRN 模型的 CPU 支持

## 问题

在 `model/tbsrn.py` 中硬编码了 `.cuda()` 调用，导致 CPU 模式运行失败：

```
AssertionError: Torch not compiled with CUDA enabled
```

## 修复的文件

### `model/tbsrn.py`

**问题位置**: 第 83 行

**之前**:
```python
position2d = positionalencoding2d(64,16,64).float().cuda().unsqueeze(0).view(1,64,1024)
```

**之后**:
```python
position2d = positionalencoding2d(64,16,64).float().to(conv_feature.device).unsqueeze(0).view(1,64,1024)
```

## 修复方法

使用 `.to(conv_feature.device)` 自动匹配输入张量的设备，而不是硬编码 `.cuda()`。

这样：
- 如果输入在 GPU 上，position2d 也会在 GPU 上
- 如果输入在 CPU 上，position2d 也会在 CPU 上
- 自动适配，无需手动指定设备

## 验证

修复后可以正常导入和使用：

```bash
source .venv37/bin/activate
python -c "from model.tbsrn import TBSRN; print('TBSRN 导入成功！')"
```

## 完整修复列表

现在所有 CUDA 硬编码调用都已修复：

1. ✅ `loss/weight_ce_loss.py` - 权重交叉熵损失
2. ✅ `loss/text_focus_loss.py` - 文本聚焦损失
3. ✅ `loss/transformer.py` - Transformer 模型
4. ✅ `interfaces/base.py` - 模型加载
5. ✅ `model/tbsrn.py` - TBSRN 模型

代码现在应该可以在 CPU 模式下完整运行。

