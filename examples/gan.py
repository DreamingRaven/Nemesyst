#!/usr/bin/env python3

# @Author: George Onoufriou <archer>
# @Date:   2018-09-27
# @Filename: gan.py
# @Last modified by:   georgeraven
# @Last modified time: 2018-12-11
# @License: Please see LICENSE file in project root

import copy
import datetime
import json
import os
import pickle
import pprint
import sys

import pandas as pd
from keras.layers import (LSTM, Activation, BatchNormalization, Dense,
                          LeakyReLU, Reshape)
from keras.models import Sequential
from src.data import Data

fileName = "gan.py"
prePend = "[ " + fileName + " ] "
# this is calling system wide nemesyst src.arg so if you are working on a branch
# dont forget this will be the main branch version of args


def main(args, db, log):

    # deep copy args to maintain them throught the rest of the program
    args = copy.deepcopy(args)
    log(prePend + "\n\tArg dict of length: " + str(len(args))
        + "\n\tDatabase obj: " + str(db) + "\n\tLogger object: " + str(log), 0)
    db.connect()
    gan = Gan(args=args, db=db, log=log)
    gan.debug()

    if(args["toTrain"]):
        gan.train()

    if(args["toTest"]):
        gan.test()

    if(args["toPredict"]):
        gan.predict()


class Gan():

    def __init__(self, args, db, log):
        self.db = db
        self.log = log
        self.epochs = 0
        self.args = args
        self.model_dict = None
        self.model_cursor = None
        self.prePend = "[ gan.py -> Gan ] "
        # this is a dictionary that should be referanced every time something
        # defaults or needs to check what is expected
        self.expected = {
            "type": "gan"
        }
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = str(args["tfLogMin"])

    def debug(self):
        self.log(self.prePend, 3)

    def train(self):
        # branch depending if model is to continue training or create new model
        if(self.args["toReTrain"] == True):
            # DONT FORGET IF YOU ARE RETRAINING TO CONCATENATE EXISTING STUFF LIKE EPOCHS
            modelPipe = self.getPipe(self.args["modelPipe"])
            self.model_dict = self.getModel(modelPipe)
            # check that the imported model is a gan
            # model is already overwritten when loading from database so self.model != None now
        else:
            self.args["type"] = self.expected["type"]
            self.model_dict = self.createModel()
        # show dict to user
        model_json = json.dumps(self.model_dict, indent=4,
                                sort_keys=True, default=str)
        self.log(model_json, 3)
        # for loop that cant go backwards that will iterate the difference
        # between the current epoch of the model and the desired amount
        for epoch in range(self.model_dict["epochs"], self.args["epochs"], 1):
            self.log("current EPOCH: (zero indexed): " + str(epoch), 3)

    def test(self, collection=None):
        # uses its own collection variable to allow it to be reused if testColl != coll
        collection = collection if collection is not None else self.args["coll"]
        # branch depending if model is already in memory to save request to database
        if(self.model_dict != None):
            None
        else:
            self.model_dict = self.getModel(
                self.getPipe(self.args["modelPipe"]))
        # now model should exist now use it to test

    def predict(self):
        # branch depending if model is already in memory to save request to database
        if(self.model_dict != None):
            None
        else:
            None

    def save(self):
        None

    # function responsible for creating whatever type of model is desired by the
    # user in this case GANs
    def createModel(self):
        # https://medium.com/@mattiaspinelli/simple-generative-adversarial-network-gans-with-keras-1fe578e44a87        # creating GAN
        # https://github.com/LantaoYu/SeqGAN/blob/master/sequence_gan.py

        self.log("Generator:", 0)
        generator = self.createGenerator()
        self.log("Discriminator:", 0)
        discriminator = self.createDiscriminator()
        generator.compile(
            optimizer=self.args["optimizer"], loss=self.args["lossMetric"])
        discriminator.compile(
            optimizer=self.args["optimizer"], loss=self.args["lossMetric"],
            metrics=[self.args["lossMetric"]])
        discriminator.trainable = False  # freezing weights

        gan = Sequential()
        gan.add(generator)
        gan.add(discriminator)
        self.log("GAN:", 0)
        gan.summary()
        gan.compile(loss=self.args["lossMetric"],
                    optimizer=self.args["optimizer"])

        try:
            # this is an optional dependancy that is only used for plots
            from keras.utils import plot_model
            plot_model(generator, to_file="generator.png")
            plot_model(generator, to_file="discriminator.png")
            plot_model(gan, to_file="GAN.png")
        except ModuleNotFoundError:
            self.log(
                "ModuleNotFoundError: could not plot models as likeley 'pydot'"
                + " module not found please "
                + " consider installing if you wish to visualise models\n"
                + str(sys.exc_info()[0]) + " "
                + str(sys.exc_info()[1]), 1)

        model_dict = {
            "utc": datetime.datetime.utcnow(),
            "loss": None,
            "epochs": 0,
            "generator": generator,
            "discriminator": discriminator,
            "gan": gan,
        }
        return model_dict

    def createGenerator(self):
        model = Sequential()
        model.add(Dense(256, input_shape=(100,)))
        model.add(LeakyReLU(alpha=0.2))
        model.add(BatchNormalization(momentum=0.8))
        model.add(Dense(512))
        model.add(LeakyReLU(alpha=0.2))
        model.add(BatchNormalization(momentum=0.8))
        model.add(Dense(1024))
        model.add(LeakyReLU(alpha=0.2))
        model.add(BatchNormalization(momentum=0.8))
        model.add(Dense(self.args["timeSteps"] *
                        self.args["dimensionality"], activation='tanh'))
        model.add(
            Reshape((self.args["timeSteps"], self.args["dimensionality"])))
        model.summary()
        return model

    def createDiscriminator(self):
        model = Sequential()
        # model.add(Flatten(input_shape=self.SHAPE))
        model.add(Dense(self.args["timeSteps"] * self.args["dimensionality"],
                        input_shape=(self.args["timeSteps"], self.args["dimensionality"])))

        model.add(LeakyReLU(alpha=0.2))
        model.add(
            Dense(int((self.args["timeSteps"] * self.args["dimensionality"]) / 2)))
        model.add(LeakyReLU(alpha=0.2))

        model.add(Dense(1, activation='sigmoid'))
        model.summary()
        return model

    def getModel(self, model_pipe=None):
        # modify keras witrh get and set funcs to be able to unserialise the data
        self.make_keras_picklable()
        query = model_pipe if model_pipe is not None else {}
        self.log(self.prePend + "db query: " + str(query), 0)
        # get model cursor to most recent match with query
        self.model_cursor = self.db.getMostRecent(
            query=query, collName=self.args["modelColl"])
        # get a dictionary of key:value pairs of this document from query
        model_dict = (
            pd.DataFrame(list(self.model_cursor))
        ).to_dict('records')[0]
        # self.model = pickle.loads(self.model_dict["model_bin"])
        # self.compile()
        if(model_dict["type"] != self.expected["type"]):
            raise RuntimeWarning(
                "The model retrieved using query: " + str(model_pipe)
                + " gives: " + str(model_dict["type"])
                + ", which != expected: " +  self.expected["type"])
        return model_dict

    def getPipe(self, pipePath):
        with open(pipePath) as f:
            return json.load(f)

    def make_keras_picklable(self):
        import tempfile
        import keras.models
        import h5py

        def __getstate__(self):
            model_str = ""
            with tempfile.NamedTemporaryFile(suffix='.hdf5', delete=True) as fd:
                keras.models.save_model(self, fd.name, overwrite=True)
                model_str = fd.read()
                d = {'model_str': model_str}
                return d

        def __setstate__(self, state):
            with tempfile.NamedTemporaryFile(suffix='.hdf5', delete=True) as fd:
                fd.write(state['model_str'])
                fd.flush()
                model = keras.models.load_model(fd.name)
                self.__dict__ = model.__dict__

        cls = keras.models.Model
        cls.__getstate__ = __getstate__
        cls.__setstate__ = __setstate__
