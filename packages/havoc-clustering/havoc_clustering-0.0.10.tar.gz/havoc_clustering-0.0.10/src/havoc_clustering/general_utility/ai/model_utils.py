import numpy as np
import tensorflow.keras.backend as K


class ModelUtils:

    @staticmethod
    def get_layer_datas(model, imgs, layers):
        '''
        Returns image data after the specified layer

        :param model: tf model
        :param imgs: list of images
        :param layers: list of string layer names or model layers within the model
        :return: list of numpy arrays; each element corresponds to each layer output
        '''

        if len(layers) == 0:
            raise Exception('No layers specified')

        imgs = ModelUtils.prepare_images(imgs)

        layer_outputs = [model.get_layer(l).output if type(l) == str else l.output for l in layers]
        get_output = K.function(model.layers[0].input, layer_outputs)

        return get_output(imgs)

    @staticmethod
    def prepare_images(imgs):
        '''
        Returns an array of prepared images for model use

        :param img: array of images
        :return: array of images
        '''

        if imgs.max() > 1:
            imgs = np.divide(imgs, 255)

        return imgs
