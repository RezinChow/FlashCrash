# -*- coding: utf-8 -*-
import random
import gym
import numpy as np
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
import time

EPISODES = 20000

class agent:
    def __init__(self,initasset):
        self.asset = initasset
        self.holdunit = 0
        self.ifhold = 0
        self.epsilon = 0.9999
        self.epsilon_de = 0.99995
        self.learning_rate = 0.005
        self.buyprice = 0
        self.sellprice= 0
        self.buylist = deque(maxlen=10)
        self.selllist = deque(maxlen=10)
        self.trainlist = deque(maxlen=1000)
        self.model = self._build_model()
        self.model2= self._build_model2()
        self.buylimit = 0.00001
    
    #init model structure
    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(20, input_dim=10, activation='relu'))
        model.add(Dense(20, activation='relu'))
        model.add(Dense(5, activation='relu'))
        model.add(Dense(1, activation='linear'))
        model.compile(loss='mse',
                      optimizer=Adam(lr=self.learning_rate))
        return model
    
    #init model structure
    def _build_model2(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(20, input_dim=20, activation='relu'))
        model.add(Dense(40, activation='relu'))
        model.add(Dense(8, activation='relu'))
        model.add(Dense(1, activation='linear'))
        model.compile(loss='mse',
                      optimizer=Adam(lr=self.learning_rate))
        return model


    def buy(self,assetprice):
        self.ifhold = 1
        self.asset = 0.2 * self.asset
        self.holdunit = self.asset*4 / assetprice

    def sell(self,assetprice):
        self.ifhold = 0
        sellasset = self.holdunit * assetprice
        self.asset = self.asset + sellasset
        self.holdunit = 0
    
    #收集打包卖出和买入状态
    def gettrade(self):
        print(self.buylist)
        self.trainlist.append((self.buylist,self.selllist,self.buyprice,self.sellprice))
        
    #随机交易发生器1
    def actrandom(self,assetprice):
        if np.random.rand() < self.esp:
            if np.random.rand() < 0.5:
                if self.ifhold == 1:
                    self.sell(assetprice)

                    return 0
                else:
                    print('no trade')
                    return 0
            else:
                if self.ifhold == 0:
                    self.buy(assetprice)
                    
                    return int(np.random.rand()*30)
                else:
                    print('no trade')
                    return 0
        else:
            pass

    #随机交易发生器2
    def actrandom2(self,assetprice,currentlist):
        #if np.random.rand() < self.esp:
        if self.ifhold == 0:
            if np.random.rand()<0.4:
                self.buy(assetprice)
                self.buyprice = assetprice
                self.buylist = currentlist
                return int(np.random.rand()*20)+2
            else:
                print("no trade")
                return 0
        if self.ifhold == 1:
            self.sell(assetprice)
            self.sellprice = assetprice
            self.selllist = currentlist
            agent1.gettrade()
            #print(agent1.trainlist)
            return 0
    
    #intelligence action buy
    def actintellbuy(self,assetprice,currentlist):
        state = np.reshape(currentlist, [1, 10])
        print(self.model.predict(state))
        print('!!')
        if self.model.predict(state)>self.buylimit:
            self.buyprice = assetprice
            self.buylist = currentlist
            if self.buylimit < 0.05:
                self.buylimit = self.buylimit + 0.001
            self.buy(assetprice)
            print("intell buy")
    
    #intelligence action sell
    def actintellsell(self,assetprice,buylist,currentlist):
        state = np.reshape([buylist,currentlist], [1, 20])
        print(self.model2.predict(state))
        print('!!！！')
        if ((assetprice - agent1.buyprice)/agent1.buyprice)>0.1:
            self.sellprice = assetprice
            self.selllist = currentlist
            self.sell(assetprice)
            print("intell sell")
        elif self.model2.predict(state)>0.05:
            self.sellprice = assetprice
            self.selllist = currentlist
            self.sell(assetprice)
            print("intell sell")


    def trainsell(self,batch_size):
        minibatch = random.sample(self.trainlist,batch_size)
        for buylist,selllist,buyprice,sellprice in minibatch:
            reward = (sellprice-buyprice)/buyprice
            state = [buylist,selllist]
            state = np.reshape(state, [1, 20])
            reward = np.reshape(reward,[1,1])
            self.model2.fit(state,reward,epochs=1,verbose=0)
            if self.epsilon>0.05:
                self.epsilon = self.epsilon*self.epsilon_de
    
    #train buy action
    def trainbuy(self,batch_size):
        minibatch = random.sample(self.trainlist,batch_size)
        for buylist,selllist,buyprice,sellprice in minibatch:
            #print(buylist)
            #print(selllist)
            #print('buyprice',buyprice)
            #print('sellprice',sellprice)
            reward = (sellprice-buyprice)/buyprice
            #reward = np.array(reward)
            state = np.reshape(buylist, [1, 10])
            reward = np.reshape(reward,[1,1])
            #print(buylist.shape)
            #print(type(buyprice))
            self.model.fit(state,reward,epochs=1,verbose=0)

#模拟股票
class stock:
    def __init__(self,initprice):
        self.price = initprice

    def pricechange(self):
        b = np.random.rand()
        if b<0.45:
            b = 0.97
        elif b<0.92:
            b = 1.03
        else:
            b = 1
        return b


if __name__ == "__main__":
    stock1 = stock(100)
    agent1 = agent(100)
    batch_size = 10
    m = 0
    #print(stock1.price)
    stepindex = 0
    listline = deque(maxlen=10)
    sellban = 0
    agent1.model.load_weights("w1-1.h5")
    agent1.model2.load_weights("w2-2.h5")
    for i in range(10000):
        #random stock price
        if stepindex == 0:
            a = np.random.rand()
            if a<0.2:
                stepindex = 5
                c = stock1.pricechange()
            elif a<0.4:
                stepindex = 3
                c = stock1.pricechange()
            else:
                c = stock1.pricechange()
                stock1.price = stock1.price * c
        if stepindex != 0:
            stock1.price = stock1.price * c
            stepindex = stepindex - 1
        
        #stock price limite
        if stock1.price>500:
            stock1.price = 502
        elif stock1.price<5:
            stock1.price = 4.9
        
        #record the most recent stock data
        listline.append(stock1.price)     
        
        #训练和使用模型
        if np.random.rand() < agent1.epsilon:
        #if m < 25:
            if sellban == 0:
                sellban = agent1.actrandom2(stock1.price,listline)
            else:
                print("no trade")
                sellban = sellban - 1
        else:
            if agent1.ifhold == 0:
                agent1.actintellbuy(stock1.price,listline)
            elif agent1.ifhold == 1:
                agent1.actintellsell(stock1.price,agent1.buylist,listline)
        print(agent1.epsilon)
        
        """
        #载入训练模型
        
        m = m + 1
        if m < 10:
            if sellban == 0:
                sellban = agent1.actrandom2(stock1.price,listline)
            else:
                print("no trade")
                sellban = sellban - 1
        else:
            if agent1.ifhold == 0:
                agent1.actintellbuy(stock1.price,listline)
            elif agent1.ifhold == 1:
                agent1.actintellsell(stock1.price,agent1.buylist,listline)
        """
        
        
        print('############')
        print(stock1.price)
        print('############')
        if i%1 == 0:
            print('------------')
            print(agent1.asset)
            #print(agent1.buylist)
            print('------------')
        #print("eps",len(agent1.trainlist))
        if len(agent1.trainlist)>=batch_size:
            agent1.trainbuy(batch_size)
            agent1.trainsell(batch_size)
            
            #agent1.trainsell(10)
        #time.sleep(0.002)
        print(i)
        #print("eps",agent1.epsilon)
    agent1.sell(stock1.price)
    print(agent1.asset)

    agent1.model.save_weights("w1-1.h5")
    agent1.model2.save_weights("w2-2.h5")
    agent1.model.save("a1.h5")
    agent1.model2.save("a2.h5")