# Demo 结果位置说明

## 结果输出位置

### 1. 日志文件（主要结果）

**位置**: `checkpoint/{exp_name}/log.txt`

根据你的命令：
```bash
python main.py --batch_size=1 --STN --exp_name demo --text_focus --demo --demo_dir ./demo --resume checkpoint/model_best.pth
```

**结果文件**: `checkpoint/demo/log.txt`

### 2. 结果内容

日志文件包含：
- **识别结果**: 每张图片的识别文本
  - 格式: `{LR识别结果} ===> {SR识别结果}`
  - 例如: `hello ===> hello`
- **性能统计**: FPS（每秒处理帧数）
- **处理信息**: 时间戳、参数等

### 3. 查看结果

```bash
# 查看完整日志
cat checkpoint/demo/log.txt

# 查看最后几行（识别结果）
tail -20 checkpoint/demo/log.txt

# 实时查看（如果正在运行）
tail -f checkpoint/demo/log.txt
```

### 4. 结果格式示例

```
[12:34:56.789] hello ===> hello
[12:34:57.123] world ===> world
[12:34:58.456] fps=2.5
```

## 注意事项

1. **没有保存图像**: Demo 函数只输出识别文本，不保存超分辨率后的图像
2. **日志同时输出到控制台和文件**: 结果会同时显示在终端和日志文件中
3. **如果目录不存在**: 运行 demo 时会自动创建 `checkpoint/demo/` 目录

## 如果需要保存图像结果

如果需要保存超分辨率后的图像，可以修改 demo 函数，添加图像保存功能。

