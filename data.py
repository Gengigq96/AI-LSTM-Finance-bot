import click
import pandas as pd

import yfinance as yf
# python .\data.py 'AAPL' 2025-01-01 2025-03-01 --mode l
@click.command()
@click.argument('ticker', type=str)
@click.argument('start', type=click.DateTime(formats=["%Y-%m-%d"]), required=False) 
@click.argument('end', type=click.DateTime(formats=["%Y-%m-%d"]), required=False)
@click.option('--mode', type=click.Choice(['l', 'p'], case_sensitive=False), default='l', 
                help="Specify the mode: 'l' for live (default) or 'p' for period.")

def main(ticker, start, end, mode):

    if mode == 'p':
        if not start or not end:
            raise click.UsageError("For mode 'p', both 'start' and 'end' dates are required.")
    elif mode == 'l':
        if start or end:
            print(f"Note: In 'live' mode, the dates are not required, but you've provided them. They will be ignored.")

    start_str = start.strftime("%Y-%m-%d") if start else None
    end_str = end.strftime("%Y-%m-%d") if end else None

    if mode == 'p':
        data = yf.download(ticker, start=start_str, end=end_str)
    elif mode == 'l':
        ticker_token = yf.Ticker(ticker)
        data = ticker_token.history(period='1d')

    data = yf.download(ticker, start=start_str, end=end_str)
    nombre_archivo = f"{ticker}_datos_{start_str}_{end_str}.xlsx"
    data.to_excel(nombre_archivo, index=True)


if __name__ == "__main__":
    main()
