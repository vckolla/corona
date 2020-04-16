import numpy                as np
import pandas               as pd
#import tensorflow           as tf

from datetime              import datetime
from keras.models          import Sequential
from keras.layers          import Dense, LSTM

from math                  import sqrt
from matplotlib            import pyplot
from numpy                 import array, mean, std

from sklearn.metrics       import mean_squared_error
import os
import warnings

os.environ['TF_CPP_MIN_LOG_LEVEL']='3'
with warnings.catch_warnings():
	warnings.filterwarnings("ignore", category=DeprecationWarning)

# split a univariate dataset into train/test sets
def train_test_split(data, n_test):
    train, test = data[:-n_test], data[-n_test:]
    return train, test

# transform list into supervised learning format
def series_to_supervised(data, n_in, n_out=1):
    df = pd.DataFrame(data)
    cols = list()
    
    # input sequence (t-n, ... t-1)
    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
        
    # forecast sequence (t, t+1, ... t+n)
    for i in range(0, n_out):
        cols.append(df.shift(-i))
        
    # put it all together
    agg = pd.concat(cols, axis=1)
    
    # drop rows with NaN values
    agg.dropna(inplace=True)
    
    return agg.values

# root mean squared error or rmse
def measure_rmse(actual, predicted):
    rmse = sqrt(mean_squared_error(actual, predicted))
    
    return rmse

# difference dataset
def difference(data, interval):
    diff_data = [data[i] - data[i - interval] for i in range(interval, len(data))]
    
    return diff_data

# fit a model
def model_fit(train, config):
    # unpack config
    n_input, n_nodes, n_epochs, n_batch, n_diff = config
    
    # prepare data (useful for seasonal differencing, which
    # is not applicable here)
    if n_diff > 0:
        train = difference(train, n_diff)
    
    data = series_to_supervised(train, n_input)
    train_x, train_y = data[:, :-1], data[:, -1]
    train_x = train_x.reshape((train_x.shape[0], train_x.shape[1], 1))
    
    # define model
    model = Sequential()
    model.add(LSTM(n_nodes, activation='relu', input_shape=(n_input, 1)))
    model.add(Dense(n_nodes, activation='relu'))
    model.add(Dense(1))
    model.compile(loss='mse', optimizer='adam')
    
    # fit
    model.fit(train_x, train_y, epochs=n_epochs, batch_size=n_batch, verbose=0)
    
    return model

# forecast with a pre-fit model
def model_predict(model, history, config):
    # unpack config
    n_input, _, _, _, n_diff = config
    
    # prepare data
    correction = 0.0
    if n_diff > 0:
        correction = history[-n_diff]
        history = difference(history, n_diff)
    
    x_input = array(history[-n_input:]).reshape((1, n_input, 1))
    
    # forecast
    yhat = model.predict(x_input, verbose=0)
    pred = correction + yhat[0]
    
    return pred

# walk-forward validation for univariate data
def walk_forward_validation(data, n_test, cfg):
    predictions = list()
    
    # split dataset
    train, test = train_test_split(data, n_test)
    
    # fit model
    model = model_fit(train, cfg)
    
    # seed history with training dataset
    history = [ x for x in train ]
    
    # step over each time-step in the test set
    for i in range(len(test)):
        # fit model and make forecast for history
        yhat = model_predict(model, history, cfg)
        
        # store forecast in list of predictions
        predictions.append(yhat)
        
        # add actual observation to history for the next loop
        history.append(test[i])
    
    # estimate prediction error
    error = measure_rmse(test, predictions)
    #print(f"RMSE = {error:.0f}")
    
    return error, test, predictions

# repeat evaluation of a config
def repeat_evaluate(data, n_test, config, n_repeats=10):
    scores = []

    # fit and evaluate the model n times
    for _ in range(n_repeats):
        score, test, pred = walk_forward_validation(data, n_test, config)
        scores.append(score)
        
    return scores

# summarize model performance
def summarize_scores(scores):
    # print a summary
    scores_m, score_std = mean(scores), std(scores)
    print(f"{scores_m:.2f} RMSE (+/- {score_std:.2f})")
    
    # box and whisker plot
    pyplot.boxplot(scores)
    pyplot.show()

def get_lstm_rslts(df_in, metric):
    """run_all - orchestrator
    """
    # number of periods in hold-out
    n_test = 7

    # n_inputs, n_nodes, n_epochs, n_batch, n_diff
    config = [ 1, 50, 200, 5, 0 ]

    # ======================================================================
    # Actual work starts here
    # ======================================================================
    new_col_names = { metric:'y' }
    old_col_names = { 'y':metric }

    df = df_in.copy()
    df['date'] = df['date'].astype('datetime64[ns]')

    # rename
    df.rename(columns=new_col_names, inplace = True)

    # Prep data
    pred_dts = df['date'][-n_test:]
    data = df['y'].values
    
    score, test, pred = walk_forward_validation(data, n_test, config)
    df_out = pd.DataFrame(columns = ['date', metric, 'type'])
    op = zip(pred_dts, test, pred)
    for tpl in op:
        tpl_2 = (tpl[0], tpl[2][0], 'predicted')
        df_out = df_out.append(pd.Series(tpl_2, index=df_out.columns), ignore_index = True)

    df_out.rename(columns=old_col_names, inplace = True)
    df_out.index = df_out['date']
    
    return df_out

if __name__ == '__main__':
    # ======================================================================
    # Pre-done by the tracker tool
    # ======================================================================
    today = datetime.now().date()
    metric = 'incidence'

    csv_file = f"covid19_us_{today}.csv"
    df = pd.read_csv(csv_file)

    # metric
    min_date = '2020-03-01'
    df = df[['date', metric]]
    df = df[df['date'] >= min_date]
    df = pd.DataFrame(df.groupby('date')[metric].sum())
    df['date'] = df.index
    # predict
    df_out = get_lstm_rslts(df, metric)
    print(df_out)
