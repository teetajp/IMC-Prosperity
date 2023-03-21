from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order, Symbol, Trade


class Trader:
    symbols = ["PEARLS", "BANANAS"]
    initial_fair_price = {"PEARLS": 10000, "BANANAS": 4875}
    position_limits = {"PEARLS": 20, "BANANAS": 20}
    window_size = 10  # Set the number of prices to consider for the weighted moving average

    def __init__(self):
        self.trade_history = {"PEARLS": [], "BANANAS": []}

    def update_trade_history(self, own_trades: Dict[Symbol, List[Trade]], market_trades: Dict[Symbol, List[Trade]]) \
            -> None:
        for symbol in Trader.symbols:
            recent_trades = []
            if symbol in own_trades:
                recent_trades.extend(own_trades[symbol])
            if symbol in market_trades:
                recent_trades.extend(market_trades[symbol])

            recent_trades.sort(key=lambda trade: trade.timestamp)

            for trade in recent_trades:
                self.trade_history[symbol].append(trade.price)

            while len(self.trade_history[symbol]) > Trader.window_size:
                self.trade_history[symbol].pop(0)

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}

        # Update trade history for moving average calculations
        self.update_trade_history(state.own_trades, state.market_trades)

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            # Retrieve the Order Depth containing all the market BUY and SELL orders for the product
            order_depth: OrderDepth = state.order_depths[product]

            # Initialize the list of Orders to be sent as an empty list
            orders: list[Order] = []

            # Calculate the weighted moving average of recent prices
            if len(self.trade_history[product]) == Trader.window_size:
                weights = list(range(1, Trader.window_size + 1))
                fair_price = sum([price * weight for price, weight in
                                  zip(self.trade_history[product][:Trader.window_size], weights)]) / sum(weights)
            else:
                # If moving average history is less than window size, set the fair price to a default value
                fair_price = Trader.initial_fair_price[product]

            # Quantity Limit (may need to change if making more than one order in a round)
            if product in state.position:
                order_qty = Trader.position_limits[product] - abs(state.position[product])
            else:
                order_qty = Trader.position_limits[product]

            # If statement checks if there are any SELL orders in the market
            if len(order_depth.sell_orders) > 0:

                # Sort all the available sell orders by their price,
                # and select only the sell order with the lowest price
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]

                # Check if the lowest ask (sell order) is lower than the fair value
                if best_ask < fair_price:
                    if product in state.position and state.position[product] >= Trader.position_limits[product]:
                        continue

                    # In case the lowest ask is lower than our fair value,
                    # This presents an opportunity for us to buy cheaply
                    print("BUY", str(order_qty) + "x", best_ask)
                    orders.append(Order(product, best_ask, order_qty))

            # If the price of the order is higher than the fair value
            # This is an opportunity to sell at a premium
            if len(order_depth.buy_orders) > 0:
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]

                if best_bid > fair_price:
                    if product in state.position and state.position[product] <= -Trader.position_limits[product]:
                        continue

                    print("SELL", str(-order_qty) + "x", best_bid)
                    orders.append(Order(product, best_bid, -order_qty))

            # Add all the above the orders to the result dict
            result[product] = orders

            # Return the dict of orders, possibly containing BUY or SELL orders
        return result
