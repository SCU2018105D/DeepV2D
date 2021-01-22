import numpy as np
import tensorflow as tf
from utils.einsum import einsum


MIN_DEPTH = 0.1
# 按照形状进行网格化
def coords_grid(shape, homogeneous=True):
    """ grid of pixel coordinates """
    xx, yy = tf.meshgrid(tf.range(shape[-1]), tf.range(shape[-2]))

    xx = tf.cast(xx, tf.float32) # 转换坐标
    yy = tf.cast(yy, tf.float32)

    if homogeneous:
        coords = tf.stack([xx, yy, tf.ones_like(xx)], axis=-1)
    else:
        coords = tf.stack([xx, yy], axis=-1)

    new_shape = (tf.ones_like(shape[:-2]), shape[-2:], [-1])
    new_shape = tf.concat(new_shape, axis=0)
    coords = tf.reshape(coords, new_shape)

    tile = tf.concat((shape[:-2], [1,1,1]), axis=0) # 获取小块
    coords = tf.tile(coords, tile) # 对坐标点张量进行扩张
    return coords

def extract_and_reshape_intrinsics(intrinsics, shape=None):
    """ Extracts (fx, fy, cx, cy) from intrinsics matrix """

    fx = intrinsics[:, 0, 0]
    fy = intrinsics[:, 1, 1]
    cx = intrinsics[:, 0, 2]
    cy = intrinsics[:, 1, 2]

    if shape is not None:
        batch = tf.shape(fx)[:1]
        fillr = tf.ones_like(shape[1:])
        k_shape = tf.concat([batch, fillr], axis=0)

        fx = tf.reshape(fx, k_shape)
        fy = tf.reshape(fy, k_shape)
        cx = tf.reshape(cx, k_shape)
        cy = tf.reshape(cy, k_shape)

    return (fx, fy, cx, cy)

# 将depthmap转换为点云,主要是根据相机参数还原原始的3D点云
def backproject(depth, intrinsics, jacobian=False):
    """ backproject depth map to point cloud """

    coords = coords_grid(tf.shape(depth), homogeneous=True)
    x, y, _ = tf.unstack(coords, num=3, axis=-1)

    x_shape = tf.shape(x)
    fx, fy, cx, cy = extract_and_reshape_intrinsics(intrinsics, x_shape)
    # 在这里矫正fx
    Z = tf.identity(depth) # 获取全像素的真实深度
    X = Z * (x - cx) / fx # 获取x坐标
    Y = Z * (y - cy) / fy
    points = tf.stack([X, Y, Z], axis=-1)

    if jacobian:
        o = tf.zeros_like(Z) # used to fill in zeros

        # jacobian w.r.t (fx, fy)
        jacobian_intrinsics = tf.stack([
            tf.stack([-X / fx], axis=-1),
            tf.stack([-Y / fy], axis=-1),
            tf.stack([o], axis=-1),
            tf.stack([o], axis=-1)], axis=-2)

        return points, jacobian_intrinsics
    
    return points


def project(points, intrinsics, jacobian=False):
    
    """ project point cloud onto image 将点云投影到图像上""" 
    X, Y, Z = tf.unstack(points, num=3, axis=-1)
    Z = tf.maximum(Z, MIN_DEPTH) # 获取最大深度

    x_shape = tf.shape(X) # 获取x数据的长度
    fx, fy, cx, cy = extract_and_reshape_intrinsics(intrinsics, x_shape) # 获取x方向上的相机内参

    x = fx * (X / Z) + cx
    y = fy * (Y / Z) + cy
    coords = tf.stack([x, y], axis=-1)

    if jacobian:
        o = tf.zeros_like(x) # used to fill in zeros
        zinv1 = tf.where(Z <= MIN_DEPTH+.01, tf.zeros_like(Z), 1.0 / Z)
        zinv2 = tf.where(Z <= MIN_DEPTH+.01, tf.zeros_like(Z), 1.0 / Z**2)

        # jacobian w.r.t (X, Y, Z)
        jacobian_points = tf.stack([
            tf.stack([fx * zinv1, o, -fx * X * zinv2], axis=-1),
            tf.stack([o, fy * zinv1, -fy * Y * zinv2], axis=-1)], axis=-2)

        # jacobian w.r.t (fx, fy)
        jacobian_intrinsics = tf.stack([
            tf.stack([X * zinv1], axis=-1),
            tf.stack([Y * zinv1], axis=-1),], axis=-2)

        return coords, (jacobian_points, jacobian_intrinsics)

    return coords
