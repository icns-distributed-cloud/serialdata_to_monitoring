import pandas as pd
import numpy as np
import tensorflow as tf

f = pd.read_csv('./data.csv', encoding='cp949')
f.info()

# train
X = f[['temperature','humidity']]

from sklearn.model_selection import train_test_split
train, test = train_test_split(X, shuffle=False, test_size=0.25)


# scaling
from sklearn.preprocessing import MinMaxScaler
sc = MinMaxScaler()

# scaled data
train_sc = sc.fit_transform(train)
test_sc = sc.fit_transform(test)

# Transfrom data to pandas dataframe
# pandas is useful to make window for LSTM
train_sc_df = pd.DataFrame(train_sc, columns=['temperature','humidity'], index=train.index)
test_sc_df = pd.DataFrame(test_sc, columns=['temperature','humidity'], index=test.index)

train_sc_df.columns = train.columns
test_sc_df.columns = test.columns
column_list = list(train_sc_df)

train_sc_df.head()

# SlidingWindow generation
for s in reversed(range(1, 21)):
    tmp_train = train_sc_df[column_list].shift(s)
    tmp_test = test_sc_df[column_list].shift(s)

# column name
    tmp_train.columns = "shift_" + tmp_train.columns + "_" + str(-(s-21))
    tmp_test.columns = "shift_" + tmp_test.columns + "_" + str(-(s-21))

    train_sc_df[tmp_train.columns] = train_sc_df[column_list].shift(s)
    test_sc_df[tmp_test.columns] = test_sc_df[column_list].shift(s)

# drop space
X_train = train_sc_df.dropna().drop(['temperature','humidity'], axis=1)
y_train = train_sc_df.dropna()[['temperature','humidity']]
X_test = test_sc_df.dropna().drop(['temperature','humidity'], axis=1)
y_test = test_sc_df.dropna()[['temperature','humidity']]

# numpy expression by (.values)
X_train = X_train.values
X_test= X_test.values
y_train = y_train.values
y_test = y_test.values

print(X_train)
print(y_train)

# transform into 3-dimension (size, timestamp, feature)
X_train_t = X_train.reshape(X_train.shape[0], 20, 2)
X_test_t = X_test.reshape(X_test.shape[0], 20, 2)

print(X_train_t)
print(X_test_t)

print("Final Data")
print(X_train_t.shape)
print(X_test_t.shape)
print(y_train.shape)

from tensorflow.keras.layers import LSTM
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, SimpleRNN, Activation
from tensorflow.keras import optimizers

model = Sequential()
model.add(LSTM(50, input_shape=(20,2), return_sequences=True))
model.add(LSTM(50, input_shape=(20,2)))
model.add(Dense(50,activation='relu'))
model.add(Dense(25,activation='relu'))
model.add(Dense(2))

model.compile(loss='mse', optimizer = 'Adam', metrics = ['accuracy'])

hist = model.fit(X_train_t, y_train, epochs = 100, batch_size = 100)

print('## training loss and acc ##')
print(hist.history['loss'])
print(hist.history['accuracy'])

#plot_train_history(hist, 'loss & accuracy')

# save model
model.save('save_model_3.h5')

print("------------------------------------------------------------")
print("+----------------    Training finished    -----------------+")
print("------------------------------------------------------------")
