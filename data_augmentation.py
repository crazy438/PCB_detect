import cv2
import pathlib
import pandas as pd
import albumentations as A


# 固定随机种子
import random
import numpy as np
seed = 2026
random.seed(42)
np.random.seed(42)



# 定义数据增强操作
# ISONoise摄像头传感器噪音
transform = A.Compose(
    [
        A.RandomRotate90(p=1),
        A.RandomBrightnessContrast(brightness_limit=0.05, contrast_limit=0.05, p=0.5),
        A.OneOf(
            [
                A.MotionBlur(blur_limit=(3,15), p=1),
                A.GaussianBlur(blur_limit=(3,15), p=1),
                A.MedianBlur(blur_limit=(3,11), p=1),
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
        A.ImageCompression(quality_range=(20,90), compression_type="jpeg", p=1)
    ],
    bbox_params = A.BboxParams(format="yolo"),
    seed = seed
)

transform_two_times = A.Compose(
    [transform for i in range(2)],
    bbox_params = A.BboxParams(format="yolo"),
    seed = seed
)

##############################################################
# 加载图片，并对每张图片增强多次，获得99张图片，再加上原来的一张，构成100张样本
img_list = pathlib.Path("../PCB_DATASET/images").rglob("*.jpg")

for img_path in img_list:
    img = cv2.imread(img_path)

    # 获取对应的标签文件路径，并读取标签数据
    label_path = img_path.with_suffix(".txt")
    df = pd.read_csv(label_path, header=None, sep=' ')

    bboxes = [ row for row in df.iloc[:, 1:].itertuples(index=False) ]


    for i in range(1,100):
        result = transform_two_times(
            image=img,
            bboxes=bboxes,
        ),

        # 更新bboxes坐标参数
        df.iloc[:, 1:] = pd.DataFrame(result[0]["bboxes"])

        cv2.imwrite(img_path.parent / (str(img_path.stem) + f"_{i}.jpg"), result[0]["image"])
        df.to_csv(label_path.parent / (str(label_path.stem) + f"_{i}.txt"), sep=' ', index=False, header=False)
pass