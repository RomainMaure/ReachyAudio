import nltk
import json
import random
import pickle
import tflearn
import numpy as np
from tensorflow.python.framework import ops
from nltk.stem.lancaster import LancasterStemmer

stemmer = LancasterStemmer()
CONFIDENCE_THRESHOLD = 0.7


class ReachyAudioAnswering():
    """ This class implements a small neural network
        allowing Reachy to answer to simple questions.
        To make it flexible, it uses sentence tokenizing
        and word stemming such that the network can provide
        answers to sentences different to the one used for
        the training. These input sentences have to remain
        close to the training sentences however.
    """
    
    def __init__(self):
        """ Train the model of the network or load
            it if it already exists.
        """
        
        # Load the json file containing the training data
        with open("intents.json") as myFile:
            self.data = json.load(myFile)

        # Load the data necessary to the initialization
        # of the network if the training has already been
        # done before, create it otherwise
        try:
            with open("data.pickle", "rb") as f:
                self.words, self.labels, train_input, train_target = pickle.load(f)
        except:
            self.words = []    # Contain all the different stemmed words constituing the patterns
            self.labels = []   # Contain all the different intents of the input sentences (patterns)
            docs_x = []        # Contain the training sentences of the network
            docs_y = []        # Contain the corresponding intent of a tokenized pattern
            train_input = []   # Contain the training inputs of the network
            train_target = []  # Contain the expected output for the training of the network

            # Extract the data from the json file
            for intent in self.data["intents"]:
                for pattern in intent["patterns"]:
                    wrds = nltk.word_tokenize(pattern)
                    self.words.extend(wrds)
                    docs_x.append(pattern)
                    docs_y.append(intent["tag"])

                if intent["tag"] not in self.labels:
                    self.labels.append(intent["tag"])


            # Apply word stemming i.e. find the root of the word (ex: happened -> happen)
            self.words = [stemmer.stem(w.lower()) for w in self.words if w != "?"]
            
            # transform to set to remove doublons 
            self.words = sorted(list(set(self.words)))
            
            self.labels = sorted(self.labels)

            out_empty = [0 for _ in range(len(self.labels))]
            

            # Transform each training sentence into a bag of words (an input for the network)
            for x, doc in enumerate(docs_x):
                bag = self.bag_of_words(doc).tolist()

                # Expected output
                output_row = out_empty[:]
                output_row[self.labels.index(docs_y[x])] = 1

                # We add the input and the expected output to the training set
                train_input.append(bag)
                train_target.append(output_row)


            train_input = np.array(train_input)
            train_target = np.array(train_target)
            
            # We store the computed training set for future uses
            with open("data.pickle", "wb") as f:
                pickle.dump((self.words, self.labels, train_input, train_target), f)


        # Initialization of the neural network
        ops.reset_default_graph()

        net = tflearn.input_data(shape = [None, len(train_input[0])])
        net = tflearn.fully_connected(net, 8)
        net = tflearn.fully_connected(net, 8)
        net = tflearn.fully_connected(net, len(train_target[0]), activation = "softmax")
        net = tflearn.regression(net)

        # Load the model if it already exists, train it otherwise
        try:
            print("Loading answering model...")
            self.model = tflearn.DNN(net)
            self.model.load("model.tflearn")
            print("Loading answering model: Done")
        except:
            print("Training answering model...")
            self.model = tflearn.DNN(net)
            self.model.fit(train_input, train_target, n_epoch = 1000, batch_size = 8, snapshot_epoch = False)
            self.model.save("model.tflearn")
            print("Training answering model: Done")


    def bag_of_words(self, input_sentence):
        """ Compute a bag of words that will be used as
            input for the network. A bag of words is a vector
            whose length correspond to the "vocabulary" known
            by the network (all the different words composing
            the sentences of the training set). For each word
            of the vocabulary, if this word is present in the
            input sentence, then the vector contains a 1,
            otherwise it contains a 0.

            :param input_sentence: The sentence to be answered.
            :return: The bag of word corresponding to the input sentence.
        """
        
        bag = []

        # Tokenize the input sentence and apply word stemming
        # on each of the tokenized words
        sentence_words = nltk.word_tokenize(input_sentence)
        stemmed_words = [stemmer.stem(word.lower()) for word in sentence_words]

        # Fill the vector
        for w in self.words:
            if w in stemmed_words:
                bag.append(1)
            else:
                bag.append(0)

        return np.array(bag)
    

    def answer(self, input_sentence):
        """ Allow Reachy to answer to a question similar to
            the ones used for the training of the network.

            :param input_sentence: The sentence to be answered.
            :return: The detected intent of the input sentence
                     (None if the intent could not be detected).
            :return: The answer to the input sentence.
        """
        
        # Compute the output of the model with respect to the input sentence
        results = self.model.predict([self.bag_of_words(input_sentence)])[0]
        
        # Take the most confident output as the result
        results_index = np.argmax(results)
        intent = self.labels[results_index]

        # Provide an answer only if the network
        # was confident enough about his output
        if results[results_index] > CONFIDENCE_THRESHOLD:
            for tg in self.data["intents"]:
                if tg["tag"] == intent:
                    # The response is picked randomly among the ones
                    # related to the detected input sentence intent
                    responses = tg["responses"]
                    answer = random.choice(responses)
                    break
        else:
            intent = None
            answer = "I didn't get that, can you try again ?"
            
        return intent, answer
