import errno
import os
from loguru import logger

import torch
import torchvision
from PIL import Image
from torchvision.transforms import transforms as T
from torchvision.utils import draw_segmentation_masks


def get_args_parser(add_help=True):
    import argparse

    parser = argparse.ArgumentParser(description="Image Segmentation And Mosaic", add_help=add_help)

    parser.add_argument("-w", "--weight-file-path",
                        required=True,
                        dest="weight_file_path",
                        default="./model.pth",
                        type=str,
                        help="The weight file path")

    parser.add_argument("-i", "--input", required=True, type=str, help="Input image file")

    parser.add_argument("-o", "--output-dir",
                        dest="output_dir",
                        default="./output_images",
                        type=str,
                        help="The dir of processed images")

    parser.add_argument("-s", "--score-threshold",
                        dest="score_threshold",
                        default=0.5,
                        type=float,
                        help="The fractional threshold of the identification area")

    parser.add_argument("-v", "--verbose",
                        dest="verbose",
                        action="store_true",
                        help="Output detailed log")

    parser.add_argument("-l", "--log-file",
                        dest="log_file",
                        default="prediction.log",
                        type=str,
                        help="The path of log file, default is ./prediction.log")

    return parser


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


@logger.catch
def enter(args):
    if args.verbose:
        logger.add(args.log_file)
    _device = 'cpu'
    if torch.cuda.is_available():
        logger.info('cuda is available')
        _device = 'cuda'
    else:
        logger.info('cuda is not available, cpu is in use')
    device = torch.device(_device)
    if args.output_dir:
        mkdir(args.output_dir)
    # 加载模型权重
    model_path = args.weight_file_path
    model = torchvision.models.get_model(
        'maskrcnn_resnet50_fpn', weights=None, weights_backbone='ResNet50_Weights.IMAGENET1K_V1', num_classes=17
    ).to(device)

    checkpoint = torch.load(model_path, map_location=device)

    model.load_state_dict(checkpoint['model'])

    model.eval()

    # 读取输入图片
    image = Image.open(args.input).convert("RGB")

    transforms = T.Compose(
        [
            T.PILToTensor(),
            T.ConvertImageDtype(torch.float),
        ]
    )
    transforms_uint8 = T.Compose(
        [
            T.PILToTensor(),
            T.ConvertImageDtype(torch.uint8),
        ]
    )

    image_tensor = transforms(image).to(device)

    # 进行预测
    with torch.no_grad():
        predictions = model([image_tensor])

    # 将预测结果转换为 NumPy 数组
    pred_boxes = predictions[0]["boxes"]
    pred_masks = predictions[0]["masks"]
    pred_classes = predictions[0]["labels"]
    pred_scores = predictions[0]["scores"]

    score_threshold = args.score_threshold

    img_ = transforms_uint8(image)
    for i in range(pred_masks.shape[0]):
        if pred_scores[i] >= score_threshold:
            img_ = draw_segmentation_masks(img_, torch.as_tensor(pred_masks[i, 0, :, :] >= 0.5, dtype=torch.bool),
                                           colors=(240, 10, 157), alpha=1)

    tensor_to_pil = T.ToPILImage()

    pil_image = tensor_to_pil(img_)

    input_file_name, extension = os.path.splitext(os.path.basename(args.input))

    output_file_name = f'{input_file_name}_out{extension}'

    pil_image.save(os.path.join(args.output_dir, output_file_name))

    logger.info(
        f'The image [{input_file_name}{extension}] processing is complete '
        f'and has been saved to [{os.path.abspath(os.path.join(args.output_dir, output_file_name))}].'
        f'The score threshold is {score_threshold}'
    )


def main():
    args = get_args_parser().parse_args()
    enter(args)


if __name__ == "__main__":
    main()
