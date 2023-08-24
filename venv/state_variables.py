from initial_state import *
from policy_functions import *


'''
State variables
for the first PSUB
'''


def s_midprice(system_params, substep, state_history, previous_state, policy_input):
    updated_midprice = policy_input['mid-price']

    return "mid-price", updated_midprice


def s_reservation_price(system_params, substep, state_history, previous_state, policy_input):
    updated_reservation_price = policy_input['reservation price']

    return "reservation price", updated_reservation_price


def s_target_spread(system_params, substep, state_history, previous_state, policy_input):
    updated_target_spread = policy_input['target_spread']

    return "target_spread", updated_target_spread


def s_optimal_bid(system_params, substep, state_history, previous_state, policy_input):
    updated_bid = policy_input['optimal_bid']

    return "optimal_bid", updated_bid


def s_optimal_ask(system_params, substep, state_history, previous_state, policy_input):
    updated_ask = policy_input['optimal_ask']

    return "optimal_ask", updated_ask


def s_target(system_params, substep, state_history, previous_state, policy_input):
    updated_spread = policy_input['target_spread']

    return "target_spread", updated_spread


'''
State variables 
for the second PSUB
'''


def s_active_orders(system_params, substep, state_history, previous_state, policy_input):
    active_orders = policy_input['active_orders']

    return "active_orders", active_orders


def s_all_orders(system_params, substep, state_history, previous_state, policy_input):
    all_orders = policy_input['all_orders']

    return "all_orders", all_orders


def s_q(system_params, substep, state_history, previous_state, policy_input):
    q = policy_input['q']

    return "q", q


def s_trades_iterator(system_params, substep, state_history, previous_state, policy_input):
    trades_iterator = policy_input['trades_iterator']

    return "trades_iterator", trades_iterator


def s_PnL(system_params, substep, state_history, previous_state, policy_input):
    PnL = policy_input['PnL']

    return "PnL", PnL


'''
State variables 
for the third PSUB
'''


def s_timestamp(system_params, substep, state_history, previous_state, policy_input):
    updated_timestamp = previous_state['timestamp'] + 1


    return "timestamp", updated_timestamp


partial_state_update_blocks = [
    {
        'policies': {
            'optimal orders': p_optimal_orders
        },  # 1 calculating parameters
        'variables': {
            'mid-price': s_midprice,
            'reservation price': s_reservation_price,
            'optimal_bid': s_optimal_bid,
            'optimal_ask': s_optimal_ask,
            'target_spread': s_target
        }
    },
    {
        'policies': {
            'execute orders': p_execute_orders
        },  # 2 placing orders
        'variables': {
            'active_orders': s_active_orders,
            'all_orders': s_all_orders,
            'q': s_q,
            'PnL': s_PnL,
            'trades_iterator': s_trades_iterator
        }
    },
    {
        'policies': {
        },
        'variables': {
            'timestamp': s_timestamp
        }
    }

]

sim_config = config_sim({
    "N": 1,  # the number of times we'll run the simulation ("Monte Carlo runs")
    "T": range(len(df_book) - 1),  # the number of timestamps the simulation will run for
    "M": system_params  # the parameters of the system
})

del configs[:]  # Clear any prior configs

experiment = Experiment()
experiment.append_configs(
    initial_state=initial_state,
    partial_state_update_blocks=partial_state_update_blocks,
    sim_configs=sim_config
)
