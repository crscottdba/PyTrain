#Signet Jewelers Stock/Covid Tracker
import pandas as pd, datetime
import plotly.graph_objects as go

def main():
    display_data(wrangle_data(*scrape_data()))

def scrape_data():
    def scrape_yahoo(id_):
        BASE_URL = 'https://query1.finance.yahoo.com/v7/finance/download/'
        now  = int(datetime.datetime.now().timestamp())
        url  = f'{BASE_URL}{id_}?period1=1579651200&period2={now}&interval=1d&events=history'
        return pd.read_csv(url, usecols=['Date', 'Close']).set_index('Date').Close 
    covid = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv', 
                        usecols=['date', 'total_cases'])
    covid = covid.groupby('date').sum()
    dow, gold, signet = [scrape_yahoo(id_) for id_ in ('^DJI', 'GC=F', 'SIG')]
    dow.name, gold.name, signet.name = 'Dow Jones', 'Gold', 'Signet'
    return covid, dow, gold, signet

def wrangle_data(covid, dow, gold, signet):
    df = pd.concat([covid, dow, gold, signet], axis=1)
    df = df.loc['2020-02-23':].iloc[:-2]
    df = df.interpolate()
    df.iloc[:, 1:] = df.rolling(10, min_periods=1, center=True).mean().iloc[:, 1:]
    df.iloc[:, 1:] = df.iloc[:, 1:] / df.iloc[0, 1:] * 100
    return df

def display_data(df):
    def get_trace(col_name):
        return go.Scatter(x=df.index, y=df[col_name], name=col_name, yaxis='y2')
    traces = [get_trace(col_name) for col_name in df.columns[1:]]
    traces.append(go.Scatter(x=df.index, y=df.total_cases, name='Total Cases', yaxis='y1'))
    figure = go.Figure()
    figure.add_traces(traces)
    figure.update_layout(
        yaxis1=dict(title='Total Cases', rangemode='tozero'),
        yaxis2=dict(title='%', rangemode='tozero', overlaying='y', side='right'),
        legend=dict(x=1.1)
    ).show()

if __name__ == '__main__':
    main()