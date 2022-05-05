# -*- coding: utf-8 -*-
## This is the sample main function for all module
## Copyright: King's College London
## Author: Hefeng Zhou

import random
import gym
import numpy as np
import pandas as pd
import math
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
import matplotlib.pyplot as plt

import time

EPISODES = 20000

###global variable###
step = 1
# bank info  dataframe
bank_list = [i for i in range(3)]  # init stock-id stock_list = [0,1,2]
all_bank_info = []
all_bank_info = pd.DataFrame(all_bank_info, columns=["interest_rate", "lever_rate", "force_sell_rate"])
# save all information of dataframe
stock_list = [i for i in range(3)]  # init stock-id stock_list = [0,1,2]
all_stock_info = []
all_stock_info = pd.DataFrame(all_stock_info, columns=["cur_price",
                                                       "init_num", "total_value",
                                                       "rest_num", "init_price"])   #current price cur_price; initial number of shares：init_num; ：total_value ；rest number of shares：rest_num; init_price
##training queue
listline_array_short = [deque(maxlen=30) for i in range(len(stock_list))]
listline_array_long = [deque(maxlen=30) for i in range(len(stock_list))]


class Agent:
    def __init__(self, initasset, name):
        self.name = name
        self.asset = initasset  # self asset
        self.holdunit = 0
        self.ifhold = 0
        self.epsilon = 0.9999
        self.epsilon_de = 0.99995  # 0.8#0.99995
        self.learning_rate = 0.005
        self.buyprice = 0
        self.sellprice = 0
        self.trainlist = deque(maxlen=1000)
        self.model = self._build_model()
        self.model2 = self._build_model2()
        self.buylimit = 0.00001
        ###new list format###
        self.train_sell_list_v2 = deque(maxlen=100)
        self.train_buy_list_v2 = deque(maxlen=100)
        # profility 
        self.agent_info_df = []
        self.agent_info_df = pd.DataFrame(self.agent_info_df, columns=["hold_num", "profit"], index=stock_list)  # hold_num ; profit
        self.agent_info_df.loc[:, :] = 0  # initialize all data is 0
        # self buylist_array,selllist_array
        self.buylist_array = [deque(maxlen=10) for i in range(len(stock_list))]
        self.selllist_array = [deque(maxlen=10) for i in range(len(stock_list))]
        # self leveraged_contract
        self.contract_list = []
        self.contract_id = 0
        self.leveraged_contract_df = []
        self.leveraged_contract_df = pd.DataFrame(self.leveraged_contract_df,
                                                  columns=["stock_id", "buyprice", "own_principal",
                                                           "bank_id", "interest_rate", "lever_rate",
                                                           "force_sellprice", "buy_step"])

    # init model structure
    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(20, input_dim=10, activation='relu'))
        #model.add(Dropout(0.4))
        model.add(Dense(20, activation='relu'))
        model.add(Dense(5, activation='relu'))
        model.add(Dense(1, activation='linear'))
        model.compile(loss='mse',
                      optimizer=Adam(lr=self.learning_rate))
        return model

    # init model structure
    def _build_model2(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(20, input_dim=20, activation='relu'))
        #model.add(Dropout(0.4))
        model.add(Dense(40, activation='relu'))
        model.add(Dense(8, activation='relu'))
        model.add(Dense(1, activation='linear'))
        model.compile(loss='mse',
                      optimizer=Adam(lr=self.learning_rate))
        return model

    def leverage_buy(self, id, bank_id, own_principal):  # id:buy stock id ; bank_id ; own_principal; original asset
        global step
        # compute the ave buyprice
        current_sumvalue = all_stock_info.loc[id, "total_value"]
        lever_rate = all_bank_info.loc[bank_id, "lever_rate"]
        interest_rate = all_bank_info.loc[bank_id, "interest_rate"]
        trading_money = own_principal * (
                    lever_rate + 1)  #   allAssetBuy <- assetBuy * (1+leverageRate[bankId])
        static_cost = all_stock_info.loc[id, "init_num"]
        buy_ave_price = (((current_sumvalue + trading_money) + current_sumvalue) / 2) / static_cost
        holdunit = math.floor(trading_money / buy_ave_price)  # compute the holduint and get the floor int

        ###
        price_before_buy =  all_stock_info.loc[id,"cur_price"]

        # compute the force sellprice
        force_sell_rate = all_bank_info.loc[bank_id, "force_sell_rate"]
        force_sellprice = buy_ave_price * force_sell_rate
        buy_step = step  # get the current step
        # create the contract
        new_leverage_df = [[id, buy_ave_price, own_principal, bank_id, interest_rate, lever_rate, force_sellprice, buy_step]]
        new_leverage_df = pd.DataFrame(new_leverage_df, columns=["stock_id", "buyprice", "own_principal", "bank_id",
                                                                 "interest_rate", "lever_rate", "force_sellprice",
                                                                 "buy_step"],
                                       index=[self.contract_id])  # compensate is the int(holdint) self compensate
        self.leveraged_contract_df = self.leveraged_contract_df.append(new_leverage_df)
        # update stock
        all_stock_info.loc[id, "rest_num"] -= holdunit
        all_stock_info.loc[id, "total_value"] += trading_money
        all_stock_info.loc[id, "cur_price"] = all_stock_info.loc[id, "total_value"] / static_cost
        # update  self assest
        price_after_buy = all_stock_info.loc[id, "cur_price"]
        asset_cost = (price_before_buy + price_after_buy)/2 * holdunit
        dif_cost =  trading_money - asset_cost
        self.asset =  self.asset - own_principal + dif_cost  # compute the assest
        # update self buylist_array[]
        self.buylist_array[id].append(buy_ave_price)  # apeend buy_ave_price, update buylist
        print("create a new contract %d：" % self.contract_id)
        self.contract_id += 1
        print(new_leverage_df)

    def leverage_sell(self, contract_id):  # contract_id
        global step
        id = self.leveraged_contract_df.loc[contract_id, "stock_id"]
        buyprice = self.leveraged_contract_df.loc[contract_id, "buyprice"]
        own_principal = self.leveraged_contract_df.loc[contract_id, "own_principal"]
        lever_rate = self.leveraged_contract_df.loc[contract_id, "lever_rate"]
        interest_rate = self.leveraged_contract_df.loc[contract_id, "interest_rate"]
        #compute the sell ave price
        static_cost = all_stock_info.loc[id, "init_num"]
        sellunit = math.floor(own_principal * (1 + lever_rate) / buyprice)
        ##
        down_rate = (all_stock_info.loc[id, "cur_price"] - all_stock_info.loc[id, "init_price"]) / (
                    all_stock_info.loc[id, "init_num"] - all_stock_info.loc[id, "rest_num"])
        aftersell_price = all_stock_info.loc[id, "cur_price"] - down_rate * sellunit
        sell_ave_price = (all_stock_info.loc[id, "cur_price"] + aftersell_price) / 2

        # step
        buy_step = self.leveraged_contract_df.loc[contract_id, "buy_step"]
        sell_step = step
        self.leveraged_contract_df = self.leveraged_contract_df.drop(contract_id, axis=0)  # delete contract
        # trading_money
        trading_money = sell_ave_price * sellunit  # trading moneey in this step
        # update self assest
        earn_money = (sell_ave_price - buyprice) * sellunit
        self.asset += (own_principal + earn_money)
        # update stock
        all_stock_info.loc[id, "rest_num"] += sellunit
        all_stock_info.loc[id, "total_value"] -= trading_money
        all_stock_info.loc[id, "cur_price"] = all_stock_info.loc[id, "total_value"] / static_cost
        print("del a new contract %d：" % contract_id)

    def actinel_leverage_buy(self, own_principal):
        print("%s actinel_leverage " % self.name, end="")
        bank_id = random.choice(bank_list)  # bank
        buy_rate = []
        for id in stock_list:
            currentlist = listline_array[id]
            state = np.reshape(currentlist, [1, 10])
            buy_rate.append(self.model.predict(state))  # append all stock buy rate
        buy_id = np.argmax(buy_rate)
        self.leverage_buy(id=buy_id, bank_id=bank_id, own_principal=own_principal)

    def actinel_leverage_sell(self):
        print("%s actinel_leverage " % self.name, end="")
        self.contract_list = self.leveraged_contract_df.index.tolist()  # get exist contract list
        if self.contract_list != []:
            for contract_id in self.contract_list:
                id = self.leveraged_contract_df.loc[contract_id, "stock_id"]
                if self.leveraged_contract_df.loc[contract_id, "force_sellprice"] > all_stock_info.loc[
                    id, "cur_price"]:  # if current asset price lower than the contract limitation
                    print("boom force sell！！！！！！")
                    self.leverage_sell(contract_id)
                elif ((all_stock_info.loc[id, "cur_price"] - self.leveraged_contract_df.loc[contract_id, "buyprice"]) /
                      self.leveraged_contract_df.loc[contract_id, "buyprice"]) > 0.3:
                    if np.random.rand() > 0.2:  # if earn > 30% : 20% sell
                        self.leverage_sell(contract_id)
                        print(self.name, end="")
                        print("earn more than 30% sell！！！！！！")
                    else:
                        # compute the actnel_sell_rate
                        currentlist = listline_array[id]
                        state = np.reshape([self.buylist_array[id], currentlist], [1, 20])
                        if self.model2.predict(state) > 0.3:  #  actinel sell rate > 30%
                            self.leverage_sell(contract_id)
                            print("actinel lever sell！！！！！！")
        else:
            print("contract_list empty")

    def get_stock_hold_list(self):
        hold_list = []
        for id in stock_list:
            if self.agent_info_df.loc[id, "hold_num"] > 0:
                hold_list.append(id)
        return hold_list

    # trading method buy or sell
    def buy(self, id, rate):  #
        # compute the buy_ave_price
        current_sumvalue = all_stock_info.loc[id, "total_value"]
        trading_money = rate * self.asset
        static_cost = all_stock_info.loc[id, "init_num"]  # init_num  is stock'static
        buy_ave_price = (((current_sumvalue + trading_money) + current_sumvalue) / 2) / static_cost  # the average stock price in this buy round
        holdunit = math.floor(trading_money / buy_ave_price)  # compute the holduint and get the floor int
        print("buy %d hold!!!"%holdunit)
        # update self assest
        old_asset = self.asset
        self.asset -= trading_money
        ###
        price_before_buy = all_stock_info.loc[id, "cur_price"]

        # update stock
        all_stock_info.loc[id, "rest_num"] -= holdunit
        all_stock_info.loc[id, "total_value"] += trading_money
        all_stock_info.loc[id, "cur_price"] = all_stock_info.loc[id, "total_value"] / static_cost
        ###
        price_after_buy = all_stock_info.loc[id, "cur_price"]
        asset_cost = (price_before_buy + price_after_buy) / 2 * holdunit
        dif_cost = trading_money - asset_cost

        # update self.agent_info_df
        self.agent_info_df.loc[id, "hold_num"] += holdunit
        self.agent_info_df.loc[id, "profit"] -= trading_money
        self.agent_info_df.loc[id, "profit"] += dif_cost
        self.asset += dif_cost
        # update self buylist_array[]
        self.buylist_array[id].append(buy_ave_price)  # apeend  buy_ave_price
        # update train_buy_list
        self.update_train_buy_list(id, trading_money, old_asset)
        print("buy stock%d %f"%(id,trading_money))
        print("%s asset: %f"%(self.name,self.asset))

    def sell(self, id, rate):
        static_cost = all_stock_info.loc[id, "init_num"]
        holdunit = self.agent_info_df.loc[id, "hold_num"]
        sellunit = math.floor(holdunit * rate)  # sellunit = holdunit * rate, floor int
        ###
        down_rate = (all_stock_info.loc[id, "cur_price"] - all_stock_info.loc[id, "init_price"]) / (
                    all_stock_info.loc[id, "init_num"] - all_stock_info.loc[id, "rest_num"])
        aftersell_price = all_stock_info.loc[id, "cur_price"] - down_rate * sellunit
        sell_ave_price = (all_stock_info.loc[id, "cur_price"] + aftersell_price) / 2
        return_asset = sell_ave_price * sellunit

        trading_money = sell_ave_price * sellunit  # sell order the rate
        # update self assest
        old_asset = self.asset
        self.asset += trading_money
        # update stock
        all_stock_info.loc[id, "rest_num"] += sellunit
        all_stock_info.loc[id, "total_value"] -= trading_money
        ###
        # all_stock_info.loc[id,"total_value"] -= trading_money

        all_stock_info.loc[id, "cur_price"] = all_stock_info.loc[id, "total_value"] / static_cost
        # update self.agent_info_df
        self.agent_info_df.loc[id, "hold_num"] -= sellunit
        self.agent_info_df.loc[id, "profit"] += trading_money  # if profit
        #update self selllist_array[]
        self.selllist_array[id].append(sell_ave_price)  # apeend  sell_ave_price  in order to selllist
        #update train_sell_list
        self.update_train_sell_list(id, trading_money, old_asset)
        print("sell stock%d %d" % (id, trading_money))

    def actrandom_buy(self):
        print("%s " % self.name, end="")
        if np.random.rand() < 0.8:
            buy_id = random.choice(stock_list)  # choose the buy stock
            print("actrandom ",end="")
            self.buy(id=buy_id, rate=0.01)  # buy the 1% assest
        else:
            pass
            print("no trade")

    def actrandom_sell(self):
        print("%s " % self.name, end="")
        if np.random.rand() < 0.2:
            hold_list = self.get_stock_hold_list()  # choose the sell stock
            sell_id = random.choice(hold_list)
            print("actrandom ", end="")
            self.sell(id=sell_id, rate=0.1)  # choose the sell stock  sell the whole 10% assest
        else:
            pass
            # print("no trade")

    # intelligence action buy
    def actintellbuy(self):
        print("%s " % self.name, end="")
        buy_rate = []
        for id in stock_list:
            currentlist = listline_array[id]
            state = np.reshape(currentlist, [1, 10])
            print("__________currentlist____________")
            print("stock%d" % id)
            print(currentlist)
            print("__________currentlist____________")
            buy_rate.append(self.model.predict(state))  # append all stock buy rate
        buy_rate = np.reshape(buy_rate, [1, 3])
        buy_rate = buy_rate.flatten()
        buy_id = np.argmax(buy_rate)
        print("--------buyrate--------")
        print(buy_rate)
        print("--------buyrate--------")
        print("actintell ", end="")
        self.buy(id=buy_id, rate=buy_rate[buy_id])  # buy order buy rate

    # intelligence action sell
    def actintellsell(self):
        print("%s " % self.name, end="")
        sell_rate = []
        hold_list = self.get_stock_hold_list()  # get now what stock hold
        for id in hold_list:
            currentlist = listline_array[id]
            state = np.reshape([self.buylist_array[id], currentlist], [1, 20])
            sell_rate.append(self.model2.predict(state))  # append all stock sell rate
        sell_rate = np.reshape(sell_rate, [1, -1])
        sell_rate = sell_rate.flatten()
        sell_id = np.argmax(sell_rate)
        print("actintell ", end="")
        self.sell(id=sell_id, rate=sell_rate[sell_id])  # sell order sell_rate

    def update_train_buy_list(self, id, trading_money, old_assest):
        global step  # real time step
        d = len(self.buylist_array[id]) - 1
        buyprice = self.buylist_array[id][d]  # buyprice  get the last buylist_array
        x1 = listline_array_short[id]  # short： per step
        x2 = listline_array_long[id]  # long : 50  step
        x3 = self.buylist_array[id]
        x4 = all_stock_info.loc[id, "cur_price"]
        x5 = buyprice
        x6 = step
        x7 = trading_money  # before 
        x8 = old_assest  # asset before 
        self.train_buy_list_v2.append((x1, x2, x3, x4, x5, x6, x7, x8))

    def update_train_sell_list(self, id, trading_money, old_assest):
        global step
        d = len(self.selllist_array[id]) - 1  # real time step
        sellprice = self.selllist_array[id][d]  # sellprice  get the last selllist_array
        x1 = listline_array_short[id]  # short： per step
        x2 = listline_array_long[id]  # long : 50  step
        x3 = self.selllist_array[id]
        x4 = all_stock_info.loc[id, "cur_price"]
        x5 = sellprice
        x6 = step
        x7 = trading_money 
        x8 = old_assest  
        self.train_sell_list_v2.append((x1, x2, x3, x4, x5, x6, x7, x8))

    #def trainbuy(self,batch_size):

    

class Stock:
    def __init__(self, id, cur_price, init_num, total_value):
        global all_stock_info  # setting globe df list
        rest_num = init_num
        #self.title = title
        self.price = cur_price
        self.init_num = init_num
        self.total_value = total_value  
        self.rest_num = rest_num  # rest_num
        init_price = cur_price
        self.init_price = cur_price
        self.stock_info_new = [[cur_price, init_num, total_value, rest_num, init_price]]
        self.stock_info_new = pd.DataFrame(self.stock_info_new,
                                           columns=["cur_price", "init_num", "total_value", "rest_num", "init_price"], index=[id])
        print("stock%d init_num: %d init_price :%d total_value %d " % (id, init_num, init_price, total_value))
        all_stock_info = all_stock_info.append(self.stock_info_new)  # init stock info
        self.estimated = 0
'''
        def get_valuation(self):
            filename = self.title + 'priceforval.csv'
            fiter = csv.reader(open(filename))
            count = 0
            total = 0
            for i in fiter:
                count += 1
                total += float(i[0])
                print (total/count)

        def price_difference(self):
            return (-(self.price-self.real_price[t]) * Coe_real * random.rand())

        def price_estimate(self):
            self.valuation = self.get_valuation()
            com_value = -(self.price - self.valuation[t]) * Coe_val * random.rand()
            return com_value
            
        def priceflu(self):
            r1 = np.random.rand()
            r2 = np.random.rand()
            if self.price < self.estimated:
                if r1 < 0.4:
                    fluindex = Coe1 * r2 * self.price
                else:
                    fluindex = -Coe2 * r2 * self.price
            elif self.price >= estimated:
                if r1 <0.4:
                    fluindex = -Coe1 * r2 * self.price
                else:
                    fluindex = Coe2 * r2 * self.price
            return fluindex

        def total_com(self):
            return (get_valuation() +price_difference() + priceflu())

        def excute_com(self):
            if self.title == "":
                pass
            else:
                before_com_price = cur_price
'''



class Bank:  # 银行
    def __init__(self, bank_id, interest_rate, level_rate, force_sell_rate):
        global all_bank_info
        self.bank_id = bank_id
        self.interest_rate = interest_rate
        self.level_rate = level_rate  #
        self.force_sell_rate = force_sell_rate
        new_bank_df = [[self.interest_rate, self.level_rate, self.force_sell_rate]]
        new_bank_df = pd.DataFrame(new_bank_df, columns=["interest_rate", "lever_rate", "force_sell_rate"],
                                   index=[self.bank_id])
        all_bank_info = all_bank_info.append(new_bank_df)
        print("bank%d interest_rate：%s,lever_rate:%s,force_sell_rate:%s" % (
        self.bank_id, self.interest_rate, self.level_rate, self.force_sell_rate))


# update listline
def listline_short_update():
    # update stock
    for id in stock_list:
        listline_array_short[id].append(all_stock_info.loc[id, "cur_price"])


def listline_long_update():
    # Get the short stock price from df table and update each step
    for id in stock_list:
        listline_array_long[id].append(all_stock_info.loc[id, "cur_price"])


def listline_update():
    listline_short_update()  # short update per step
    if step % 50 == 0:
        listline_long_update()  # long update 50 step


if __name__ == "__main__":

    stock1 = Stock(id=stock_list[0], cur_price=10, init_num=1000000,total_value=10000000)  # init stock1： cur_price price 10 ;init_num cost 1000 ;total_value sum_value 10000
    stock2 = Stock(id=stock_list[1], cur_price=17.2, init_num=1000000,
                   total_value=17200000,)
    stock3 = Stock(id=stock_list[2], cur_price=10, init_num=1000000,
                   total_value=10000000,)
    agent1 = Agent(initasset=1000000, name="agent1")  # init agent1 asset
    agent2 = Agent(initasset=100000,  name="agent2")  #  init agent2 asset
    agent3 = Agent(initasset=100000,  name="agent3")  #  init agent3 asset

    bank1 = Bank(bank_id=0, interest_rate=0.01, level_rate=5,
                 force_sell_rate=0.92)  # interest_rate 1% level_rate  5multiple force_sell_rate 92%
    bank2 = Bank(bank_id=1, interest_rate=0.02, level_rate=6,
                 force_sell_rate=0.90)  # interest_rate 1% level_rate  5multiple force_sell_rate 90%
    bank3 = Bank(bank_id=2, interest_rate=0.02, level_rate=6,
                 force_sell_rate=0.91)  # interest_rate 1% level_rate  5multiple force_sell_rate 91%
    batch_size = 10
    m = 0
    # print(stock1.price)
    stepindex = 0

    # change agent trading sequence /  step1 agent0->agent1->agent2; step 2 agent1->agent2->agent0 ;step3 agent2->agent0->agent1
    # Instantiate the agent as an intermediate variable
    agent = Agent(1000, name="agent")
    agent_list = [deque(maxlen=3)]
    agent_list[0].append(agent1)
    agent_list[0].append(agent2)
    agent_list[0].append(agent3)  # agent_list[0] = [agent1,agent2,agent3]
    #############################
    ##########################   normal trading   #####################################
    # random trading
    for i in range(3000):
        for i in range(3):  # 3 agent
            agent = agent_list[0][i]
            if step % 1 == 0:
                if np.random.rand() < 0.3:
                    if agent.asset > 500:  # when buy agent'assest must > 0
                        agent.actrandom_buy()  # random buy
                else:
                    hold_list = agent.get_stock_hold_list()
                    if hold_list != []:
                        agent.actrandom_sell()  # random sell
                    else:
                        pass
                        # print("%s now hold is empty!!!"%agent.name )
            pass
            # print("%s asset:%f" % (agent.name, agent.asset))
        listline_update()  # updata the listline,include short update and long update
        step += 1
        agent_list[0].append(agent_list[0][0])  # agent To cause the order of transactions to change in turn
        #all_stock_info.to_csv("result.csv")
    for i in range(20):
        for i in range(3):  # 3 agent
            agent = agent_list[0][i]
            if step % 1 == 0:
                hold_list = agent.get_stock_hold_list()
                if hold_list != []:
                    agent.actrandom_sell()  # random sell
                else:
                    pass
                    # print("%s now hold is empty!!!"%agent.name )
            pass
            # print("%s asset:%f" % (agent.name, agent.asset))
        listline_update()  # updata the listline,include short update and long update
        step += 1
        agent_list[0].append(agent_list[0][0])  # agent To cause the order of transactions to change in turn
    print("________________________long listline : 50 setps perprice________________________________")
    print(listline_array_long)
    print("________________________short listline : per setps perprice______________________________")
    print(listline_array_short)
    print("_______________________self.train_buy_list_v2____________________________________________")
    # print(agent1.train_buy_list_v2)
    # print(agent2.train_buy_list_v2)
    # print(agent3.train_buy_list_v2)
    print("_______________________self.train_sell_list_v2____________________________________________")
    # print(agent1.train_sell_list_v2)
    # print(agent2.train_sell_list_v2)
    # print(agent3.train_sell_list_v2)

    # actintell trading
    # for i in range(1000):
    #     for i in  range(3): #三个agent
    #         agent = agent_list[0][i]
    #         if np.random.rand() < 0.5:
    #             if agent.asset > 0:  # when buy agent'assest must > 0
    #                 agent.actintellbuy()                   # actintell buy
    #             hold_list = agent.get_stock_hold_list()
    #             if hold_list != []   :   # full of the  linelist(maxlen=10) ,abodon error:
    #                 agent.actintellsell()              # actintell sell
    #             else:
    #                 print("%s now hold is empty!!!"%agent.name)
    #             print("%s asset:%f" % (agent.name, agent.asset))
    #     listline_update()  # updata the listline
    #     print(all_stock_info)
    #     print("__________listline_array_________________")
    #     print(listline_array)
    #     print("__________listline_array_________________")
    #     step += 1
    #     agent_list[0].append(agent_list[0][0])  
    #
    #         # random_trade slow to actintell_trade
    #         # if agent.epsilon > 0.05:
    #         #     agent.epsilon = agent.epsilon * agent.epsilon_de
    #         # print("%s epsilon:%f" %(agent.name,agent.epsilon))
    #         ##########################   lever trading   #####################################
    #         # if step%20 == 0:
    #         #     if agent.asset > 10:    # when buy agent'assest must > 0
    #         #         own_principal = 0.3 * agent.asset  
    #         #         agent.actinel_leverage_buy(own_principal=own_principal)
    #         # if step > 10 :   # full of the  linelist(maxlen=10) ,abodon error
    #         #     agent.actinel_leverage_sell()    #leverage_sell tour
    #
    #     # listline_update()    # updata the listline
    #     # step += 1
    #     # print("%s asset:%f" %(agent.name,agent.asset))
    #     # agent_list[0].append(agent_list[0][0])  
    ###################################################agetn info ###########################################
    print("--" * 5)
    print("agent1 current_asset", end="")
    print(agent1.asset)
    print("agent1 current_asset")
    print(agent1.agent_info_df)

    print("agent1 current_leverage_contract")
    print(agent1.leveraged_contract_df)
    ##
    print("--" * 5)
    print("agent2 current_asset", end="")
    print(agent2.asset)
    print("agent2 current_asset")
    print(agent2.agent_info_df)
    print("agent2 current_leverage_contract")
    print(agent2.leveraged_contract_df)
    print("--" * 5)
    ##
    print("--" * 5)
    print("agent3 current_asset", end="")
    print(agent3.asset)
    print("agent3 current_asset")
    print(agent3.agent_info_df)
    print("agent3 current_leverage_contract")
    print(agent3.leveraged_contract_df)
    print("--" * 5)

    print('--Liquidation of all sold assets--')
    print('-----------*')
    for i in range(3):
        print(agent1.agent_info_df.loc[i, "profit"] + agent1.agent_info_df.loc[i, "hold_num"] * (
                    all_stock_info.loc[i, "cur_price"] + all_stock_info.loc[i, "init_price"]) / 2)
    print('-----------*')
    asset2_rest = 0
    for i in range(3):
        print(agent2.agent_info_df.loc[i, "profit"] + agent2.agent_info_df.loc[i, "hold_num"] * (
                    all_stock_info.loc[i, "cur_price"] + all_stock_info.loc[i, "init_price"]) / 2)
        asset2_rest += agent2.agent_info_df.loc[i, "hold_num"] * (
                    all_stock_info.loc[i, "cur_price"] + all_stock_info.loc[i, "init_price"]) / 2
    asset2_rest += agent2.asset
    print(asset2_rest)
    print('-----------*')
    asset3_rest = 0
    for i in range(3):
        print(agent3.agent_info_df.loc[i, "profit"] + agent3.agent_info_df.loc[i, "hold_num"] * (
                    all_stock_info.loc[i, "cur_price"] + all_stock_info.loc[i, "init_price"]) / 2)
        asset3_rest += agent3.agent_info_df.loc[i, "hold_num"] * (
                    all_stock_info.loc[i, "cur_price"] + all_stock_info.loc[i, "init_price"]) / 2
    asset3_rest += agent3.asset
    print(asset3_rest)
    ########################################################################################################
    print(all_stock_info)

    #     print('############')
    #     print(stock_price)
    #     print('############')
    #     if i % 1 == 0:
    #         print('------------')
    #         print(agent1.asset)
    #         # print(agent1.buylist)
    #         print('------------')
    #     # print("eps",len(agent1.trainlist))
    #     if len(agent1.trainlist) >= batch_size:
    #         agent1.trainbuy(batch_size)
    #         agent1.trainsell(batch_size)
    #
    #         # agent1.trainsell(10)
    #     # time.sleep(0.002)
    #     print(i)
    #     # print("eps",agent1.epsilon)
    # agent1.sell(stock1.price)
    # print(agent1.asset)
    #
    # agent1.model.save_weights("w1-1.h5")
    # agent1.model2.save_weights("w2-2.h5")
    # agent1.model.save("a1.h5")
    # agent1.model2.save("a2.h5")

# plt.scatter(x,y)
# # plt.plot(x,y)
# plt.show()
#