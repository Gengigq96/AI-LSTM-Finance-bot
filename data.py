import click
import pandas as pd
import os
import yfinance as yf
from datetime import datetime

VALID_PERIODS = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']

def download_financial_data(ticker, start=None, end=None, mode='l', period='1d', export=None):
    """
    Download financial data for a given ticker.
    
    Args:
        ticker (str): Stock ticker symbol
        start (datetime/str): Start date (required for period mode)
        end (datetime/str): End date (required for period mode)
        mode (str): 'l' for live, 'p' for period
        period (str): Time period for live mode
        export (str): Path to export data (optional)
    
    Returns:
        pd.DataFrame: Financial data if not exported, None otherwise
    """
    # Convert datetime objects to strings if needed
    if isinstance(start, datetime):
        start = start.strftime("%Y-%m-%d")
    if isinstance(end, datetime):
        end = end.strftime("%Y-%m-%d")
    
    if mode == 'p':
        if not start or not end:
            raise ValueError("For mode 'p', both 'start' and 'end' dates are required.")
        data = yf.download(ticker, start=start, end=end)
        start_str, end_str = start, end
    elif mode == 'l':
        start_str, end_str = "NA", "NA"
        ticker_token = yf.Ticker(ticker)
        data = ticker_token.history(period=period)

    if export and not data.empty:
        if os.path.isdir(export) or not os.path.splitext(export)[1]:
            filename = f"{ticker}_datos_{start_str}_{end_str}.xlsx" if mode == 'p' else f"{ticker}_live_{period}.xlsx"
            export_path = os.path.join(export, filename)
        else:
            export_path = export

        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        data.to_excel(export_path, index=True)
        print(f"Data saved in {export_path}")
        return None
    
    return data if not data.empty else None

@click.command()
@click.argument('ticker', type=str)
@click.argument('start', type=click.DateTime(formats=["%Y-%m-%d"]), required=False) 
@click.argument('end', type=click.DateTime(formats=["%Y-%m-%d"]), required=False)
@click.option('--mode', type=click.Choice(['l', 'p'], case_sensitive=False), default='l', 
              help="Specify the mode: 'l' for live (default) or 'p' for period")
@click.option('--period', type=click.Choice(VALID_PERIODS, case_sensitive=False), default='1d',
              help="Time period for live mode (default: '1d')")
@click.option('--export', type=click.Path(), help="Export data to an XLSX file (provide a directory or full path).")
def cli(ticker, start, end, mode, period, export):
    """CLI interface for the financial data downloader"""
    try:
        result = download_financial_data(
            ticker=ticker,
            start=start,
            end=end,
            mode=mode,
            period=period,
            export=export
        )
        
        if result is not None and not export:
            print(result)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

if __name__ == "__main__":
    cli()