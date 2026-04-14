import argparse

parser = argparse.ArgumentParser(description="参数管理")

parser.add_argument('--model', type=str, help="YOLO模型选择")
parser.add_argument('--seed', type=int, default=2026, help="随机数种子设置")
parser.add_argument('--epochs', type=int, default=100)
parser.add_argument('--batch', type=int, default=-1)
parser.add_argument('--imagesz', type=int, default=1280)
parser.add_argument('--optimizer', type=str, default="Adam", help="模型训练的优化器")
parser.add_argument('--patience', type=int, default=15, help="模型早停的轮数")

args = parser.parse_args()
