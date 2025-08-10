from datetime import datetime
import dukascopy_python as dcp
import dukascopy_python.instruments as dcpi
import pandas as pd
from collections import defaultdict

'''
Bazujemy na analizie historycznej notowań różnych instrumentów inwestycyjnych.
Dane historyczne udostępnia wiele isntytucji, np: Dukascopy.
https://www.dukascopy.com/swiss/pl/marketwatch/historical/
Jest to szwajcarski bank, który z perspektywy osoby poszukującej źródła
danych udostępnia notowania instrumentów za pomocą biblioteki dukascopy_python.


Dukascopy daje możliwość pobierania danych za pomocą tej specjalnej biblioteki
pythonowej, co jest bardzo wygodnym rozwiązaniem.
'''

def display_available_instruments(group_filter: str = None):
    """
    Pobieranie i wyświetlanie listy dostępnych instrumentów z Dukascopy
    i ich sortowanie.
    Tych instrumentów jest bardzo dużo, więc trzeba uporządkować 
    ich wyswietlanie.
    Działanie:
    - Jeśli group_filter jest None, wyświetla listę dostępnych grup.
    - Jeśli group_filter jest podany, wyświetla instrumenty z tej grupy
      w formacie wielokolumnowym.

    Args:
        group_filter (str, optional): Nazwa grupy do wyświetlenia (np. 'FX').
                                      Wielkość liter nie ma znaczenia.
    """

    print("Pobieranie listy dostępnych instrumentów...")
    
    grouped_instruments = defaultdict(list)
    
    # Iteracja po wszystkich nazwach w module instruments.
    for var_name in dir(dcpi):
        # poszukiwanie zmiennych przechowujących nazwy instrumentów.
        if var_name.startswith('INSTRUMENT_'):
            try:
                # Podział nazwy zmiennej, aby wyodrębnić grupę.
                # Np. z 'INSTRUMENT_FX_CROSSES_AUD_CAD' pobiera 'FX'.
                group = var_name.split('_')[1]
                
                # Wartość zmiennej to właściwa nazwa instrumentu.
                instrument_name = getattr(dcpi, var_name)
                
                # Dodanie do listy.
                if isinstance(instrument_name, str):
                    grouped_instruments[group].append(instrument_name)
            except (IndexError, AttributeError):
                # Ignorowanie zmiennych niepasujących do wzorca.
                continue
            
    print("-" * 80)
    
    if group_filter is None:
        # Tryb 1: Wyświetl tylko dostępne grupy
        print("Dostępne grupy instrumentów:")
        sorted_groups = sorted(grouped_instruments.keys())
        for i, group in enumerate(sorted_groups, 1):
            print(f"  {i}. {group}")
        print("-" * 80)
        print("Aby zobaczyć instrumenty, wywołaj funkcję z filtrem, np.:")
        print("display_available_instruments(group_filter='FX')")
        print("-" * 80)
    else:
        # Tryb 2: Wyświetl instrumenty z wybranej grupy
        target_group = group_filter.upper()
        if target_group in grouped_instruments:
            print(f"Instrumenty w grupie: === {target_group} ===")
            
            instruments = sorted(grouped_instruments[target_group])
            num_columns = 4 # Ile kolumn chcemy wyświetlić
            
            # Obliczenie optymalnej szerokości kolumny
            col_width = max(len(name) for name in instruments) + 3
            
            # Drukowanie w kolumnach
            for i in range(0, len(instruments), num_columns):
                row = instruments[i:i+num_columns]
                # Użycie ljust do wyrównania tekstu w kolumnach
                print("".join(name.ljust(col_width) for name in row))

            print("-" * 80)
        else:
            print(f"Błąd: Grupa '{target_group}' nie została znaleziona.")
            print("Dostępne grupy:", 
                  ", ".join(sorted(grouped_instruments.keys())))
            print("-" * 80)


def fetch_dukascopy_data(instrument: str, 
                         start_date: datetime, 
                         end_date: datetime, 
                         interval: str = '1DAY', 
                         offer_side: str = 'B') -> pd.DataFrame:
    """
    Funkcja pobiera dane historyczne z Dukascopy i zwraca DataFrame z danymi
    Timestamp, OHLC i Volume.

    Args:
        instrument (str): Nazwa instrumentu (np. 'EUR/USD').
        start_date (datetime): Data początkowa.
        end_date (datetime): Data końcowa.
        interval (str, optional): Interwał czasowy. Domyślnie '1DAY'.
        offer_side (str, optional): Strona oferty. Domyślnie 'B'.

    Returns:
        pd.DataFrame: DataFrame z danymi historycznymi lub pusty 
        DataFrame w przypadku błędu.
    """
    print(f"Pobieranie danych dla {instrument}, \
          okres: {start_date.date()} - {end_date.date()}...")
    try:
        # Pobranie danych
        df = dcp.fetch(instrument, interval, offer_side, start_date, end_date)
        print("Pobieranie danych zakończone.")
        return df
    except Exception as e:
        print(f"Wystąpił błąd podczas pobierania danych: {e}")
        return pd.DataFrame() # Zwraca pusty DataFrame w razie błędu

