# FIXME: refactor according to wiki?

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


def preprocess_mnist(data, output_size):
    # channels = len(data[0].mode)
    channels = 1  # All Mnist networks requires 1 channel
    result = np.ndarray((0, *output_size, channels), dtype=np.float32)
    for img in data:
        img = img.resize(size=output_size, resample=Image.CUBIC)
        tensor = np.array(img).astype(np.float32)
        # tensor = cv2.resize(tensor, dsize=output_size, interpolation=cv2.INTER_CUBIC) # from openCV
        tensor = np.expand_dims(tensor, axis=0)
        if len(tensor.shape) < 4:
            tensor = np.expand_dims(tensor, axis=3)
        tensor = tensor / 255.0
        result = np.concatenate((result, tensor), 0)
    return result


def pre(path_to_image):
    image = Image.open(path_to_image)

    # run preprocessing data
    input_data = [(np.asarray(image).astype(np.float32),)]
    sizes = get_img_sizes(input_data)

    #
    images = []
    for data in input_data:
        for dat in data:
            images.append(Image.fromarray(np.uint8(dat)).convert('L'))

    _, dim0, dim1, _ = None, 28, 28, 1
    input_hw_size = dim0, dim1

    result_array = preprocess_mnist(images, input_hw_size)

    result_dict = {}
    input_tensor_names = ('input_input',)

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


def postprocess_imagenet(inference_results, class_offset: int):
    top = 1
    num_classes = []
    for result in inference_results:
        assert len(result.keys()) == 1
        input_data = result[list(result.keys())[0]]
        input_data = np.reshape(input_data, (input_data.shape[0], input_data.shape[-1]))
        classes = np.squeeze(input_data.argsort()[::, -top:])[()]
        # the operation '[()]' returns number if the array in 0-d and returns an array otherwise
        if not isinstance(classes, np.ndarray):
            classes = np.array([classes])
        classes = classes + class_offset

        num_classes.append(classes)

    return num_classes


def post(images_sizes, inference_output):
    predictions = []
    for idx in range(len(images_sizes)):
        outs_to_imagenet = get_slice_array_dict(idx, inference_output)

        prediction = postprocess_imagenet((outs_to_imagenet,), 0)
        predictions.append(prediction[0])

    return predictions
