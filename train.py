import json
import numpy as np
import pickle
import random
import spacy

from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import SGD

file = 'intents.json'

# Library to manage English language
nlp = spacy.load('en_core_web_sm')
# Prepare the data
data_file = open(file).read()
data_json = json.loads(data_file)

# Classification accordingly to the data in the json file
documents = []
# Tags in the json file
tags = []
# All the words in lowercase
words = []
tokens_ignored = ['?', '!', ',', '.']

for intent in data_json['intents']:
    for pattern in intent['patterns']:
        for token in nlp(pattern):
            if token.text in tokens_ignored:
                continue

            if token.lemma_ != "-PRON-":
                documents.append((token.lemma_, intent['tag']))
                words.append(token.lemma_.lower())
            else:
                documents.append((token.text, intent['tag']))
                words.append(token.text.lower())

            if intent['tag'] not in tags:
                tags.append(intent['tag'])

# Clean up the tags and words
tags = sorted(list(set(tags)))
words = sorted(list(set(words)))

pickle.dump(tags, open('tags.pkl', 'wb'))
pickle.dump(words, open('words.pkl', 'wb'))

# Data to train
training = []

for doc in documents:
    coefficients = []
    pattern = doc[0]
    # Create the coefficient for each of the coefficients
    for w in words:
        coefficients.append(1) if w in pattern else coefficients.append(0)

    output = list([0] * len(tags))
    output[tags.index(doc[1])] = 1

    training.append([coefficients, output])

random.shuffle(training)
training = np.array(training)

# Split the training data
train_x = list(training[:,0])
train_y = list(training[:,1])

# Train
# Create model - 3 layers. First layer 128 neurons, second layer 64 neurons and 3rd output layer contains number of neurons
# equal to number of intents to predict output intent with softmax
model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))

# Compile model. Stochastic gradient descent with Nesterov accelerated gradient gives good results for this model
sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

#fitting and saving the model
hist = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)
model.save('chatbot_model.h5', hist)
