from keras.models import Sequential
from keras.layers import Dense, Dropout
from sklearn import preprocessing
from sklearn.metrics import classification_report, precision_score, recall_score, auc, roc_curve
import pandas as pd
import numpy as np

from preprocessing.data_utils import load_data, split_train_val_test, split_abundant_target, data_target, DATA_FINAL_PICKLE

# fix random seed for reproducibility
seed = 7
np.random.seed(seed)


class NeuralNets:
    def __init__(self):
        self.load_and_split()

    def load_and_split(self):
        data_df = load_data('../data/{filename}'.format(filename=DATA_FINAL_PICKLE),
                            drop_cols=['count', 'click', 'basket', 'revenue'],
                            mode='pkl')
        self.train_df, self.val_df, self.test_df = split_train_val_test(data_df)

    def preprocess_train(self):
        zero_df = self.train_df[self.train_df['order'] == 0]
        one_df = self.train_df[self.train_df['order'] == 1]

        ratio = round(zero_df.shape[0] / one_df.shape[0])

        for zero_df in split_abundant_target(zero_df, ratio):
            yield data_target(pd.concat([one_df, zero_df]), 'order')

    @staticmethod
    def preprocess_data(df):
        df, target = data_target(df, 'order')
        data = preprocessing.normalize(df, axis=1)
        return data, target

    @staticmethod
    def simple_nn(train_data, train_target, val_data, val_target, class_weight=None):
        model = Sequential()
        model.add(Dense(256, activation='relu', input_dim=train_data.shape[1]))
        model.add(Dense(128, activation='relu', input_dim=100))
        model.add(Dense(32, activation='relu', input_dim=100))
        model.add(Dense(1, activation='sigmoid'))
        model.compile(optimizer='rmsprop',
                      loss='binary_crossentropy',
                      metrics=['accuracy'])

        model.fit(train_data, train_target,
                  validation_data=(val_data, val_target),
                  epochs=1,
                  class_weight=class_weight,
                  batch_size=128)
        # model.save('simple_nn_v1.h5')
        return model

    # def complex_nn(self):
    #     print('complex nn')
    #     model = Sequential([
    #         Dense(256, activation='relu', input_dim=self.train_df.shape[1]),
    #         Dropout(0.8),
    #         Dense(128, activation='relu'),
    #         Dropout(0.4),
    #         Dense(32, activation='relu'),
    #         Dense(1, activation='sigmoid'),
    #     ])
    #     model.compile(optimizer='rmsprop',
    #                   loss='binary_crossentropy',
    #                   metrics=['accuracy'])
    #
    #     class_weights = class_weight.compute_class_weight('auto', np.unique(self.train_target), self.train_target)
    #     print('class weights')
    #     print(class_weights)
    #     model.fit(self.train_df, self.train_target,
    #               validation_data=(self.val_df, self.val_target),
    #               epochs=1)
    #     model.save('complex_nn_v1.h5')
    #     return model

    @staticmethod
    def describe(target_true, target_pred):
        report = classification_report(target_true, target_pred)
        print()
        print('classification report')
        print(report)
        precision = precision_score(target_true, target_pred)
        print('precision score')
        print(precision)
        recall = recall_score(target_true, target_pred)
        print('recall score')
        print(recall)
        fpr, tpr, thresholds = roc_curve(target_true, target_pred, pos_label=2)
        auc_metric = auc(fpr, tpr)
        print('auc')
        print(auc_metric)


if __name__ == '__main__':
    nn = NeuralNets()

    val_data, val_target = nn.preprocess_data(nn.val_df)
    test_data, test_target = nn.preprocess_data(nn.test_df)

    for train_df, train_target in nn.preprocess_train():
        train_data = preprocessing.normalize(train_df, axis=1)
        model = nn.simple_nn(train_data, train_target, val_data, val_target)
        print()
        print('target preds')
        target_pred = model.predict_classes(val_data)
        nn.describe(val_target, target_pred)

    train_data, train_target = nn.preprocess_data(nn.train_df)

    model = nn.simple_nn(train_data, train_target, val_data, val_target)
    print()
    print('target preds')
    target_pred = model.predict_classes(val_data)
    nn.describe(val_target, target_pred)

    model = nn.simple_nn(train_data, train_target, val_data, val_target, class_weight={0: 1., 1: 2.2})
    print()
    print('target preds')
    target_pred = model.predict_classes(val_data)
    nn.describe(val_target, target_pred)
