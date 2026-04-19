import os
import shutil
import random
import xml.etree.ElementTree as ET

# --------------------------- 配置区域 ---------------------------
# 原始数据集路径（请根据实际情况修改）
ORIGINAL_DATASET_PATH = "../NEU-DET"
# 输出数据集路径
OUTPUT_PATH = "../NEU_DET_YOLO"
# 数据集划分比例
TRAIN_RATIO = 0.7
# 随机种子（保证结果可复现）
RANDOM_SEED = 42
# NEU-DET 缺陷类别定义
CLASS_NAMES = [
    "crazing",
    "inclusion",
    "patches",
    "pitted_surface",
    "rolled-in_scale",
    "scratches"
]


# -----------------------------------------------------------------

def create_output_dirs():
    """创建输出目录结构"""
    dirs = [
        os.path.join(OUTPUT_PATH, "train", "images"),
        os.path.join(OUTPUT_PATH, "train", "labels"),
        os.path.join(OUTPUT_PATH, "val", "images"),
        os.path.join(OUTPUT_PATH, "val", "labels")
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def parse_xml_to_yolo(xml_path, class_to_idx):
    """
    解析XML文件并转换为YOLO格式
    返回: [(class_id, x_center, y_center, width, height), ...]
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # 获取图像尺寸
    size_elem = root.find("size")
    img_w = int(size_elem.find("width").text)
    img_h = int(size_elem.find("height").text)

    yolo_labels = []
    for obj in root.findall("object"):
        # 获取类别
        class_name = obj.find("name").text
        if class_name not in class_to_idx:
            continue
        class_id = class_to_idx[class_name]

        # 获取边界框坐标
        bndbox = obj.find("bndbox")
        xmin = float(bndbox.find("xmin").text)
        ymin = float(bndbox.find("ymin").text)
        xmax = float(bndbox.find("xmax").text)
        ymax = float(bndbox.find("ymax").text)

        # 转换为YOLO格式 (归一化中心坐标和宽高)
        x_center = (xmin + xmax) / 2.0 / img_w
        y_center = (ymin + ymax) / 2.0 / img_h
        width = (xmax - xmin) / img_w
        height = (ymax - ymin) / img_h

        yolo_labels.append((class_id, x_center, y_center, width, height))

    return yolo_labels


def main():
    random.seed(RANDOM_SEED)
    create_output_dirs()

    # 类别到索引的映射
    class_to_idx = {name: i for i, name in enumerate(CLASS_NAMES)}

    # 1. 收集所有样本并按类别分组
    print("正在收集样本信息...")
    class_to_samples = {name: [] for name in CLASS_NAMES}

    images_dir = os.path.join(ORIGINAL_DATASET_PATH, "IMAGES")
    annotations_dir = os.path.join(ORIGINAL_DATASET_PATH, "ANNOTATIONS")

    for img_file in os.listdir(images_dir):
        if not img_file.endswith(".jpg"):
            continue
        # 解析文件名 (例如: crazing_3.jpg -> class_name=crazing)
        name_part = os.path.splitext(img_file)[0]
        # 使用rsplit从右分割，处理类似 rolled-in_scale 的类别名
        class_name = name_part.rsplit("_", 1)[0]

        if class_name in class_to_samples:
            # 存储不带后缀的文件名，方便同时处理图片和标签
            class_to_samples[class_name].append(name_part)

    # 2. 按类别均匀划分训练集和验证集
    train_samples = []
    val_samples = []

    for class_name, samples in class_to_samples.items():
        # 打乱当前类别的样本
        random.shuffle(samples)
        # 计算切分点
        split_idx = int(len(samples) * TRAIN_RATIO)
        # 分配
        train_samples.extend(samples[:split_idx])
        val_samples.extend(samples[split_idx:])
        print(
            f"类别 {class_name}: 总数 {len(samples)} -> 训练 {len(samples[:split_idx])}, 验证 {len(samples[split_idx:])}")

    # 3. 定义处理函数：复制图片和转换标签
    def process_samples(sample_list, split_name):
        target_img_dir = os.path.join(OUTPUT_PATH, split_name, "images")
        target_lbl_dir = os.path.join(OUTPUT_PATH, split_name, "labels")

        print(f"正在处理 {split_name} 集...")
        for name_part in sample_list:
            # 复制图片
            src_img = os.path.join(images_dir, name_part + ".jpg")
            dst_img = os.path.join(target_img_dir, name_part + ".jpg")
            shutil.copyfile(src_img, dst_img)

            # 转换并写入标签
            src_xml = os.path.join(annotations_dir, name_part + ".xml")
            dst_txt = os.path.join(target_lbl_dir, name_part + ".txt")

            yolo_data = parse_xml_to_yolo(src_xml, class_to_idx)

            with open(dst_txt, "w") as f:
                for data in yolo_data:
                    # 格式: class_id x_center y_center width height
                    line = f"{data[0]} {data[1]:.6f} {data[2]:.6f} {data[3]:.6f} {data[4]:.6f}"
                    f.write(line + "\n")

    # 4. 执行处理
    process_samples(train_samples, "train")
    process_samples(val_samples, "val")

    # 5. 生成 YOLO 配置文件 (yaml)
    yaml_content = f"""
# NEU-DET Dataset Config
path: {os.path.abspath(OUTPUT_PATH)}
train: train/images
val: val/images

nc: {len(CLASS_NAMES)}
names: {CLASS_NAMES}
""".strip()

    with open(os.path.join(OUTPUT_PATH, "neu_det.yaml"), "w") as f:
        f.write(yaml_content)

    print("\n处理完成！")
    print(f"数据集已保存至: {OUTPUT_PATH}")
    print(f"配置文件已生成: {os.path.join(OUTPUT_PATH, 'neu_det.yaml')}")


if __name__ == "__main__":
    main()