
import yfinance as yf
import datetime
from yahoo_fin import stock_info as si


def obtener_opciones_yahoo_finance(ticker = 'GGAL'):
    
    data = yf.Ticker(ticker)
    vencimientos = data.options

    calls = data.option_chain(vencimientos[0])[0]
    puts = data.option_chain(vencimientos[0])[1]

    for vencimiento in vencimientos[1:]:
        calls = calls.append(data.option_chain(vencimiento)[0])
        puts = puts.append(data.option_chain(vencimiento)[1])

    panel_opciones = calls.append(puts)

    panel_opciones['Spot'] = (data.info['bid']+data.info['ask'])/2
    
    panel_opciones['Ticker'] = ticker
    return panel_opciones


def obtener_panel_opciones_nyse(ticker='GGAL', clean_flag=False):

    panel_opciones = obtener_opciones_yahoo_finance(ticker)

    panel_opciones['Moneyness'] = 0.0

    panel_opciones['TTM'] = 0
    panel_opciones['CallPut'] = ''

    panel_opciones = panel_opciones.reset_index()


    for idx in list(panel_opciones.index.values):
        year = 2000 + int(panel_opciones.contractSymbol.values[idx][4:6])
        month = int(panel_opciones.contractSymbol.values[idx][6:8])
        day = int(panel_opciones.contractSymbol.values[idx][8:10])
        callput = panel_opciones.contractSymbol.values[idx][10:11]

        hoy = datetime.date.today()
        expiry_datetime = datetime.date(year, month, day)
        ttm = (expiry_datetime - hoy).days

        panel_opciones['TTM'].values[idx] = ttm
        panel_opciones['CallPut'].values[idx] = callput
        panel_opciones['Moneyness'].values[idx] = panel_opciones['Spot'].values[idx] / panel_opciones['strike'].values[idx]

    if clean_flag == True:
        panel_opciones = panel_opciones.rename(
            columns={'lastTradeDate': 'Last_Date', 'contractSymbol': 'Especie', 'strike': 'Strike', 'bid': 'Bid',
                     'ask': 'Ask', 'lastPrice': 'Last'}, inplace=False)

        panel_opciones = panel_opciones.sort_values(['TTM', 'Ticker', 'Strike', 'CallPut'])

        panel_opciones = panel_opciones[['Especie', 'Ticker', 'Spot', 'CallPut', 'Strike', 'TTM', 'Last', 'Moneyness', 'impliedVolatility', 'Ask','Bid']]

    return panel_opciones

