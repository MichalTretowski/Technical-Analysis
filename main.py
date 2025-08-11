from datetime import datetime
import pandas as pd
from data.loaders.dukascopy import display_available_instruments as display_instruments
from data.loaders.dukascopy import fetch_dukascopy_data as fetch_data
from indicators.trend.adx import calculate_adx as adx
import itertools

display_instruments(group_filter = 'FX')

instrument = 'EUR/USD'
start_date = datetime(2000, 1, 1)
end_date = datetime.today()
interval = '1DAY'
offer_side = 'B'

df = fetch_data(
        instrument = instrument, 
        start_date = start_date, 
        end_date = end_date, 
        interval = interval, 
        offer_side = offer_side
        )

print(df.info())

'''
Wskaźnik: ADX
Lista srednich
rma (Relative Moving Average)	Tryb domyślny dla ADX. 
    Jest to wygładzona średnia, podobna do EMA, ale o wolniejszej reakcji. 
    Utrzymuje wskaźnik w formie, jakiej chciał jego autor.
ema (Exponential Moving Average)	Najpopularniejsza alternatywa. 
    Wykładnicza średnia krocząca, która przykłada większą wagę do 
    najnowszych danych. 
    Reaguje na zmiany szybciej niż rma i sma.
sma	(Simple Moving Average)	Prosta średnia krocząca. Najbardziej podstawowy 
    rodzaj, który traktuje wszystkie dane z danego okresu jednakowo. 
    Jest wolniejsza i mniej reaktywna niż ema.
wma	(Weighted Moving Average)	Ważona średnia krocząca, która przypisuje 
    liniowo większą wagę nowszym danym. Jest szybsza od sma, 
    ale mniej popularna niż ema.
hma	(Hull Moving Average)	Średnia krocząca Hulla. Zaawansowana średnia, 
    zaprojektowana, aby być jednocześnie bardzo szybka i gładka. 
    Usuwa więcej szumu niż inne średnie.
dema	(Double EMA)	Podwójna wykładnicza średnia krocząca. 
    Bardziej agresywna wersja ema, która jeszcze szybciej reaguje 
    na zmiany cen, starając się zredukować opóźnienie.
tema	(Triple EMA)	Potrójna wykładnicza średnia krocząca. 
    Jeszcze bardziej agresywna niż dema. Dla traderów szukających 
    maksymalnej szybkości reakcji.
'''

# !!PAMIĘTAJ!! Duży zakres parametrów = ogromna ilosć kombinacji
# a to prowadzi do niezwykle dużego zapotrzebowania na moc obliczeniową
# a to spowoduje, że Twój komputer nie da rady
# W celu przeszukiwania dużych zakresów parametrów pomysl o wynajęciu zasobów
# chmurowych.

'''
Maksymalna kombinacja parametrów dla współpczynnika ADX:
    'forming_trend_threshold': list(range(20, 26)),
    'trend_threshold': list(range(40, 51)),
    'length': list(range(7, 31)),
    'lensig': list(range(3, 11)),
    'mamode': ['rma', 'ema', 'sma', 'wma', 'hma', 'dema', 'tema'],
Reszta może zostać defaultem
'''

# Do analizy wybieram tylko po kilka wartosci dla każdego parametru
param_grid = {
    'forming_trend_threshold': [20, 25],
    'trend_threshold': [40, 45, 50],
    'length': [7, 10, 15, 20, 25, 30],
    'lensig': [3, 6, 10],
    'mamode': ['rma', 'ema', 'hma', 'dema', 'tema']
    }

if not df.empty:
    print('\nRozpoczynam analizę dla wszystkich kombinacji parametrów')
    print("." * 20 + " (Grid Search) " + '.' * 20)

    df_adx = df.copy()
    
    param_names = list(param_grid.keys())
    param_values = list(param_grid.values())
    
    for combination in itertools.product(*param_values):
        
        current_params = dict(zip(param_names, combination))

        # lensig nie może być większy niż lenght
        if current_params['lensig'] > current_params['length']:
            continue # Przejdź do następnej iteracji pętli
        # hma potrzebuje dłuższego okresu niż 3
        if current_params['mamode'] == 'hma' and current_params['lensig'] < 4:
            continue
        
        key_abbr = {
            'lenght': 'len',
            'lensig': 'ls',
            'mamode': 'ma',
            'forming_trend_threshold': 'ft',
            'trend_threshold': 'tt'       
            }
        
        suffix_parts = [f'{key_abbr.get(key, key)}{value}' for key, value \
                        in current_params.items()]
        suffix = '_' + '_'.join(suffix_parts)
        
        print(f' - Przetwarzanie danych dla kombinacji: {suffix}...')
        
        temp_df = df_adx.copy()
        adx(temp_df, col_suffix = suffix, **current_params)
    
        new_columns = temp_df.columns.difference(df_adx.columns)
        if not new_columns.empty:
            df_adx = df_adx.join(temp_df[new_columns])
        else:
            print(f'!Warning!: Kombinacja {suffix} nie wygenerowała wynikóW')
    print("\nAnaliza Grid Search zakończona.")
    
    # Wyświetlamy informacje o wszystkich kolumnach w DataFrame
    print("\nStruktura finalnego DataFrame:")
    pd.set_option('display.max_rows', None) # Aby wyświetlić wszystkie kolumny
    print(df_adx.info())
    pd.reset_option('display.max_rows')

else:
    print("\nNie udało się pobrać danych. Zatrzymuję skrypt.")