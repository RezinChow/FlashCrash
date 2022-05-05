I verify that I am the sole author of the programmes contained in this archive, except where explicitly stated to the contrary
Hefeng Zhou
------------------------------------------------
mainforall.py

This is the integrated file

running version:
python 3.6
tensorflow 1.15
impot libs: numpy  pandas math collections  keras.models keras.layers keras.optimizers random
------------training---------------------------
traing inputsample is from random trading create, using fcn 
actrandom_buy()--- buy()
actrandom_sell()----sell()
Circular 1000 times,then get the buy_model1 and sell_model2
the sample input construct:
  	x1: listline_array_short  size[30]
	x2: listline_array_long  size[30]
	x3: self.buylist_array    size[10]
	x4: cur_price               size[1]
	x5: buyprice                size[1]
	x6: step 		  size[1]
	x7: trading_money	  size[1]
	x8:old_assest               size[1]        
	
output: is the stock buy or sell rate,express by rate in  [0,1]
------------trading fcn-----------------------
random trading can full in the self buylist、selllist、listline(stock price listline),in order to create the samle for training
random trading fcn:
	actrandom_buy()--- buy()
	actrandom_sell()----sell()
Use established actintell trading models to predict stock purchases and sales
actintell trading fcn:
	actintellbuy()---buy()
	actintellsell()---sell()
Leverage trading, mainly rely on the intelligence model of the buy and sell forecast, to achieve trading,and contain the bank include money interest、lever_rate、force_sell_rate
lever trading fcn:
	actinel_leverage_buy()---leverage_buy()
	actinel_leverage_sell()---leverage_sell()

we should update the stock price frequence,include long update(50 steps) and short update(every step)
update listline:
	listline_short_update()---update the cur_price every step
	listline_long_update()---update the cur_price every 50 steps

----------------------------------------------
In Django
There a little files of source code and the templet is more than 800mb, I would upload it in my GitHub later.

