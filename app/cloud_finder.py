import numpy as np
from itertools import product
import os
import matplotlib.pyplot as plt
import cv2
from os.path import join

from eolearn.io.local_io import ImportFromTiff
from eolearn.core import EOPatch
from eolearn.core.constants import FeatureType
from tqdm import tqdm


def find_clouds(filename, path, data):
    # data = data['data']

    def prod(x):
        res = 1
        for i in x:
            res *= i
        return res

    # returns dictionary *set_of_frame_existance*:*mask* and framewise mask
    def process(_data):
        shape = _data.shape
        primary_mask = (_data != 0).all(axis=-1, keepdims=True)
        history_size = shape[0] - 1
        mask_templates = [[False, True] for i in range(history_size)] + [[True]]
        mask_templates = list(product(*mask_templates))[1:]
        temporal_masks = [np.expand_dims(np.array(i), (1, 2, 3)) for i in mask_templates]
        masks = []
        for mask in temporal_masks:
            masks.append((primary_mask == mask).all(axis=0, keepdims=True))
        dictionary = {k: v for k, v in zip(mask_templates, masks) if v.any()}
        return dictionary, primary_mask

    # change frame masks to overlap with the last one
    result, layer_masks = process(data)
    for idx, mask in enumerate(layer_masks):
        layer_masks[idx] = np.logical_and(mask, layer_masks[-1])

    def rescale(_data):
        rgbmin, rgbmax = np.percentile(_data.reshape(-1, _data.shape[-1]),
                                       [1, 99], axis=0, keepdims=True)
        _data = (_data.clip(rgbmin, rgbmax) - rgbmin) / (rgbmax - rgbmin)
        return _data

    # for idx, (k, v) in tqdm(enumerate(result.items())):
    #     os.makedirs(str(idx), exist_ok=True)
    #     with open(f'{idx}/description.txt', 'w') as f:
    #         f.write(str(k))
    #
    #     copy_data = np.concatenate([rescale(data[i:i + 1]) for i in range(data.shape[0])], axis=0)
    #
    #     temp_data = (copy_data * v)[:, :, :, :-1]
    #     for i in range(temp_data.shape[0]):
    #         plt.imsave(f'{idx}/{i}.png', temp_data[i])

    def sigmoid(x):
        return 1 / (1 + np.exp(-x))

    deviation = np.zeros(data.shape[:-1])[:-1]
    iterations = 10 ** 5
    errors = 500

    idata = data.astype('int')
    t_means = []

    for frame in range(data.shape[0] - 1):
        X = idata[-1] - idata[frame]
        X = X[layer_masks[frame][:, :, 0], :]
        # mean_vectors = []

        idices = np.random.choice(X.shape[0], iterations)
        values = X[idices, :]

        tmean = values.mean(axis=0)
        for i in tqdm(range(180)):
            L2 = (((values - tmean) ** 2).sum(axis=1)) ** 0.5
            values = values[np.argpartition(L2, -errors)[:-errors]]
            tmean = values.mean(axis=0)

        t_means.append(np.expand_dims(tmean.astype('int'), (0, 1, 2)))
        approximation = data[frame] + np.expand_dims(tmean.astype('int'), (0, 1, 2))
        L2 = (((approximation - data[-1])[0] * layer_masks[0]) ** 2).sum(axis=2) ** 0.5
        L = ((L2 - L2.mean()) / (L2.mean() / 3)) * layer_masks[0][:, :, -1]
        L = sigmoid(L) * layer_masks[0][:, :, -1]
        deviation[frame] = L
    # t_means = np.concatenate(t_means, axis=0)
    print("Smth")
    result_cloud_map = np.zeros((data.shape[1], data.shape[2]))
    for idx, (k, v) in tqdm(enumerate(result.items())):
        temp_data = deviation[np.array(k[:-1])]
        print(temp_data)
        result_cloud_map += np.min(temp_data, axis=0) * v.squeeze()

    plt.imsave(join(path, "clouds.png"), result_cloud_map, cmap='gray')

    raw_mask = (result_cloud_map * 255).astype('uint8')

    mask_edit = np.zeros((len(raw_mask), len(raw_mask[0])))
    mask_edit = cv2.normalize(raw_mask, mask_edit, 0, 255, cv2.NORM_MINMAX)
    # cv2.imwrite("clouds_edit.png", mask_edit)

    mask_median = cv2.medianBlur(mask_edit, 35)
    # cv2.imwrite("clouds_median.png", mask_median)

    _, mask_thresh = cv2.threshold(mask_median, 50, 255, cv2.THRESH_BINARY)
    # cv2.imwrite("clouds_thresh.png", mask_thresh)

    kernel = np.ones((15, 15), np.uint8)
    mask_opening = cv2.morphologyEx(mask_thresh, cv2.MORPH_OPEN, kernel)
    cv2.imwrite(join(path, "clouds_opening.png"), mask_opening)


def tif_to_npz(files):
    patch = EOPatch()
    tasks = [ImportFromTiff((FeatureType.DATA, f'LOADED_DATA'), path) for path in files[::-1]]

    for task in tqdm(tasks):
        task.execute(patch)
        if 'bands' in patch[FeatureType.DATA]:
            patch.add_feature(FeatureType.DATA, 'bands', EOPatch.concatenate_data(
                patch[FeatureType.DATA][f'LOADED_DATA'],
                patch[FeatureType.DATA]['bands'],
            ))
            patch.remove_feature(FeatureType.DATA, f'LOADED_DATA')
        else:
            patch.rename_feature(FeatureType.DATA, f'LOADED_DATA', 'bands')

    np.savez_compressed('data', data=patch[FeatureType.DATA]['bands'])
    # def rescale(arr):
    #     rgbmin, rgbmax = np.percentile(arr, [1, 99])  # Ignore outliers
    #     arr = (arr.clip(rgbmin, rgbmax) - rgbmin) / (rgbmax - rgbmin)  # Rescale to brighten the image
    #     return arr
    #
    # for img in range(len(files)):
    #     arr = np.concatenate([rescale(data[img, :, :, i:i + 1]) for i in range(2, -1, -1)], axis=2)
    #     plt.imshow(arr)
    #     plt.show()
    #     plt.imsave(f"eo_learn/patch/img{img}.png", arr)


def npz_to_imgs(files, path, data):
    def rescale(arr):
        rgbmin, rgbmax = np.percentile(arr, [1, 99])  # Ignore outliers
        arr = (arr.clip(rgbmin, rgbmax) - rgbmin) / (rgbmax - rgbmin)  # Rescale to brighten the image
        return arr
    image_nums = []
    for img, _ in enumerate(files):
        arr = np.concatenate([rescale(data[img, :, :, i:i + 1]) for i in range(2, -1, -1)], axis=2)
        jpg_full_path = join(path, f"{img}.png")
        image_nums.append(img)
        plt.imsave(jpg_full_path, arr)
    return image_nums
