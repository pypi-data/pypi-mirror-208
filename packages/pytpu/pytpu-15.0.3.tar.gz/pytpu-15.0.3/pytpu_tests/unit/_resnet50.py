# FIXME: refactor according to wiki?

from typing import Tuple, Any

import numpy as np
from PIL import Image


def get_img_sizes(input_data):
    sizes = []
    for inp in input_data:
        if len(inp) == 1:
            for image in inp:
                sizes.append(image.shape[:-1][::-1])
        else:
            sizes.append(inp[0].shape)
    return sizes


# Preprocessing
def _central_crop(image: Image, percent: float = 1.0) -> Image:
    """Crop center from image."""
    height, width = np.shape(image)[:2]
    min_dim = int(min(height, width) * percent)
    crop_top = (height - min_dim) // 2
    crop_left = (width - min_dim) // 2
    return image.crop((crop_left, crop_top, crop_left + min_dim, crop_top + min_dim))


def _crop_and_resize(image: Image, target_img_size: Tuple[int, int]) -> Image:
    """Crop center from image and resize it to another shape."""
    new_img = _central_crop(image, 0.85)
    new_img = new_img.resize(size=target_img_size)
    return new_img


def preprocess_imagenet(data, output_size):
    channels = 3  # All Imagenet networks requires 3 channels
    result = np.ndarray((0, *output_size, channels), dtype=np.float32)
    for img in data:
        img = img.convert('RGB')
        img = _crop_and_resize(img, output_size)
        tensor = np.asarray(img).astype(np.float32)
        tensor = np.expand_dims(tensor, axis=0)
        result = np.concatenate((result, tensor), 0)
    return result


def _sub_mean_rgb(tensor):
    # RGB MEAN
    return tensor - np.array([123.68, 116.779, 103.939], dtype=np.float32)


def pre(image_path: Any):
    image = Image.open(image_path)

    # Data preprocessing
    input_data = [(np.asarray(image).astype(np.float32),)]
    sizes = get_img_sizes(input_data)

    images = []
    for data in input_data:
        for dat in data:
            images.append(Image.fromarray(np.uint8(dat)))

    _, dim0, dim1, _ = None, 224, 224, 3
    input_hw_size = dim0, dim1

    result_array = preprocess_imagenet(images, input_hw_size)
    result_array = _sub_mean_rgb(result_array)

    result_dict = {}

    input_tensor_names = ('Placeholder',)

    for input_tensor_name in input_tensor_names:
        result_dict[input_tensor_name] = result_array
    return result_dict, sizes


# Postprocessing
def get_slice_array_dict(idx_slice: int, inference_output):
    outs = list(inference_output.keys())
    out_dict = {}
    for i in range(len(outs)):
        out_dict[outs[i]] = inference_output[outs[i]][idx_slice:idx_slice + 1]
    return out_dict


def postprocess_imagenet(inference_results, class_offset, top):
    num_classes = []
    for result in inference_results:
        assert len(result.keys()) == 1
        input_data = result[list(result.keys())[0]]
        input_data = np.reshape(input_data, (input_data.shape[0], input_data.shape[-1]))
        classes = np.squeeze(input_data.argsort()[::, -top:])[()]
        if not isinstance(classes, np.ndarray):
            classes = np.array([classes])
        classes = classes + class_offset

        num_classes.append(classes)
    return num_classes


def post(images_sizes, inference_output):
    predictions = []
    for idx in range(len(images_sizes)):
        outs_to_imagenet = get_slice_array_dict(idx, inference_output)

        prediction = postprocess_imagenet((outs_to_imagenet,), 1, 1)
        predictions.append(prediction[0])

    return predictions


IMAGENET_CLASSES = {
    0: "background",
    1: "tench, Tinca tinca",
    2: "goldfish, Carassius auratus",
    256: "Leonberg",
    257: "Newfoundland, Newfoundland dog",
    258: "Great Pyrenees",
    817: "spindle",
    818: "sports car, sport car",
    819: "spotlight, spot",
    998: "bolete",
    999: "ear, spike, capitulum",
    1000: "toilet tissue, toilet paper, bathroom tissue",
}
