#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查看 LMDB 数据集内容
用法: python view_lmdb.py <lmdb_path> [max_samples]
"""
import lmdb
from PIL import Image
import io
import sys

def view_lmdb(lmdb_path, max_samples=5):
    """查看 LMDB 数据集的前几个样本"""
    env = lmdb.open(lmdb_path, readonly=True, lock=False)
    
    with env.begin() as txn:
        # 获取样本数
        num_samples = int(txn.get(b'num-samples'))
        print(f"总样本数: {num_samples}")
        print(f"显示前 {min(max_samples, num_samples)} 个样本:\n")
        
        # 查看前几个样本
        for i in range(1, min(max_samples + 1, num_samples + 1)):
            print(f"样本 {i}:")
            
            # 尝试读取高分辨率图像
            hr_key = f'image_hr-{i:09d}'.encode()
            lr_key = f'image_lr-{i:09d}'.encode()
            label_key = f'label-{i:09d}'.encode()
            
            # 读取标签
            label = txn.get(label_key)
            if label:
                print(f"  标签: {label.decode()}")
            
            # 读取图像
            hr_data = txn.get(hr_key)
            lr_data = txn.get(lr_key)
            
            if hr_data:
                print(f"  高分辨率图像: {len(hr_data)} bytes")
            if lr_data:
                print(f"  低分辨率图像: {len(lr_data)} bytes")
            
            # 如果没有 HR/LR，尝试读取单张图像
            if not hr_data:
                img_key = f'image-{i:09d}'.encode()
                img_data = txn.get(img_key)
                if img_data:
                    print(f"  图像: {len(img_data)} bytes")
            
            print()
    
    env.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python view_lmdb.py <lmdb_path> [max_samples]")
        print("示例: python view_lmdb.py dataset/mydata/train1 10")
        sys.exit(1)
    
    lmdb_path = sys.argv[1]
    max_samples = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    view_lmdb(lmdb_path, max_samples)

