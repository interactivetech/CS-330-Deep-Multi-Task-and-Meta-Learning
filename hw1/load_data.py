import numpy as np
import os
import random
import tensorflow as tf
from scipy import misc


def get_images(paths, labels, nb_samples=None, shuffle=True):
    """
    Takes a set of character folders and labels and returns paths to image files
    paired with labels.
    Args:
        paths: A list of character folders
        labels: List or numpy array of same length as paths
        nb_samples: Number of images to retrieve per character
    Returns:
        List of (label, image_path) tuples
    """
    if nb_samples is not None:
        sampler = lambda x: random.sample(x, nb_samples)
    else:
        sampler = lambda x: x
    images_labels = [(i, os.path.join(path, image))
                     for i, path in zip(labels, paths)
                     for image in sampler(os.listdir(path))]
    if shuffle:
        random.shuffle(images_labels)
    return images_labels


def image_file_to_array(filename, dim_input):
    """
    Takes an image path and returns numpy array
    Args:
        filename: Image filename
        dim_input: Flattened shape of image
    Returns:
        1 channel image
    """
    #image = misc.imread(filename)
    image = np.random.rand(28, 28)
    image = image.reshape([dim_input])
    image = image.astype(np.float32) / 255.0
    image = 1.0 - image
    return image


class DataGenerator(object):
    """
    Data Generator capable of generating batches of Omniglot data.
    A "class" is considered a class of omniglot digits.
    """

    def __init__(self, num_classes, num_samples_per_class, config={}):
        """
        Args:
            num_classes: Number of classes for classification (K-way)
            num_samples_per_class: num samples to generate per class in one batch
            batch_size: size of meta batch size (e.g. number of functions)
        """
        self.num_samples_per_class = num_samples_per_class
        self.num_classes = num_classes

        data_folder = config.get('data_folder', './omniglot_resized')
        self.img_size = config.get('img_size', (28, 28))

        self.dim_input = np.prod(self.img_size)
        self.dim_output = self.num_classes

        character_folders = [os.path.join(data_folder, family, character)
                             for family in os.listdir(data_folder)
                             if os.path.isdir(os.path.join(data_folder, family))
                             for character in os.listdir(os.path.join(data_folder, family))
                             if os.path.isdir(os.path.join(data_folder, family, character))]

        random.seed(1)
        random.shuffle(character_folders)
        num_val = 100
        num_train = 1100
        self.metatrain_character_folders = character_folders[: num_train]
        self.metaval_character_folders = character_folders[
                                         num_train:num_train + num_val]
        self.metatest_character_folders = character_folders[
                                          num_train + num_val:]

    def sample_batch(self, batch_type, batch_size):
        """
        Samples a batch for training, validation, or testing
        Args:
            batch_type: train/val/test
        Returns:
            A a tuple of (1) Image batch and (2) Label batch where
            image batch has shape [B, K, N, 784] and label batch has shape [B, K, N, N]
            where B is batch size, K is number of samples per class, N is number of classes
        """
        if batch_type == "train":
            folders = self.metatrain_character_folders
        elif batch_type == "val":
            folders = self.metaval_character_folders
        else:
            folders = self.metatest_character_folders

        #############################
        #### YOUR CODE GOES HERE ####
        # Extract second folder from folder strings
        samples = np.ndarray(shape=(4,))
        # Placeholder
        # string = "a" * 20
        # families = {string[19:19+(string[19:].find('/'))]: [] for string in folders}
        # #families = families.keys()
        # families = {string[19:19+(string[19:].find('/'))]: (families[string[19:19+(string[19:].find('/'))]]).append(string[1+19+(string[19:].find('/')):]) for string in folders}
        o = len('./omniglot_resized/')
        families = {}
        for string in folders:
            class_name = string[o:o + (string[o:].find('/'))]
            # charName   = string[1 + o + (string[o:].find('/')):]
            char_folder = string
            if not class_name in families.keys():
                families[class_name] = np.asarray(char_folder)
            else:
                families[class_name] = np.hstack([families[class_name], char_folder])

        B = batch_size
        N = self.num_classes
        K = self.num_samples_per_class
        img_size = 784
        all_image_batches = np.ndarray([B, K, N, img_size])
        all_label_batches = np.ndarray([B, K, N, N])
        classes = [f for f in families.keys()]
        # 0. Repeat for B batches
        for batch in range(B):
            # 1. Sample N different classes
            n_classes = np.random.choice(classes, N, replace=False)
            # 2. Sample and load K images
            for j, cl in enumerate(n_classes):
                k_char_folders = np.random.choice(families[cl], K, replace=True)
                k_labels = [s[1 + o + (s[o:].find('/')):] for s in k_char_folders]
                k_char_paths = [char_folder for char_folder in k_char_folders]

                k_tuples = get_images(k_char_paths, k_labels, nb_samples=K)
                k_images = np.asarray([image_file_to_array(im[1], img_size) for im in k_tuples])


                all_image_batches[batch, :, j, :] = k_images.copy()#.view((K, img_size)) # ! TODO: Check dimensions!
                all_label_batches[batch, :, j, :] = np.array([0] * N)
                all_label_batches[batch, :, j, j] = 1
        # print(">> ", all_image_batches.shape)
        # print(">> ", all_label_batches.shape)

            #############################
        return all_image_batches, all_label_batches
