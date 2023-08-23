from initial_state import *

def p_optimal_orders(system_params, substep, state_history, previous_state):

    # Extracting relevant system parameters
    book_data = system_params['book data']
    trades_data = system_params['trades data']

    gamma = system_params['gamma']
    sigma = system_params['sigma']
    T = system_params['T']
    dt = system_params['dt']
    k = system_params['k']

    # Extracting relevant previous state parameters
    timestamp = previous_state['timestamp']
    q = previous_state['q']

    mid_price = (book_data.loc[timestamp, f'bids[{0}].price'] + book_data.loc[timestamp, f'asks[{0}].price']) / 2

    # Calculating reservation price and target spread
    reservation_price = mid_price - q * gamma * sigma ** 2 * (T - timestamp * dt / T)
    target_spread = gamma * sigma ** 2 * (T - timestamp * dt / T) + (2 / gamma) * np.log(1 + gamma / k)

    # Calculating optimal bid and ask prices
    optimal_bid = reservation_price - target_spread / 2
    optimal_ask = reservation_price + target_spread / 2

    return {'mid-price': mid_price, 'reservation price': reservation_price, 'optimal_bid': optimal_bid,
            'optimal_ask': optimal_ask, 'target_spread': target_spread}


def p_execute_orders(system_params, substep, state_history, previous_state):


    # Extract system parameters from the previous state.
    timestamp = previous_state['timestamp']
    q = previous_state['q']
    trades_param = previous_state['trades_iterator']
    PnL = previous_state['PnL']

    active_orders = previous_state['active_orders']
    all_orders = previous_state['all_orders']

    optimal_bid = previous_state['optimal_bid']
    optimal_ask = previous_state['optimal_ask']
    mid_price = previous_state['mid-price']
    size = system_params['size']
    hold_time = system_params['hold_time']
    target_spread = previous_state['target_spread']

    book_data = system_params['book data'].loc[timestamp]
    trades_data = system_params['trades data']
    book_upd_time = book_data['local_timestamp']
    next_book_upd_time = system_params['book data'].loc[timestamp + 1]['local_timestamp']

    # Volume imbalance implementation
    v_a = book_data[f'asks[{0}].amount']
    v_b = book_data[f'bids[{0}].amount']

    p = (v_b - v_a) / (v_b + v_a)

    # Get the previous placed order time.
    if len(active_orders) == 0:
        previous_placed_order_time = 0
    else:
        previous_placed_order_time = active_orders[-1]['place_time']

    # Add new orders if conditions are met.
    if book_upd_time - previous_placed_order_time > system_params['delay']:

        if p > 0:
            p = min(0.15 + p, 1)
        else:
            p = max(0.8 - p, 0)

        order_size = size * p

        active_orders.append(
            {'id': timestamp, 'side': 'BID', 'place_time': book_upd_time, 'close_time': '-', 'type': '-', 'size': size,
             'price_open': optimal_bid})
        q += order_size

        if p < 0:
            p = min(0.15 + abs(p), 1)
        else:
            p = max(0.8 - abs(p), 0)

        active_orders.append(
            {'id': timestamp, 'side': 'ASK', 'place_time': book_upd_time, 'close_time': '-', 'type': '-', 'size': size,
             'price_open': optimal_ask})

        q -= order_size

    # Remove orders held beyond the specified hold time.
    if active_orders:
        new_active_orders = [order for order in active_orders if book_upd_time - order['place_time'] <= hold_time]

        # Update all_orders with removed active orders.
        for order in active_orders:
            if order not in new_active_orders:
                order.update({'close_time': order['place_time'] + hold_time, 'type': 'Manually'})
                all_orders.append(order)

        active_orders = new_active_orders

    # Handle trades and remove orders that have been executed.
    takers_orders = []

    while trades_data.loc[trades_param]['local_ts'] < book_upd_time and trades_param < len(trades_data) - 2:
        takers_orders.append(trades_data.loc[trades_param])
        trades_param = trades_param + 1 if trades_param < len(trades_data) - 2 else trades_param

    new_active_orders = []
    for maker_order in active_orders:
        order_matched = False
        for taker_order in takers_orders:
            # Market depth calculation.
            m = 0

            if taker_order['side'] == 'S' and maker_order['side'] == 'BID' and order_matched == False:
                while book_data[f'bids[{m}].price'] > maker_order['price_open'] and m < 24:
                    m += 1

                maker_order['market_depth'] = book_data[f'bids[{m}].amount']

                # Check taker order and update accordingly.
                if taker_order['amount'] > maker_order['market_depth']:
                    maker_order.update({'close_time': taker_order['local_ts'], 'type': 'Market'})
                    all_orders.append(maker_order)
                    q += maker_order['size']
                    order_matched = True

                    PnL -= maker_order['size'] * maker_order['price_open']

            elif taker_order['side'] == 'B' and maker_order['side'] == 'ASK' and order_matched == False:
                while book_data[f'asks[{m}].price'] < maker_order['price_open'] and m < 24:
                    m += 1

                maker_order['market_depth'] = book_data[f'asks[{m}].amount']

                # Check taker order and update accordingly.
                if taker_order['amount'] > maker_order['market_depth']:
                    maker_order.update({'close_time': taker_order['local_ts'], 'type': 'Market'})
                    all_orders.append(maker_order)
                    q -= maker_order['size']
                    order_matched = True

                    PnL += maker_order['size'] * maker_order['price_open']

        if not order_matched:
            new_active_orders.append(maker_order)

    active_orders = new_active_orders

    if timestamp == len(df_book) - 2:
        PnL += q * mid_price
        q = 0

    return {'active_orders': active_orders, 'all_orders': all_orders, 'q': q, 'trades_iterator': trades_param,
            'PnL': PnL}