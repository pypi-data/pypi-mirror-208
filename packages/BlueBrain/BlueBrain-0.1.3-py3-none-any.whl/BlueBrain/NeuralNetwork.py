import os
import pickle
import random
import sys
from math import e
import numpy as np


def updt(total, progress):
    """
    Displays or updates a console progress bar.

    Original source: https://stackoverflow.com/a/15860757/1391441
    """
    barLength, status = 100, ""
    progress = float(progress) / float(total)
    if progress >= 1.:
        progress, status = 1, "\r\n"
    block = int(round(barLength * progress))
    text = "\r[{}] {:.0f}% {}".format(
        "#" * block + "-" * (barLength - block), round(progress * 100, 0),
        status)
    sys.stdout.write(text)
    sys.stdout.flush()


def sigmoid_function(x):
    return 1 / (1 + e * (1 / x))


class NeuralNetwork:
    # Setting neural network values.
    def __init__(self, input_layer_size, secret_layer_size, secret_layer_count, generation_count):
        self.secret_layer_count = secret_layer_count
        self.secret_layer_size = secret_layer_size
        self.input_layer_size = input_layer_size
        self.network_weight = []
        self.generation_count = generation_count
        self.generation_weight = secret_layer_size * secret_layer_size * (
                secret_layer_count - 1) + input_layer_size * secret_layer_size
        self.model_path = os.getcwd()

    # create network weights and prepare training data
    def set_up(self):
        self.create_network_weight()
        self.split_data()

    # load saved model from folder
    def load_model_by_path(self, path=None):
        with open(path, 'rb') as f:
            self = pickle.load(f)
            return self

    # save trained- model on folder.
    def save_model_by_path(self, path=None):
        if path is None:
            with open('../Models/AITO.dat', 'wb') as f:
                pickle.dump(self, f)
        else:
            with open(path, 'wb') as f:
                pickle.dump(self, f)

    # load saved model from folder
    def load_model_by_file(self, file):
        self = pickle.load(file)
        return self

    # save trained- model on folder.
    def save_model_by_file(self, file):
        pickle.dump(self, file)

    # create network weight for training model.
    def create_network_weight(self):
        for generation in range(self.generation_count):
            self.network_weight.append([])
            for i in range(self.generation_weight):
                self.network_weight[generation].append(round(random.uniform(-1.0, 1.0),
                                                             5) / 50)

    # generate new weights to compare old weights.
    def create_new_weights(self):
        new_data = []
        for i in range(len(self.network_weight)):
            new_data.append([])
            for j in range(len(self.network_weight[i])):
                new_data[i].append([])
                for t in range(len(self.network_weight[i][j])):
                    new_data[i][j].append(self.network_weight[i][j][t] + round(random.uniform(-1.0, 1.0),
                                                                               5) / 100)

        return new_data

    # parse train data for train ML model.
    def split_data(self):
        for generation in range(self.generation_count):
            temp_list = [[]]
            for k in self.network_weight[generation]:
                last_param = len(temp_list[len(temp_list) - 1])
                if last_param == self.secret_layer_size:
                    temp_list.append([])
                temp_list[len(temp_list) - 1].append(k)
            self.network_weight[generation] = temp_list.copy()

    # predict a estimation according to ML model.
    def predict(self, input_x):
        if self.inputIsNotValid(input_x):
            print('\033[1;31m' + "Invalid input, shape of data doesn't fit model.")
            print('\033[1;31m' + "Check predict function.")
            return []
        t = 0

        y = (np.dot(input_x, self.network_weight[0][0:self.input_layer_size]))

        index = 0
        for j in range(len(self.network_weight[0])):

            if j == self.input_layer_size + index * self.secret_layer_size:
                y = (
                    np.dot(
                        y,
                        self.network_weight[0][
                        self.input_layer_size + self.secret_layer_size * index: self.input_layer_size + self.secret_layer_size * index + self.secret_layer_size]))
                index = index + 1
                t = t + 1

        return y

    #
    def predict_with_current_weight(self, input_x, current_y):

        for i in range(self.generation_count):
            t = 0
            for x in input_x:
                if len(current_y[i]) < len(input_x):
                    current_y[i].append([])
                current_y[i][t] = (np.dot(x, self.network_weight[i][0:self.input_layer_size]))

                index = 0
                for j in range(len(self.network_weight[i])):
                    if j == self.input_layer_size + index * self.secret_layer_size:
                        current_y[i][t] = (
                            np.dot(
                                current_y[i][t],
                                self.network_weight[i][
                                self.input_layer_size + self.secret_layer_size * index: self.input_layer_size + self.secret_layer_size * index + self.secret_layer_size]))
                        index = index + 1
                t = t + 1
        return current_y

    # *--------------------------------------------------------------------------------------------------------------*

    def predict_for_Training(self, input_x, new_y, new_weights):
        y = []
        for i in range(self.generation_count):
            t = 0
            y.append([])
            for x in input_x:
                # if len(y[i]) < len(input_x):
                y[i].append([])
                y[i][t] = (np.dot(x, new_weights[i][0:self.input_layer_size]))

                index = 0
                for j in range(len(new_weights[i])):
                    if j == self.input_layer_size + index * self.secret_layer_size:
                        y[i][t] = (
                            np.dot(
                                y[i][t],
                                new_weights[i][
                                self.input_layer_size + self.secret_layer_size * index: self.input_layer_size + self.secret_layer_size * index + self.secret_layer_size]))
                        index = index + 1
                t = t + 1
        return y

    def generate_new_population(self, output_y, current_result):

        total_current = []
        for i in range(self.generation_count):
            total_current.append([0])

        for i in range(self.generation_count):
            for t in range(len(output_y)):
                for j in range(len(output_y[0])):
                    total_current[i] = total_current[i] + abs(output_y[t][j] - current_result[i][t][j])
        min_weight = self.network_weight[total_current.index(min(total_current))]

        for i in range(self.generation_count):
            self.network_weight[i] = min_weight

    def comparing_weights(self, current_result, new_result, output_y, new_weights):
        total_new = []
        total_current = []
        for i in range(self.generation_count):
            total_new.append([0])
            total_current.append([0])

        for i in range(self.generation_count):
            for t in range(len(output_y)):
                for j in range(len(output_y[0])):
                    total_new[i] = total_new[i] + abs(output_y[t][j] - new_result[i][t][j])
                    total_current[i] = total_current[i] + abs(output_y[t][j] - current_result[i][t][j])

        for i in range(self.generation_count):
            if total_new[i] < total_current[i]:
                self.network_weight[i] = new_weights[i]
            else:
                pass

    def fit(self, input_x, output_y, iteration, genetic_iteration):

        if self.inputIsNotValid(input_x):
            print('\033[1;31m' + "Invalid input, shape of data doesn't fit model.")
            print('\033[1;31m' + "Check fit function.")
            sys.exit()
        current_y = []  # predict output by current network weight
        new_y = []  # predict output by make-up network weight

        for i in range(self.generation_count):
            current_y.append([])
            new_y.append([])

        for generation in range(genetic_iteration):
            for rep in range(iteration):
                updt(iteration * genetic_iteration, (generation * rep + rep))

                new_weights = self.create_new_weights()

                current_result = self.predict_for_Training(input_x, current_y, self.network_weight)

                new_result = self.predict_for_Training(input_x, new_y, new_weights)

                # find best network weight on self.network_weight generations
                self.comparing_weights(current_result, new_result, output_y, new_weights)

            self.generate_new_population(output_y, current_result)

    def inputIsNotValid(self, input_x):

        if type(input_x[0]) is int:
            if self.input_layer_size != len(input_x):
                return True
            return False

        else:

            if self.input_layer_size != len(input_x[0]):
                return True
            return False
