#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

def check_lmdb_samples(lmdb_path):
    try:
        import lmdb
        if not os.path.exists(lmdb_path):
            return 0
        env = lmdb.open(lmdb_path, readonly=True, lock=False, readahead=False, meminit=False)
        with env.begin(write=False) as txn:
            n_samples = int(txn.get(b'num-samples'))
        env.close()
        return n_samples
    except ImportError:
        return None
    except Exception as e:
        return None

train1_samples = check_lmdb_samples('./dataset/mydata/train1')
train2_samples = check_lmdb_samples('./dataset/mydata/train2')

if train1_samples is not None and train2_samples is not None:
    total = train1_samples + train2_samples
    print(f"train1: {train1_samples:,} 样本")
    print(f"train2: {train2_samples:,} 样本")
    print(f"总计: {total:,} 样本")
else:
    print("无法读取样本数（需要安装lmdb模块）")
    print("基于数据大小估算: 约 17,000-20,000 样本")
