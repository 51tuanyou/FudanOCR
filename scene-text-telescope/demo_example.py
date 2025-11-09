#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Scene Text Telescope 图片识别示例脚本

这个脚本提供了一个简单的接口来使用 scene-text-telescope 进行图片识别。

使用方法:
    python demo_example.py --image_path path/to/your/image.jpg
    或者
    python demo_example.py --demo_dir path/to/your/images/directory
"""

import os
import sys
import argparse
import yaml
from easydict import EasyDict
from interfaces.super_resolution import TextSR


def main():
    parser = argparse.ArgumentParser(description='Scene Text Telescope 图片识别示例')
    
    # 基本参数
    parser.add_argument('--image_path', type=str, default='', 
                       help='单张图片路径')
    parser.add_argument('--demo_dir', type=str, default='./demo', 
                       help='图片目录路径（用于批量处理）')
    parser.add_argument('--exp_name', type=str, default='demo_example',
                       help='实验名称')
    parser.add_argument('--resume', type=str, default='',
                       help='模型权重路径（如果使用预训练模型）')
    parser.add_argument('--arch', default='tbsrn', 
                       choices=['tbsrn', 'tsrn', 'bicubic', 'srcnn', 'vdsr', 'srres', 'esrgan', 'rdn', 'edsr', 'lapsrn'],
                       help='使用的模型架构')
    parser.add_argument('--text_focus', action='store_true', default=True,
                       help='启用文本聚焦模式')
    parser.add_argument('--STN', action='store_true', default=True,
                       help='使用空间变换网络')
    parser.add_argument('--batch_size', type=int, default=1,
                       help='批次大小')
    parser.add_argument('--rec', default='crnn', choices=['crnn'],
                       help='识别器类型')
    
    args = parser.parse_args()
    
    # 如果指定了单张图片，创建临时目录并复制图片
    if args.image_path:
        if not os.path.exists(args.image_path):
            print(f"错误: 图片文件不存在: {args.image_path}")
            sys.exit(1)
        
        # 创建临时demo目录
        temp_demo_dir = './demo_temp'
        os.makedirs(temp_demo_dir, exist_ok=True)
        
        # 复制图片到demo目录
        import shutil
        image_name = os.path.basename(args.image_path)
        dest_path = os.path.join(temp_demo_dir, image_name)
        shutil.copy(args.image_path, dest_path)
        
        args.demo_dir = temp_demo_dir
        args.demo = True
        print(f"已将图片复制到临时目录: {dest_path}")
    
    # 检查demo目录是否存在
    if not os.path.exists(args.demo_dir):
        print(f"错误: demo目录不存在: {args.demo_dir}")
        print("请创建该目录并放入要识别的图片，或使用 --image_path 指定单张图片")
        sys.exit(1)
    
    # 检查demo目录中是否有图片
    image_files = [f for f in os.listdir(args.demo_dir) 
                   if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
    if not image_files:
        print(f"错误: demo目录中没有找到图片文件: {args.demo_dir}")
        sys.exit(1)
    
    print(f"找到 {len(image_files)} 张图片")
    print(f"使用模型架构: {args.arch}")
    print(f"文本聚焦模式: {'开启' if args.text_focus else '关闭'}")
    
    # 检查是否使用CPU
    import torch
    if torch.cuda.is_available():
        print(f"使用设备: GPU (CUDA)")
    else:
        print(f"使用设备: CPU (注意：CPU模式速度较慢)")
    
    if args.resume:
        print(f"加载模型权重: {args.resume}")
    else:
        print("注意: 未指定模型权重路径，将使用默认配置")
    
    # 加载配置
    config_path = os.path.join('config', 'super_resolution.yaml')
    if not os.path.exists(config_path):
        print(f"错误: 配置文件不存在: {config_path}")
        sys.exit(1)
    
    config = yaml.load(open(config_path, 'r'), Loader=yaml.Loader)
    config = EasyDict(config)
    
    # 设置demo模式
    args.demo = True
    
    # 创建TextSR实例并运行demo
    try:
        mission = TextSR(config, args)
        print("\n开始处理图片...")
        mission.demo()
        print("\n处理完成！")
        
        # 如果使用了临时目录，询问是否删除
        if args.image_path and os.path.exists('./demo_temp'):
            print("\n提示: 临时目录 './demo_temp' 已创建，可以手动删除")
            
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

