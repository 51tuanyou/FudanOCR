# 修复 Protobuf 版本兼容性错误

## 错误信息

```
TypeError: Descriptors cannot not be created directly.
If this call came from a _pb2.py file, your generated code is out of date and must be regenerated with protoc >= 3.19.0.
If you cannot immediately regenerate your protos, some other possible workarounds are:
 1. Downgrade the protobuf package to 3.20.x or lower.
 2. Set PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
```

## 问题原因

- **protobuf 版本**: 4.24.4（太新）
- **tensorboard 版本**: 2.5.0（旧版本）
- **不兼容**: protobuf 4.x 与 tensorboard 2.5.0 不兼容

## 解决方案

### 方案 1: 降级 protobuf（推荐）

```bash
source .venv37/bin/activate
uv pip install "protobuf<=3.20.0"
```

或使用 pip：
```bash
pip install "protobuf<=3.20.0"
```

### 方案 2: 设置环境变量（临时解决）

```bash
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
python main.py --batch_size=1 --STN --exp_name demo --text_focus --demo --demo_dir ./demo --resume checkpoint/model_best.pth
```

**注意**: 这会使 protobuf 使用纯 Python 实现，速度较慢。

### 方案 3: 更新 requirement.txt

在 `requirement.txt` 中添加 protobuf 版本限制：

```
protobuf<=3.20.0
```

## 验证修复

修复后验证：

```bash
source .venv37/bin/activate
uv pip list | grep protobuf
# 应该显示: protobuf 3.20.x 或更低

# 测试运行
python main.py --batch_size=1 --STN --exp_name demo --text_focus --demo --demo_dir ./demo --resume checkpoint/model_best.pth
```

## 兼容版本参考

| TensorBoard 版本 | 兼容的 Protobuf 版本 |
|-----------------|---------------------|
| 2.5.0 | <= 3.20.0 |
| 2.6.0+ | <= 3.20.0 或 4.x（需更新 tensorboard） |

## 推荐操作

1. **立即修复**：降级 protobuf
   ```bash
   uv pip install "protobuf<=3.20.0"
   ```

2. **长期解决**：更新 requirement.txt
   ```bash
   echo "protobuf<=3.20.0" >> requirement.txt
   ```

3. **验证**：运行 demo 命令测试

