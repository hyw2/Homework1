import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import pandas as pd
from os import listdir, remove
import pickle
from time import sleep

from helper_functions import *  # this statement imports all functions from your helper_functions file!

# Run your helper function to clear out any io files left over from old runs
# 1:
fig = go.Figure(
)

check_for_and_del_io_files()

# Make a Dash app!
app = dash.Dash(__name__)

# Define the layout.
app.layout = html.Div([

    # Section title
    html.H1("Section 1: Fetch & Display exchange rate historical data"),

    # Currency pair text input, within its own div.
    html.Div(
        [
            "Input Currency: ",
            # Your text input object goes here:
            html.Div(dcc.Input(id='currency-pair', value='AUDCAD', type='text'))
        ],
        # Style it so that the submit button appears beside the input.
        style={'display': 'inline-block'}
    ),
    # Submit button:
    html.Button('Submit', id='submit-button', n_clicks=0),
    # Line break
    html.Br(),
    # Div to hold the initial instructions and the updated info once submit is pressed
    html.Div(id='currency-pair-output', children='Enter a currency code and press "submit"'),
    html.Div([
        # Candlestick graph goes here:
        dcc.Graph(id='candlestick-graph', figure=fig)
    ]),
    # Another line break
    html.Br(),
    # Section title
    html.H1("Section 2: Make a Trade"),
    # Div to confirm what trade was made
    html.Div(id='output-trade-div'),
    # Radio items to select buy or sell
    html.Div(
        dcc.RadioItems(id='buy-sell', options=[{'label': 'Buy', 'value': 'buy'},
                                               {'label': 'Sell', 'value': 'sell'}], value='buy')),
    # Text input for the currency pair to be traded
    html.Div(["Input currency pair to trade:",
              dcc.Input(id='currency-pair-trade', type='text')]),
    # Numeric input for the trade amount
    html.Div(["Input amount to trade:",
              dcc.Input(id='currency-pair-amount', type='number')]),
    # Submit button for the trade
    html.Button('Submit Trade', id='submit-trade-button', n_clicks=0)
])


# Callback for what to do when submit-button is pressed
@app.callback(
    [Output('currency-pair-output', 'children'),
     Output('candlestick-graph', 'figure')],
    [Input('submit-button', 'n_clicks')],
    State('currency-pair', 'value')
)
def update_candlestick_graph(n_clicks, value):  # n_clicks doesn't get used, we only include it for the dependency.
    # Now we're going to save the value of currency-input as a text file.
    with open("currency_pair.txt", 'w') as f:
        f.write(value)
    # Wait until ibkr_app runs the query and saves the historical prices csv
    while 'currency_pair_history.csv' not in listdir():
        sleep(0.1)
    # Read in the historical prices
    df = pd.read_csv('currency_pair_history.csv')
    # Remove the file 'currency_pair_history.csv'
    check_for_and_del_io_files()
    # Make the candlestick figure
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df['date'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close']
            )
        ]
    )
    # Give the candlestick figure a title
    fig.update_layout(title=str(value)+" Candlestick Plot")
    # Return your updated text to currency-output, and the figure to candlestick-graph outputs
    return ('Submitted query for ' + value), fig


# Callback for what to do when trade-button is pressed
@app.callback(
    Output('output-trade-div', 'children'),
    Input('submit-trade-button', 'n_clicks'),
    [State('buy-sell', 'value'), State('currency-pair-trade', 'value'), State('currency-pair-amount', 'value')],  # name of pair, trade amount,
    prevent_initial_call=True
)
def trade(n_clicks, action, trade_currency, trade_amt):  # Still don't use n_clicks, but we need the dependency

    # Make the message that we want to send back to trade-output
    msg = str(action) + " " + str(trade_amt) + " of forex: " + str(trade_currency)
    # Make our trade_order object -- a DICTIONARY.
    trade_order = {'action': action, 'trade_amt': trade_amt, 'trade_currency': trade_currency}
    # Dump trade_order as a pickle object to a file connection opened with write-in-binary ("wb") permission:
    pickle.dump(trade_order, open("trade_order.p", "wb"))
    # Return the message, which goes to the trade-output div's "children" attribute.
    return msg


# Run it!
if __name__ == '__main__':
    app.run_server(debug=True)
