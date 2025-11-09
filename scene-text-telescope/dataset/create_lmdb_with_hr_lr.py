#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建包含 HR 和 LR 版本的 LMDB 数据集
这是 createDataset 的增强版，会自动生成 HR (128×32) 和 LR (64×16) 版本
"""
import os
import lmdb
import cv2
import numpy as np
from PIL import Image
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

def writeCache(env, cache):
    """写入缓存到 LMDB"""
    with env.begin(write=True) as txn:
        for k, v in cache.items():
            if type(k) is not bytes:
                k = k.encode()
            txn.put(k, v)

def createDataset_with_hr_lr(outputPath, imagePathList, labelList, 
                             hr_size=(128, 32), lr_size=(64, 16), 
                             checkValid=True):
    """
    创建包含 HR 和 LR 版本的 LMDB 数据集
    
    Args:
        outputPath: LMDB 输出路径
        imagePathList: 图片路径列表
        labelList: 标签列表
        hr_size: HR 图像尺寸，默认 (128, 32)
        lr_size: LR 图像尺寸，默认 (64, 16)
        checkValid: 是否检查图像有效性
    """
    assert (len(imagePathList) == len(labelList))
    nSamples = len(imagePathList)
    
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
    
    env = lmdb.open(outputPath, map_size=1099511627776)
    cache = {}
    cnt = 1
    
    print(f"开始创建数据集，共 {nSamples} 个样本")
    print(f"HR 尺寸: {hr_size[0]}×{hr_size[1]}")
    print(f"LR 尺寸: {lr_size[0]}×{lr_size[1]}")
    
    for i in range(nSamples):
        imagePath = imagePathList[i]
        label = labelList[i]
        
        if len(label) == 0:
            continue
        if not os.path.exists(imagePath):
            print(f'警告: 图片不存在 {imagePath}')
            continue
        
        # 读取图像
        try:
            with open(imagePath, 'rb') as f:
                imageBin = f.read()
        except Exception as e:
            print(f'警告: 无法读取 {imagePath}: {e}')
            continue
        
        # 检查图像有效性
        if checkValid:
            if not checkImageIsValid(imageBin):
                print(f'警告: 无效图像 {imagePath}')
                continue
        
        # 处理图像，生成 HR 和 LR 版本
        try:
            img = Image.open(io.BytesIO(imageBin))
            
            # 生成 HR 版本
            img_hr = img.resize(hr_size, Image.BICUBIC)
            hr_buf = io.BytesIO()
            img_hr.save(hr_buf, format='PNG')
            hr_data = hr_buf.getvalue()
            
            # 生成 LR 版本
            img_lr = img.resize(lr_size, Image.BICUBIC)
            lr_buf = io.BytesIO()
            img_lr.save(lr_buf, format='PNG')
            lr_data = lr_buf.getvalue()
            
            # 保存到缓存
            hr_key = f'image_hr-{cnt:09d}'
            lr_key = f'image_lr-{cnt:09d}'
            label_key = f'label-{cnt:09d}'
            
            cache[hr_key] = hr_data
            cache[lr_key] = lr_data
            cache[label_key] = label.encode()
            
            # 每1000个样本写入一次
            if cnt % 1000 == 0:
                writeCache(env, cache)
                cache = {}
                print(f'已处理 {cnt} / {nSamples} 个样本')
            
            cnt += 1
            
        except Exception as e:
            print(f'警告: 处理图像失败 {imagePath}: {e}')
            continue
    
    # 写入剩余数据
    nSamples = cnt - 1
    cache['num-samples'] = str(nSamples).encode()
    writeCache(env, cache)
    env.close()
    
    print(f'完成! 创建了包含 {nSamples} 个样本的数据集')
    print(f'数据集路径: {outputPath}')

if __name__ == '__main__':
    # 使用示例
    image_paths = [
        './new_images/sample1.jpg',
        './new_images/sample2.jpg',
    ]
    labels = [
        'HELLO',
        'WORLD',
    ]
    
    createDataset_with_hr_lr(
        './dataset/mydata/train3',
        image_paths,
        labels
    )

