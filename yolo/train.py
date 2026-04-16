import numpy as np
import random
import torch
import albumentations as A
from ultralytics import YOLO

from yolo.config import args

if __name__ == '__main__':
    # 初始化模型
    model = YOLO(args.model)

    # 固定随机数种子
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)

    # 定义数据增强操作
    # ISONoise摄像头传感器噪音
    transform = A.Compose(
        [
            A.RandomRotate90(p=1),
            A.RandomBrightnessContrast(brightness_limit=0.05, contrast_limit=0.05, p=0.5),
            A.OneOf(
                [
                    A.MotionBlur(blur_limit=(3, 15), p=1),
                    A.GaussianBlur(blur_limit=(3, 15), p=1),
                    A.MedianBlur(blur_limit=(3, 11), p=1),
                    A.ZoomBlur(max_factor=(1.02, 1.02), step_factor=0.02, p=1)
                ], p=0.5
            ),
            A.OneOf(
                [
                    A.ISONoise(color_shift=(0.01, 0.03), intensity=(0.1, 0.25), p=1),
                    A.GaussNoise(std_range=(0.05, 0.15), p=1),
                    A.SaltAndPepper(amount=(0.01, 0.05), salt_vs_pepper=(0.01, 0.05), p=1),
                ], p=0.5
            ),
            A.ImageCompression(quality_range=(20, 90), compression_type="jpeg", p=1)
        ],
        bbox_params=A.BboxParams(format="yolo"),
        seed=args.seed
    )

    transform_two_times = A.Compose(
        [transform for i in range(2)],
        bbox_params=A.BboxParams(format="yolo"),
        seed=args.seed
    )

    # 开始训练
    results = model.train(
        data='PCB_DATASET_YOLO/PCB_DATASET.yaml',
        name='PCB',
        seed=args.seed,
        verbose=True,
        workers=32,
        cache=True,
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        optimizer=args.optimizer,
        patience=args.patience,
        augmentations=transform,
        save_period=25,
    )