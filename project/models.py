# -*- coding: utf-8 -*-
import random
import gym
import numpy as np
import pandas as pd
from collections import deque
from keras.models import Sequential
from keras.models import Model
from keras.layers import Input,Dense
from keras.optimizers import Adam
from tensorflow import keras
from tensorflow.keras import layers
from keras.utils import plot_model
import time
from keras.layers import concatenate

import math #this is for ln()

Coe_ln = 0.5
Coe_ln_2 = 1
Coe_g = 0.2

class s:
    def __init__(self, initasset):
        self.asset = initasset  # 个人资产
        self.holdunit = 0
        self.ifhold = 0
        self.epsilon = 0.9999
        self.epsilon_de = 0.99995
        self.learning_rate = 0.005
        self.buyprice = 0
        self.sellprice = 0
        self.trainlist = deque(maxlen=1000)
        #self.model = self._build_model()
        #self.model2 = self._build_model2()
        self.buylimit = 0.00001
        # add
        self.name = None
        # 个人盈利与持股状态
        #self.agent_info_df = []
        #self.agent_info_df.loc[:, :] = 0  # 初始化所有数据为0
        # 实时交易 df表
        self.realtime_trading_df = []
        #个人的 buylist_array,selllist_array
        # listline = deque(maxlen=10)  存储股票的state
        #self.buylist_array = [deque(maxlen=10) for i in range(len(stock_list))]  # listline_array 存储 所有stock 的lisitline
        #self.selllist_array = [deque(maxlen=20) for i in range(len(stock_list))]  # listline_array 存储 所有stock 的lisitline
        #上次 的交易状态,0 ：卖  1：买
        self.last_trading_state  = 0  #
        #self leveraged_contract
        self.contract_list = []
        self.contract_id= 0
        self.leveraged_contract_df = []
        self.leveraged_contract_df = pd.DataFrame(self.leveraged_contract_df,columns=["stock_id","buyprice", "own_principal", "bank_id", "interest_rate", "lever_rate", "force_sellprice"])
        self.model_buy = self._build_model_buy()
        self.model_v2 = self._model_v2()
        self.model_buy_v2 = self._build_model_v2()
        self.model_sell_v2 = self._build_model_v2()
        ###new list format###
        self.train_sell_list_v2 = deque(maxlen=100)
        self.train_buy_list_v2 =  deque(maxlen=100)

    def _model_v2(self):
        num_tags = 12  # Number of unique issue tags
        num_words = 10000  # Size of vocabulary obtained when preprocessing text data
        num_departments = 4  # Number of departments for predictions

        title_input = keras.Input(
            shape=(None,), name="title"
        )  # Variable-length sequence of ints
        body_input = keras.Input(shape=(None,), name="body")  # Variable-length sequence of ints
        tags_input = keras.Input(
            shape=(num_tags,), name="tags"
        )  # Binary vectors of size `num_tags`

        # Embed each word in the title into a 64-dimensional vector
        title_features = layers.Embedding(num_words, 64)(title_input)
        # Embed each word in the text into a 64-dimensional vector
        body_features = layers.Embedding(num_words, 64)(body_input)

        # Reduce sequence of embedded words in the title into a single 128-dimensional vector
        title_features = layers.LSTM(128)(title_features)
        # Reduce sequence of embedded words in the body into a single 32-dimensional vector
        body_features = layers.LSTM(32)(body_features)

        # Merge all available features into a single large vector via concatenation
        x = layers.concatenate([title_features, body_features, tags_input])

        # Stick a logistic regression for priority prediction on top of the features
        priority_pred = layers.Dense(1, name="priority")(x)
        # Stick a department classifier on top of the features
        department_pred = layers.Dense(num_departments, name="department")(x)

        # Instantiate an end-to-end model predicting both priority and department
        model = keras.Model(
            inputs=[title_input, body_input, tags_input],
            outputs=[priority_pred, department_pred],
        )
        return model

    def _build_model_buy(self):
        model = Sequential()
        model.add(Dense(20, input_dim=5, activation='linear'))
        model.add(Dense(40, activation='relu'))
        model.add(Dropout(0.4))
        model.add(Dense(8, activation='relu'))
        model.add(Dense(1, activation='linear'))
        parallel_model = multi_gpu_model(model, gpus=2)
        model.compile(loss='mse',
                      optimizer=Adam(lr=self.learning_rate))
        return model


    def _build_model_v2(self):
        # define two sets of inputs
        inputA = Input(shape=(50,))
        inputB = Input(shape=(50,))
        inputC = Input(shape=(10,))
        inputD = Input(shape=(1,))

        
        # the first branch operates on the first input
        x = Dense(20, activation="relu")(inputA)
        x = Dense(4, activation="relu")(x)
        x = Model(inputs=inputA, outputs=x)
        
        # the second branch opreates on the second input
        y = Dense(20, activation="relu")(inputB)
        y = Dense(4, activation="relu")(y)
        #y = Dense(2, activation="relu")(y)
        y = Model(inputs=inputB, outputs=y)

        c = Dense(5, activation="relu")(inputC)
        c = Dense(2, activation="relu")(c)
        c = Model(inputs=inputC, outputs=c)

        d = Dense(2, activation="relu")(inputD)
        d = Model(inputs=inputD, outputs=d)

        # combine the output of the two branches
        combined = concatenate([x.output, y.output,c.output,d.output])
        
        # apply a FC layer and then a regression prediction on the
        # combined outputs
        z = Dense(4, activation="relu")(combined)
        z = Dense(1, activation="linear")(z)
        
        # our model will accept the inputs of the two branches and
        # then output a single value
        model = Model(inputs=[x.input, y.input, c.input, d.input], outputs=z)
        model.compile(loss='mse',
                optimizer=Adam(lr=self.learning_rate))
        return model


        def int_act_buy_decision(self,current_short_price,current_long_price,buy_history,valuation):
            ob_0 = np.reshape(_x[0], [1, 50])
            ob_1 = np.reshape(_x[1], [1, 50])
            ob_2 = np.reshape(_x[2], [1, 10])
            ob_3 = np.reshape(_x[3], [1, 1])
            return self.model_buy_v2.predict([ob_0,ob_1,ob_2,ob_3])

        def int_act_sell_decision(self,current_short_price,current_long_price,buy_history,valuation):
            ob_0 = np.reshape(_x[0], [1, 50])
            ob_1 = np.reshape(_x[1], [1, 50])
            ob_2 = np.reshape(_x[2], [1, 10])
            ob_3 = np.reshape(_x[3], [1, 1])
            return self.model_sell_v2.predict([ob_0,ob_1,ob_2,ob_3])
            
            
        def trainbuy_v2(self,step,current_price,bitch_size):
            minibatch = random.sample(self.train_buy_list_v2 , batch_size)
            for _x in minibatch:
                _rb = (current_price - _x[4]) / (_x[4] * Coe_ln * math.log(step + 2.73 - _x[5]))
                Rb = _rb * (1 + Coe_g * _x[6]/_x[7]) / (Coe_ln_2 * math.log(step + 9 - _x[5],10))
                ob_0 = np.reshape(_x[0], [1, 50])
                ob_1 = np.reshape(_x[1], [1, 50])
                ob_2 = np.reshape(_x[2], [1, 10])
                ob_3 = np.reshape(_x[3], [1, 1])
                reward = np.reshape(Rb, [1, 1])
                self.model_buy_v2.fit([ob_0,ob_1,ob_2,ob_3], reward, epochs=1, verbose=0)
                if self.epsilon > 0.05:
                    self.epsilon = self.epsilon * self.epsilon_de
            

        def trainsell_v2(self,step,current_price,bitch_size):
            minibatch = random.sample(self.train_sell_list_v2 , batch_size)
            for _x in minibatch:
                _rb = (_x[4]- current_price ) / (_x[4] * Coe_ln * math.log(step + 2.73 - _x[5])) + (_x[4]-_x[8]) / (_x[8] * Coe_ln * math.log(step + 2.73 - _x[5]))
                Rb = _rb * (1 + Coe_g * _x[6]/_x[7])  / (Coe_ln_2 * math.log(step + 9 - _x[5],10))
                ob_0 = np.reshape(_x[0], [1, 50])
                ob_1 = np.reshape(_x[1], [1, 50])
                ob_2 = np.reshape(_x[2], [1, 10])
                ob_3 = np.reshape(_x[3], [1, 1])
                reward = np.reshape(Rb, [1, 1])
                self.model_sell_v2.fit([ob_0,ob_1,ob_2,ob_3], reward, epochs=1, verbose=0)#sell还没确定，先用共用买的这个吧
                if self.epsilon > 0.05:
                    self.epsilon = self.epsilon * self.epsilon_de



if __name__ == "__main__":
    agent = s(10000)
    plot_model(agent.model_buy_v2, show_shapes=True, to_file='model.png')
    state = [1,2,3,4,5]
    state2 =[6,7,8,9,10]
    state3 =[2,3,4]
    state4 =1
    state = np.reshape(state, [1, 5])
    state2 = np.reshape(state2, [1, 5])
    state3 = np.reshape(state3, [1,3])
    state4 = np.reshape(state4, [1,1])
    reward = 5
    reward = np.reshape(reward,[1,1])
    agent.model_buy_v2.fit([state,state2,state3,state4],reward,epochs=1,verbose=0)
