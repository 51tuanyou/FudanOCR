#!/bin/bash
# Scene Text Telescope 训练示例脚本
# 
# 使用方法:
#   bash train_example.sh
#   或
#   chmod +x train_example.sh && ./train_example.sh

# ============================================
# 选择训练模式：GPU 或 CPU
# ============================================

# GPU训练（推荐，速度快）
# 单GPU: CUDA_VISIBLE_DEVICES=0
# 多GPU: CUDA_VISIBLE_DEVICES=0,1,2,3
export CUDA_VISIBLE_DEVICES=0
BATCH_SIZE=16

# CPU训练（不推荐，速度很慢）
# 取消下面的注释以使用CPU训练
# unset CUDA_VISIBLE_DEVICES
# BATCH_SIZE=1

# 设置实验名称（必需，用于保存checkpoint）
EXP_NAME="my_training_$(date +%Y%m%d_%H%M%S)"

# 基础训练命令
python main.py \
    --batch_size=${BATCH_SIZE} \
    --STN \
    --exp_name ${EXP_NAME} \
    --text_focus \
    --arch tbsrn

# 如果需要从检查点恢复训练，取消下面的注释并修改路径
# python main.py \
#     --batch_size=16 \
#     --STN \
#     --exp_name ${EXP_NAME} \
#     --text_focus \
#     --arch tbsrn \
#     --resume checkpoint/${EXP_NAME}/checkpoint.pth

# 训练完成后，模型会保存在:
# checkpoint/${EXP_NAME}/model_best.pth

echo "训练完成！模型保存在: checkpoint/${EXP_NAME}/model_best.pth"

