"""This module defines the ReachyAudioAnswering class."""

import nltk
import json
import torch
import random
import pickle
from nltk.stem.lancaster import LancasterStemmer

stemmer = LancasterStemmer()
CONFIDENCE_THRESHOLD = 0.7


class ReachyAudioAnswering():
    """ReachyAudioAnswering class.

    This class implements a small neural network allowing Reachy to answer to
    simple questions. To make it flexible, it uses sentence tokenizing and word
    stemming such that the network can provide answers to sentences different
    to the one used for the training. These input sentences have to remain
    close to the training sentences however.
    """

    def __init__(self):
        """Train the model of the network or load it if it already exists."""
        print("Initializing Reachy answering model...")

        # Load the json file containing the training data
        with open("utils/intents.json") as myFile:
            self.data = json.load(myFile)

        # Load the data necessary to the initialization
        # of the network if the training has already been
        # done before, create it otherwise
        try:
            with open("utils/data.pickle", "rb") as f:
                self.words, self.labels,
                train_input, train_target = pickle.load(f)
        except:
            # Contain all the different stemmed words constituing the patterns
            self.words = []

            # Contain all the different intents of the input sentences
            self.labels = []

            # Contain the training sentences of the network
            docs_x = []

            # Contain the corresponding intent of a tokenized pattern
            docs_y = []

            # Contain the training inputs of the network
            train_input = []

            # Contain the expected output for the training of the network
            train_target = []

            # Extract the data from the json file
            for intent in self.data["intents"]:
                for pattern in intent["patterns"]:
                    wrds = nltk.word_tokenize(pattern)
                    self.words.extend(wrds)
                    docs_x.append(pattern)
                    docs_y.append(intent["tag"])

                if intent["tag"] not in self.labels:
                    self.labels.append(intent["tag"])

            # Apply word stemming i.e. find the root of the word
            # (ex: happened -> happen)
            self.words = [stemmer.stem(w.lower()) for w in self.words
                          if w != "?"]

            # transform to set to remove doublons
            self.words = sorted(list(set(self.words)))

            self.labels = sorted(self.labels)

            out_empty = [0 for _ in range(len(self.labels))]

            # Transform each training sentence into a bag of words (an input
            # for the network) and compute the corresponding expected output
            for x, doc in enumerate(docs_x):
                bag = self.bag_of_words(doc)

                # Expected output
                output_row = out_empty[:]
                output_row[self.labels.index(docs_y[x])] = 1

                # We add the input and the expected output to the training set
                train_input.append(bag)
                train_target.append(output_row)

            # We store the computed training set for future uses
            with open("utils/data.pickle", "wb") as f:
                pickle.dump((self.words, self.labels,
                             train_input, train_target), f)

        # Load the model if it already exists, train it otherwise
        try:
            self.model = torch.load('utils/model.pth')
        except:
            self.model = torch.nn.Sequential(
                torch.nn.Linear(len(train_input[0]), 8),
                torch.nn.Linear(8, 8),
                torch.nn.Linear(8, len(train_target[0])),
                torch.nn.Softmax(dim=-1))

            self.train_model(torch.Tensor(train_input),
                             torch.Tensor(train_target))
            torch.save(self.model, 'utils/model.pth')

        print("Done")

    def train_model(self, train_input, train_target, nb_epochs=500,
                    show_metric=False):
        """Train the model of the network.

        :param data_input: The inputs of the training set.
        :param data_target: The corresponding outputs of the training set.
        :param nb_epochs: The number of times that the learning algorithm will
                          work through the entire training dataset.
        :param show_metric: Allow to show the performance of the model during
                            his training.
        """
        criterion = torch.nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters())

        for e in range(nb_epochs):
            # Compute the output of the model (forward pass)
            output = self.model(train_input)

            # Compute the error between the predicted output and the ground
            # truth
            loss = criterion(output, train_target)

            # Reset the sum of the gradients (the previous epoch should not
            # influence the current epoch)
            self.model.zero_grad()

            # Apply a backward pass
            loss.backward()

            # Update the parameters of the model with respect to the backward
            # pass previously done
            optimizer.step()

            # Compute the error of the current state of the network's model
            # with respect to the training set
            if show_metric:
                with torch.no_grad():
                    print("Epoch {} -> Train error = {:.02f} %".format(
                        e, self.compute_nb_errors(train_input, train_target) /
                        train_input.size(0) * 100))

    def compute_nb_errors(self, data_input, data_target):
        """Compute the number of classification errors of our network's model.

        :param data_input: The inputs of the testing set.
        :param data_target: The corresponding outputs of the testing set.
        :return: The number of classification errors made on the testing set.
        """
        nb_data_errors = 0

        # Compute the output of the model
        output = self.model(data_input)

        # Take the most confident output as the result
        predicted_classes = torch.argmax(output, 1)
        expected_classes = torch.argmax(data_target, 1)

        # Compare the prediction of the model with the ground truth
        for predicted_classe, expected_classe in zip(predicted_classes,
                                                     expected_classes):
            if predicted_classe != expected_classe:
                nb_data_errors = nb_data_errors + 1

        return nb_data_errors

    def bag_of_words(self, input_sentence):
        """Compute a bag of words that will be used as input for the network.

        A bag of words is a vector whose length correspond to the "vocabulary"
        known by the network (all the different words composing the sentences
        of the training set). For each word of the vocabulary, if this word is
        present in the input sentence, then the vector contains a 1, otherwise
        it contains a 0.

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

        return bag

    def answer(self, input_sentence):
        """Allow Reachy to answer to a question.

        :param input_sentence: The sentence to be answered.
        :return: The detected intent of the input sentence
                 (None if the intent could not be detected).
        :return: The answer to the input sentence.
        """
        # Compute the output of the model with respect to the input sentence
        results = self.model(torch.Tensor(self.bag_of_words(input_sentence)))

        # Take the most confident output as the result
        results_index = torch.argmax(results)
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
                    return intent, answer

        return None, "I didn't get that, can you try again ?"
