#!/bin/bash
# Scene Text Telescope CPU训练示例脚本
# 
# 注意：CPU训练速度非常慢，仅用于测试或小规模实验
# 强烈建议使用GPU训练
# 
# 使用方法:
#   bash train_cpu_example.sh
#   或
#   chmod +x train_cpu_example.sh && ./train_cpu_example.sh

# 禁用GPU，强制使用CPU
unset CUDA_VISIBLE_DEVICES

# 设置实验名称（必需，用于保存checkpoint）
EXP_NAME="cpu_training_$(date +%Y%m%d_%H%M%S)"

echo "=========================================="
echo "开始CPU训练（速度会很慢）"
echo "实验名称: ${EXP_NAME}"
echo "批次大小: 1 (CPU训练建议使用小批次)"
echo "=========================================="

# CPU训练命令 - 使用很小的批次大小
python main.py \
    --batch_size=1 \
    --STN \
    --exp_name ${EXP_NAME} \
    --text_focus \
    --arch tbsrn

# 如果需要从检查点恢复训练，取消下面的注释并修改路径
# python main.py \
#     --batch_size=1 \
#     --STN \
#     --exp_name ${EXP_NAME} \
#     --text_focus \
#     --arch tbsrn \
#     --resume checkpoint/${EXP_NAME}/checkpoint.pth

echo "=========================================="
echo "训练完成！模型保存在: checkpoint/${EXP_NAME}/model_best.pth"
echo "注意：CPU训练速度很慢，建议使用GPU训练以获得更好的性能"
echo "=========================================="

