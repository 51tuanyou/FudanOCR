#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
添加新图片到现有的 LMDB 数据集

用法:
    python add_images_to_lmdb.py <lmdb_path> <image_list.txt>
    
image_list.txt 格式:
    /path/to/image1.jpg label1
    /path/to/image2.jpg label2
    ...
"""
import os
import sys
import lmdb
import cv2
from PIL import Image
import numpy as np
import io

def checkImageIsValid(imageBin):
    """检查图像是否有效"""
    if imageBin is None:
        return False
    try:
        imageBuf = np.fromstring(imageBin, dtype=np.uint8)
        img = cv2.imdecode(imageBuf, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return False
        imgH, imgW = img.shape[0], img.shape[1]
        if imgH * imgW == 0:
            return False
        return True
    except:
        return False

def add_images_to_lmdb(lmdb_path, image_paths, labels):
    """
    添加新图片到现有的 LMDB 数据集
    
    Args:
        lmdb_path: LMDB 数据集路径
        image_paths: 新图片路径列表
        labels: 对应的标签列表
    """
    assert len(image_paths) == len(labels), "图片和标签数量必须一致"
    
    # 打开现有数据库（写入模式）
    env = lmdb.open(lmdb_path, map_size=1099511627776)
    
    # 获取当前样本数
    with env.begin() as txn:
        num_samples = int(txn.get(b'num-samples'))
        print(f"当前样本数: {num_samples}")
    
    # 添加新样本
    new_count = 0
    failed_count = 0
    
    for i, (img_path, label) in enumerate(zip(image_paths, labels)):
        if not os.path.exists(img_path):
            print(f"警告: 图片不存在 {img_path}")
            failed_count += 1
            continue
        
        # 读取图像
        try:
            with open(img_path, 'rb') as f:
                imageBin = f.read()
        except Exception as e:
            print(f"警告: 无法读取 {img_path}: {e}")
            failed_count += 1
            continue
        
        # 检查图像有效性
        if not checkImageIsValid(imageBin):
            print(f"警告: 无效图像 {img_path}")
            failed_count += 1
            continue
        
        # 创建 HR 和 LR 版本
        try:
            img = Image.open(io.BytesIO(imageBin))
            
            # 高分辨率: 128x32
            img_hr = img.resize((128, 32), Image.BICUBIC)
            hr_buf = io.BytesIO()
            img_hr.save(hr_buf, format='PNG')
            hr_data = hr_buf.getvalue()
            
            # 低分辨率: 64x16
            img_lr = img.resize((64, 16), Image.BICUBIC)
            lr_buf = io.BytesIO()
            img_lr.save(lr_buf, format='PNG')
            lr_data = lr_buf.getvalue()
            
            # 写入数据
            new_idx = num_samples + new_count + 1
            with env.begin(write=True) as txn:
                hr_key = f'image_hr-{new_idx:09d}'.encode()
                lr_key = f'image_lr-{new_idx:09d}'.encode()
                label_key = f'label-{new_idx:09d}'.encode()
                
                txn.put(hr_key, hr_data)
                txn.put(lr_key, lr_data)
                txn.put(label_key, label.encode())
            
            new_count += 1
            if (i + 1) % 100 == 0:
                print(f"已处理 {i + 1}/{len(image_paths)} 个图片...")
        
        except Exception as e:
            print(f"警告: 处理图像失败 {img_path}: {e}")
            failed_count += 1
            continue
    
    # 更新样本总数
    if new_count > 0:
        with env.begin(write=True) as txn:
            new_total = num_samples + new_count
            txn.put(b'num-samples', str(new_total).encode())
    
    env.close()
    
    print(f"\n完成!")
    print(f"成功添加: {new_count} 个样本")
    print(f"失败: {failed_count} 个")
    print(f"总样本数: {num_samples} -> {num_samples + new_count}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python add_images_to_lmdb.py <lmdb_path> <image_list.txt>")
        print("\nimage_list.txt 格式:")
        print("  /path/to/image1.jpg label1")
        print("  /path/to/image2.jpg label2")
        print("  ...")
        sys.exit(1)
    
    lmdb_path = sys.argv[1]
    list_file = sys.argv[2]
    
    # 读取图片和标签
    image_paths = []
    labels = []
    
    if not os.path.exists(list_file):
        print(f"错误: 文件不存在 {list_file}")
        sys.exit(1)
    
    with open(list_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split(' ', 1)
            if len(parts) == 2:
                img_path, label = parts
                if os.path.exists(img_path):
                    image_paths.append(img_path)
                    labels.append(label)
                else:
                    print(f"警告 (行 {line_num}): 图片不存在 {img_path}")
            else:
                print(f"警告 (行 {line_num}): 格式错误，应为 '路径 标签'")
    
    if len(image_paths) == 0:
        print("错误: 没有找到有效的图片")
        sys.exit(1)
    
    print(f"准备添加 {len(image_paths)} 个样本到 {lmdb_path}")
    add_images_to_lmdb(lmdb_path, image_paths, labels)

