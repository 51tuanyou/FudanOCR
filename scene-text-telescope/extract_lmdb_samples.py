#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从 LMDB 数据集中提取样本并保存为图片

用法: python extract_lmdb_samples.py <lmdb_path> <output_dir> [num_samples]
"""
import lmdb
from PIL import Image
import io
import os
import sys

def extract_samples(lmdb_path, output_dir, num_samples=10):
    """从 LMDB 中提取样本并保存为图片"""
    env = lmdb.open(lmdb_path, readonly=True, lock=False)
    os.makedirs(output_dir, exist_ok=True)
    
    with env.begin() as txn:
        num_total = int(txn.get(b'num-samples'))
        num_extract = min(num_samples, num_total)
        
        print(f"总样本数: {num_total}")
        print(f"提取前 {num_extract} 个样本到 {output_dir}\n")
        
        for i in range(1, num_extract + 1):
            # 读取标签
            label_key = f'label-{i:09d}'.encode()
            label = txn.get(label_key)
            label_str = label.decode() if label else f'sample_{i}'
            
            # 清理标签中的特殊字符（用于文件名）
            safe_label = "".join(c for c in label_str if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_label = safe_label.replace(' ', '_')[:50]  # 限制长度
            
            # 提取高分辨率图像
            hr_key = f'image_hr-{i:09d}'.encode()
            hr_data = txn.get(hr_key)
            if hr_data:
                img_hr = Image.open(io.BytesIO(hr_data))
                hr_path = os.path.join(output_dir, f'{i:09d}_hr_{safe_label}.png')
                img_hr.save(hr_path)
                print(f"样本 {i}: {label_str}")
                print(f"  HR: {hr_path} ({img_hr.size[0]}x{img_hr.size[1]})")
            
            # 提取低分辨率图像
            lr_key = f'image_lr-{i:09d}'.encode()
            lr_data = txn.get(lr_key)
            if lr_data:
                img_lr = Image.open(io.BytesIO(lr_data))
                lr_path = os.path.join(output_dir, f'{i:09d}_lr_{safe_label}.png')
                img_lr.save(lr_path)
                print(f"  LR: {lr_path} ({img_lr.size[0]}x{img_lr.size[1]})")
            
            # 如果没有 HR/LR，尝试读取单张图像
            if not hr_data:
                img_key = f'image-{i:09d}'.encode()
                img_data = txn.get(img_key)
                if img_data:
                    img = Image.open(io.BytesIO(img_data))
                    img_path = os.path.join(output_dir, f'{i:09d}_{safe_label}.png')
                    img.save(img_path)
                    print(f"  图像: {img_path} ({img.size[0]}x{img.size[1]})")
            
            print()
    
    env.close()
    print(f"完成! 已提取 {num_extract} 个样本到 {output_dir}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python extract_lmdb_samples.py <lmdb_path> <output_dir> [num_samples]")
        print("示例: python extract_lmdb_samples.py dataset/mydata/train1 ./extracted_samples 10")
        sys.exit(1)
    
    lmdb_path = sys.argv[1]
    output_dir = sys.argv[2]
    num_samples = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    
    extract_samples(lmdb_path, output_dir, num_samples)

