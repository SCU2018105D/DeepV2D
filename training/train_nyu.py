import sys
sys.path.append('deepv2d')

import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

import cv2
import os
import time
import random
import argparse

from core import config
from trainer import DeepV2DTrainer

from data_stream.nyuv2 import NYUv2

def main(args):

    cfg = config.cfg_from_file(args.cfg)
    # 日志文件夹
    log_dir = os.path.join('logs/nyu', args.name)
    # 检查日志文件夹是否存在
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    # 保存文件夹
    checkpoint_dir = os.path.join('checkpoints/nyu', args.name)
    if not os.path.exists(checkpoint_dir):
        os.makedirs(checkpoint_dir)
    
    # 临时文件夹
    tmp_dir = os.path.join('tmp/nyu', args.name)
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    # 日志文件夹
    cfg.LOG_DIR = log_dir
    # 输出路径地址
    cfg.CHECKPOINT_DIR = checkpoint_dir
    # 临时文件地址
    cfg.TMP_DIR = tmp_dir

    solver = DeepV2DTrainer(cfg)
    ckpt = None
    # 注意这里直接使用tfrecords进行训练
    if args.restore is not None:
        solver.train(args.tfrecords, cfg, stage=2, restore_ckpt=args.restore, num_gpus=args.num_gpus)

    else:
        for stage in [1, 2]:
            ckpt = solver.train(args.tfrecords, cfg, stage=stage, ckpt=ckpt, num_gpus=args.num_gpus)
            tf.reset_default_graph()


if __name__ == '__main__':

    seed = 1234
    tf.set_random_seed(seed)
    np.random.seed(seed)
    random.seed(seed)

    parser = argparse.ArgumentParser()
    parser.add_argument('--name', help='name of your experiment')
    parser.add_argument('--cfg', default='cfgs/nyu.yaml', help='path to yaml config file')
    parser.add_argument('--tfrecords', default='datasets/nyu_train.tfrecords', help='path to tfrecords training file')
    parser.add_argument('--restore',  help='use restore checkpoint')
    parser.add_argument('--num_gpus',  type=int, default=1, help='number of gpus to use')
    args = parser.parse_args()

    main(args)