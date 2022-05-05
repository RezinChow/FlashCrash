initial_p = 10;

initial_n = 10000;

previous_p= initial_p;
previous = initial_n;


agent_buy = 1000;


current_v = initial_p * initial_n + agent_buy;


current_p = current_v / initial_n;

agent_hold_n = floor(agent_buy/((current_p + initial_p)/2));


agent_sell_n = agent_hold_n;

down_rate = (current_p - previous_p)/ agent_hold_n;

price_after = current_p - down_rate * agent_sell_n;

agent_get = agent_sell_n * (price_after + current_p)/2;


