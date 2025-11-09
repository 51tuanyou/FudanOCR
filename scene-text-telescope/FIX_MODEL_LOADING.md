# 修复模型加载的 CPU 支持

## 问题

在 CPU 模式下加载 GPU 训练的模型时出错：

```
RuntimeError: Attempting to deserialize object on a CUDA device but torch.cuda.is_available() is False. 
If you are running on a CPU-only machine, please use torch.load with map_location=torch.device('cpu') to map your storages to the CPU.
```

## 修复的文件

### `interfaces/base.py`

修复了所有 `torch.load` 调用，添加 `map_location=self.device` 参数：

1. **`generator_init` 方法** (第 184, 187 行)
   - 修复超分辨率模型加载
   - 支持单 GPU 和多 GPU 模式

2. **`MORAN_init` 方法** (第 281 行)
   - 修复 MORAN 识别器模型加载

3. **`CRNN_init` 方法** (第 316 行)
   - 修复 CRNN 识别器模型加载

4. **`Aster_init` 方法** (第 333 行)
   - 修复 ASTER 识别器模型加载

## 修复方法

### 之前
```python
model.load_state_dict(torch.load(model_path)['state_dict_G'])
```

### 之后
```python
model.load_state_dict(torch.load(model_path, map_location=self.device)['state_dict_G'])
```

## 工作原理

- `self.device` 在 `TextBase.__init__` 中自动检测：
  ```python
  self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
  ```
- `map_location=self.device` 会将模型权重映射到正确的设备（CPU 或 GPU）
- 这样无论模型是在 GPU 还是 CPU 上训练的，都能正确加载

## 验证

修复后可以正常加载模型：

```bash
source .venv37/bin/activate
python main.py --batch_size=1 --STN --exp_name demo --text_focus --demo --demo_dir ./demo --resume checkpoint/model_best.pth
```

## 注意事项

1. **模型兼容性**: 修复后的代码可以加载 GPU 训练的模型到 CPU，反之亦然
2. **性能**: CPU 模式加载和运行会较慢，但功能正常
3. **设备一致性**: 所有模型和权重都会自动映射到 `self.device`

