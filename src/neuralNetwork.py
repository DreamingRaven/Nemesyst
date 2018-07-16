#!/usr/bin/env python3

# @Author: George Onoufriou <archer>
# @Date:   2018-07-02
# @Filename: NeuralNetwork.py
# @Last modified by:   archer
# @Last modified time: 2018-07-16
# @License: Please see LICENSE file in project root



import pickle
import os, sys
from keras.models import Sequential
from keras.layers import Dense, Activation, LSTM



# link for getting distinct values in collection for test train splitting
# http://api.mongodb.com/python/1.4/api/pymongo/collection.html#pymongo.collection.Collection.distinct



class NeuralNetwork():



    home = os.path.expanduser("~")
    fileName = "neuralNetwork"
    prePend = "[ " + fileName + " ] "



    def __init__(self, db, pipeline, args, logger=print):

        self.log = logger
        self.db = db
        self.pipeline = pipeline
        self.args = args
        self.cursor = None
        self.log(self.prePend + "NN.init() success", 3)



    def getCursor(self, pipeline=None):

        if(self.cursor == None) or (pipeline != None):
            pipeline = pipeline if pipeline is not None else self.pipeline
            self.db.connect()
            # can i just point out how smooth the next line is and the complex
            # -ity that is going on behind the scenes
            self.cursor = self.db.getData(pipeline=pipeline)



    def debug(self):
        self.log(self.prePend       + "\n"  +
                 "\tdb obj: " + str(self.db)  + "\n"  +
                 "\tdb pipeline: " + str(self.pipeline)  + "\n"  +
                 "\tdb cursor: " + str(self.cursor)  + "\n"  +
                 "\tlogger: " + str(self.log),
                 0)


    # this just seeks to control where the model is created from,
    # either retrievef from database or compiled for the first time
    def autogen(self):

        # check cursor has been created atleast before attempting to use it
        if(self.cursor != None):
            # adjust keras so it can save its binary to databases and declare vars
            self.make_keras_picklable()
            self.generateModel()
            self.compile()

        raise NotImplementedError('NN.autogen() not currentley implemented')


    def generateModel(self):
        if( "lstm" == self.args["type"]):
            self.lstm()
        elif("rnn" == self.args["type"]):
            self.rnn()



    def compile(self):

        if(self.model != None):
            None
        raise NotImplementedError('NN.compile() not currentley implemented')


    def lstm(self):
        self.log(self.prePend + "Creating LSTM", -1)
        model = Sequential()
        self.model = model



    def rnn(self):
        self.log(self.prePend + "Creating RNN", -1)
        model = Sequential()
        self.model = model



    def loadModel(self):
        None
        raise NotImplementedError('NN.loadModel() not currentley implemented')



    def saveModel(self):
        None
        raise NotImplementedError('NN.saveModel() not currentley implemented')



    def train(self):
        None
        raise NotImplementedError('NN.tain() not currentley implemented')



    def test(self):
        None
        raise NotImplementedError('NN.test() not currentley implemented')



    def make_keras_picklable(self):
        import keras.models
        import h5py

        def __getstate__(self):
            model_str = ""
            with tempfile.NamedTemporaryFile(suffix='.hdf5', delete=True) as fd:
                keras.models.save_model(self, fd.name, overwrite=True)
                model_str = fd.read()
                d = { 'model_str': model_str }
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
