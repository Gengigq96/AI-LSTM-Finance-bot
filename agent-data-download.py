from data import download_financial_data
from datetime import datetime

# Ejemplo de uso programático
data = download_financial_data(
    ticker='AAPL',
    start=datetime(2025, 1, 1),
    end=datetime(2025, 3, 1),
    mode='p'
)

# O en modo live con periodo personalizado
live_data = download_financial_data(
    ticker='AAPL',
    mode='l',
    period='5d'
)

print(live_data.head())

