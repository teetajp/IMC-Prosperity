from algo.datamodel import *
import pandas as pd


def simulate(round: int, day: int, trader):
    prices_path = f"markets/round_{round}/prices_round_{round}_day_{day}.csv"
    trades_path = f"markets/round_{round}/trades_round_{round}_day_{day}_nn.csv"
    df_prices = pd.read_csv(prices_path, sep=';')
    df_trades = pd.read_csv(trades_path, sep=';')
    prev_time = -1
    state = TradingState(-1, {}, {}, {}, {}, {}, {})
    position = {}
    my_trades = {}
    market_trades = {}
    observations = {}
    for _, row in df_prices.iterrows():
        time = row["timestamp"]
        product = row["product"]
        if product not in position:
            position[product] = 0
            my_trades[product] = []
            market_trades[product] = []
        listing = {product: {"symbol": product, "product": product, "denomination": product}}
        depth = {product: OrderDepth()}
        depth[product].buy_orders = {row[f"bid_price_{i}"]: row[f"bid_volume_{i}"] for i in range(1, 4)}
        depth[product].sell_orders = {row[f"ask_price_{i}"]: row[f"ask_volume_{i}"] for i in range(1, 4)}

        # process trades that happened at this time
        trades = df_trades[df_trades['timestamp'] == time]
        for _, trade in trades.iterrows():
            symbol = trade['symbol']
            if symbol != product: continue
            t = Trade(symbol, trade['price'], trade['quantity'], trade['buyer'], trade['seller'], time)
            market_trades[product].append(t)

    if time != prev_time and prev_time != -1:
        state.timestamp = time
        output = trader.run(state)
        for product in output:
            for order in output[product]:  # process trader orders
                levels = state.order_depths[order.symbol]
                if order.quantity < 0:  # sell/ask
                    volume = abs(order.quantity)
                    while len(levels.buy_orders):
                        best_bid = max(levels.buy_orders.keys())
                        if best_bid < order.price: break  # if no overlap, skip
                        volume, levels.buy_orders[best_bid] = volume - levels.buy_orders[best_bid], \
                                                              levels.buy_orders[best_bid] - volume
                        if volume <= 0: break
                        if levels.buy_orders[best_bid] <= 0: del levels.buy_orders[best_bid]
                else:  # buy / bid
                    volume = abs(order.quantity)
                    while len(levels.sell_orders):
                        best_ask = max(levels.sell_orders.keys())
                        if best_ask < order.price: break  # if no overlap, skip
                        volume, levels.sell_orders[best_ask] = volume - levels.sell_orders[best_ask], \
                                                               levels.sell_orders[best_ask] - volume
                        if volume <= 0: break
                        if levels.sell_orders[best_ask] <= 0: del levels.sell_orders[best_ask]
        state = TradingState(time, listing, depth, my_trades, market_trades, position, observations)
    else:
        state.listings[product] = listing[product]
        state.order_depths[product] = depth[product]
    prev_time = time