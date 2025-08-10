# Korzystamy z biblioteki Pandas TA
import pandas_ta as ta
import pandas as pd
import numpy as np

'''
Pierwszy alfabetycznie dostępny w bibliotece Pandas TA wskaźnik trendu to ADX
Average Directional Index
ADX:
Mierzy: Siłę trendu
Wskaźniki: ADX_(liczba sesji), DMP_(liczba sesji), DMN_(liczba sesji)
ADX <- Główna linia wskaźnika <- pokazuje jak silny jest obecny trend
DMP <- Linia kierunkowa dodatnia <- mierzy siłę ruchu w górę
DMN <- Linie kierunkowa ujemna <- mierzy siłę ruchu w dół

Interpretacja:
ADX < 20-25: Brak wyraźnego trendu - konsolidacja
ADX > 20-25: Brak Wyraźnego trendu - trend zaczyna się kształtować, 
            jeśli wartość rośnie to trend nabiera siły
ADX > 40-50: Bardzo silny, dojrzały trend
DMP > DMN - Trend wzrostowy
DMP < DMN - Trend spadkowy

Ograniczenia:
Opóźnienie. Wskaźnik może potwierdzić istniejący trend, ale nie przewidzieć go.
Na dynamicznych rynkach może dawać spóźnione sygnały

Oczekiwany zakres danych
ADX <- 0-100
DMP <- 0-100 lub 0-1
DMN <- 0-100 lub 0-1
'''

# Funkcja obliczająca ADX
def calculate_adx(df: pd.DataFrame, forming_trend_threshold=25,
                  trend_threshold=45, **kwargs):
    """
    Oblicza wskaźnik ADX, standaryzuje go i dodaje go do DataFrame.

    Zadania:
        1. Obliczenie ADX i współczynników pomocniczych
        2. Standaryzacja zakresu danych
        3. Dodanie kolumn - flag identyfikujących trend

    Args:
        df (pd.DataFrame): DataFrame z danymi OHLC.
        **kwargs: Argumenty akceptowalne przez pandas_ta.adx:
            length (int): Okres ADX. Default: 14
            lensig (int): Długość sygnału ADX. Default: lenght
            mamode (str): Rodzaj średniej kroczącej. Default: 'rma'
            scalar (float): Mnożnik. Default: 100
            drift (int): Przesunięcie. Default: 1
            offset (int): Przesunięcie wyniku. Default: 0
        forming_trend_threshold (int): Próg dla współczynnika ADX,
                                        dla którego uznajemy,
                                        że trend się kształtuje.
                                        Default: 25
        trend_threshold (int): Próg dla współczynnika ADX, 
                                dla którego uznajemy, 
                                że mamy silny trend. 
                                Default: 45
    Returns:
        pd.DataFrame: DataFrame z dodanymi kolumnami ADX, DMP, DMN
        Jesli trzeba ustandaryzować dane w kolumnach DMP i DMN
        to dodatkowo dodane zostaną kolumny: DMP_scaled, DMN_scaled
        Ostatnia dodana kolumna to flaga mówiąca o tym 
        w jakiej fazie jest rynek: konsolidacji, kształtującego się
        trendu (wzrostowego/spadkowego) lub w trendzie (wzrostowym/
                                                        spadkowym)
    """

    # --- Obliczanie wartości współczynników ---
    
    # Zapamiętanie oryginalnych nazw kolumn przed dodatniem nowych
    original_cols_names = set(df.columns)
    
    # Obliczenie ADX, append=True -> dodanie do df wyników wywołania 
    # funkcji ADX
    df.ta.adx(append=True, **kwargs)
    
    # Identyfikacja nowych kolumn dodanych przez funkcję
    new_cols_names = set(df.columns) - original_cols_names
    
    # W zależnosci od użytych parametrów nazwy kolumn mogą różnić się
    # Tworzenie słownika do przechowywania dynamicznych nazw kolumn
    adx_col_names = {}
    for col in new_cols_names:
        if col.startswith('ADX_'):
            adx_col_names['adx'] = col
        elif col.startswith('DMP_'):
            adx_col_names['dmp'] = col
        elif col.startswith('DMN_'):
            adx_col_names['dmn'] = col
    
    # Jeśli nie znaleziono kluczowych kolumn, zakończ
    if len(adx_col_names) < 3:
        print("Nie udało się zidentyfikować kolumn ADX, DMP, DMN.")
        return df    
    
    # --- Standaryzacja zakresu wartości ---
    
    dmp_col, dmn_col = adx_col_names['dmp'], adx_col_names['dmn']

    # Sprawdzenie potrzeby standaryzacji i wykonanie jej, jesli jest wymagana
    if not df[dmp_col].dropna().empty and df[dmp_col].dropna().max() <= 1.0:
        df[f'{dmp_col}_scaled'] = df[dmp_col] * 100
        # Jesli dojdzie do utworzenia nowej kolumny - trzeba zaktualizaować 
        # dmp_col
        dmp_col = f'{dmp_col}_scaled'
        
    if not df[dmn_col].dropna().empty and df[dmn_col].dropna().max() <= 1.0:
        df[f'{dmn_col}_scaled'] = df[dmn_col] * 100
        # Jesli dojdzie do utworzenia nowej kolumny - trzeba zaktualizaować 
        # dmp_col
        dmn_col = f'{dmn_col}_scaled'
        
    # --- Dodanie flag indetyfikujących trend ---
    adx_col = adx_col_names['adx']
    
    # Kolumna ze statusem trendu (Trend, Formowanie, Konsolidacja)
    
    # Warunki określające stan rynku
    is_trending = df[adx_col] > trend_threshold
    is_forming = df[adx_col] > forming_trend_threshold \
        and df[adx_col].diff() > 0
    trend_direction = df[dmp_col] > df[dmn_col]

    # Status trendu
    status_conditions = [
        is_trending,
        ~is_trending & is_forming
        ]

    status_choices = [
        'Trending'
        'Forming'
        ]
    
    df['trend_status'] = np.selection(status_conditions, 
                                      status_choices, 
                                      default = 'Consolidation')

    # Kolumna z kierunkiem trendu
    direction_conditions = [
        (df['trend_status'] != 'Consolidation') & trend_direction,
        (df['trend_status'] != 'Consolidation') & ~trend_direction
        ]

    direction_choices = [
        'Upward',
        'Downward'
        ]
    
    df['trend_direction'] = np.select(direction_conditions, 
                                      direction_choices, 
                                      default='Lateral')
    
    # Zwrot df z wyliczonymi wskaźnikami i flagami
    return df