from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order


class Trader:

    initial_fair_price = {"PEARLS": 10000, "BANANAS": 4875}
    position_limits = {"PEARLS": 20, "BANANAS": 20}
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            # Retrieve the Order Depth containing all the market BUY and SELL orders for the product
            order_depth: OrderDepth = state.order_depths[product]

            # Initialize the list of Orders to be sent as an empty list
            orders: list[Order] = []

            # Set the number of prices to consider for the weighted moving average
            n = 10

            # Calculate the weighted moving average of recent prices
            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                recent_prices = list(order_depth.sell_orders.keys()) + list(order_depth.buy_orders.keys())
                recent_prices.sort(reverse=True)
                weights = list(range(1, n + 1))
                fair_price = sum([price * weight for price, weight in zip(recent_prices[:n], weights)]) / sum(weights)
            elif len(order_depth.sell_orders) > 0:
                fair_price = min(order_depth.sell_orders.keys())
            elif len(order_depth.buy_orders) > 0:
                fair_price = max(order_depth.buy_orders.keys())
            else:
                # If there are no buy or sell orders, set the fair price to a default value
                fair_price = Trader.initial_fair_price[product]

            # If statement checks if there are any SELL orders in the market
            if len(order_depth.sell_orders) > 0:

                # Sort all the available sell orders by their price,
                # and select only the sell order with the lowest price
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]

                # Check if the lowest ask (sell order) is lower than the fair value
                if best_ask < fair_price:

                    if state.position[product] >= Trader.position_limits[product]:
                        continue
                    order_qty = Trader.position_limits[product] - state.position[product]

                    # In case the lowest ask is lower than our fair value,
                    # This presents an opportunity for us to buy cheaply
                    print("BUY", str(order_qty) + "x", best_ask)
                    orders.append(Order(product, best_ask, order_qty))

            # If the price of the order is higher than the fair value
            # This is an opportunity to sell at a premium
            if len(order_depth.buy_orders) != 0:
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]

                if best_bid > fair_price:

                    if state.position[product] <= -Trader.position_limits[product]:
                        continue
                    order_qty = state.position[product] - Trader.position_limits[product]

                    print("SELL", str(order_qty) + "x", best_bid)
                    orders.append(Order(product, best_bid, order_qty))

            # Add all the above the orders to the result dict
            result[product] = orders

            # Return the dict of orders, possibly containing BUY or SELL orders
        return result
