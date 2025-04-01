import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import matplotlib.pyplot as plt

def crear_dataset_trading(filepath, forward_window=3):
    """
    Crea dataset con acciones ÓPTIMAS que maximizan ganancias.
    
    Args:
        filepath: Ruta al Excel
        forward_window: Ventana para mirar precios futuros (default 3 días)
        
    Returns:
        pd.DataFrame con las acciones perfectas (1:vender, 2:comprar, 3:mantener)
    """
    # 1. Carga y limpieza
    df = pd.read_excel(filepath, skiprows=3)
    df.columns = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']
    
    # Convertir formato numérico europeo
    for col in ['Close', 'High', 'Low', 'Open']:
        df[col] = df[col].astype(str).str.replace(',', '.').astype(float)
    
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').reset_index(drop=True)
    
    # 2. Calcular acciones óptimas
    df['Future_Max'] = df['Close'].rolling(forward_window, min_periods=1).max().shift(-forward_window)
    df['Future_Min'] = df['Close'].rolling(forward_window, min_periods=1).min().shift(-forward_window)
    
    df['Action'] = 3  # Por defecto mantener
    
    # Condiciones para cada acción
    buy_condition = (df['Close'] < df['Future_Max']) & (df['Close'] <= df['Future_Min'] * 1.01)
    sell_condition = (df['Close'] > df['Future_Min']) & (df['Close'] >= df['Future_Max'] * 0.99)
    
    df.loc[buy_condition, 'Action'] = 2   # Comprar
    df.loc[sell_condition, 'Action'] = 1  # Vender
    
    # 3. Features técnicos
    df['MA_7'] = df['Close'].rolling(7).mean()
    df['MA_20'] = df['Close'].rolling(20).mean()
    df['RSI'] = RSIIndicator(df['Close'], window=14).rsi()
    
    bb = BollingerBands(df['Close'], window=20, window_dev=2)
    df['BB_Upper'] = bb.bollinger_hband()
    df['BB_Lower'] = bb.bollinger_lband()
    
    # 4. Normalización
    scaler = MinMaxScaler()
    cols_to_scale = ['Close', 'High', 'Low', 'Open', 'Volume', 
                    'MA_7', 'MA_20', 'RSI', 'BB_Upper', 'BB_Lower']
    df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])
    
    # 5. Limpieza final
    df = df.dropna().reset_index(drop=True)
    df = df.drop(['Future_Max', 'Future_Min'], axis=1)
    
    return df

# Ejemplo de uso
if __name__ == "__main__":
    # Crear dataset completo
    dataset = crear_dataset_trading('dataset\AAPL_datos_2010-01-01_2025-04-01_p_1d.xlsx')
    
    # Mostrar información del dataset
    print("Dataset completo para modelo de RL:")
    print(dataset.info())
    print("\nDistribución de acciones:")
    print(dataset['Action'].value_counts())
    
    # Guardar dataset
    dataset.to_excel('dataset\PROCESED-AAPL_datos_2010-01-01_2025-04-01_p_1d.xlsx', index=False)
    print("\nDataset guardado en 'dataset_trading_RL.xlsx'")


    plt.figure(figsize=(15,7))
    plt.plot(dataset['Date'], dataset['Close'], label='Precio Normalizado', alpha=0.7)
    plt.scatter(dataset[dataset['Action']==1]['Date'], 
                dataset[dataset['Action']==1]['Close'], 
                color='red', s=50, label='Vender')
    plt.scatter(dataset[dataset['Action']==2]['Date'], 
                dataset[dataset['Action']==2]['Close'], 
                color='green', s=50, label='Comprar')
    plt.title('Señales de Trading Generadas', fontsize=14)
    plt.legend()
    plt.grid(True)
    plt.show()
