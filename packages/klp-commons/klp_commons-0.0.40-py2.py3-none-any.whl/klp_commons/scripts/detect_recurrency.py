import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas.tseries.offsets import MonthEnd
import matplotlib.cm as cm
import scipy.stats



def DetectRecurrencyI(
                      trans_data : pd.DataFrame,
                      amount_tolerance : float=0.01, 
                      period_tolerance : int=6,
                      n_days : int=3,
                      client_col: str =None,
                      time_col: str = None, 
                      amount_col: str = None,
                      config: dict = None
                      ):
    """It takes as arguments the dataframe of choosen a customer, an integer "period_tolerance" that is the minimum number of occuracy of an amount that it be selected, a float number "amount_tolerance" that is the accepted range for the amount, an integer "n_days" that is the accepted variance in the payement day. It returns a plot scatter of all the transactions where the noise amount (not recurring) are in grey and the  recurring amounts in different color."""
    if config is not None:
        client_col = config.customer_id
        amount_col = config.trans_amount
        time_col = config.trans_date

    # Creation of the new columns
    # number_occuracy_big, trans_data
    number_occuracy_big, account_table = _complete_table(trans_data, 
                                period_tolerance=period_tolerance,
                                client_col=client_col, 
                                time_col=time_col, 
                                amount_col=amount_col,
                                config=config)

    # Check the time rules for recurrency
    number_occuracy_big['day_of_month_cond'] = number_occuracy_big[amount_col].map(lambda x: 
                        (number_occuracy_big[(number_occuracy_big[amount_col] > x - x * amount_tolerance)
                                    & 
                    (number_occuracy_big[amount_col] <= x + x * amount_tolerance)]
                     .day_of_month.value_counts().count() < n_days))

    number_occuracy_big['number_day_end_month_cond'] = number_occuracy_big[amount_col].map(lambda x:
           (number_occuracy_big[(number_occuracy_big[amount_col] > x - x * amount_tolerance)
                                    & 
                    (number_occuracy_big[amount_col] <= x + x * amount_tolerance)]
                     .number_day_end_month.value_counts().count() < n_days))

    number_occuracy_big['number_business_day_end_month_cond'] = number_occuracy_big[amount_col].map(lambda x:
                  (number_occuracy_big[(number_occuracy_big[amount_col] >= x - x * amount_tolerance)
                                    & 
                    (number_occuracy_big[amount_col] <= x + x * amount_tolerance)]
                     .number_business_day_end_month.value_counts().count() < n_days))
    
    number_occuracy_big['rec'] = ((number_occuracy_big['day_of_month_cond'] == True) |
                        (number_occuracy_big['number_day_end_month_cond'] == True) |
                        (number_occuracy_big['number_business_day_end_month_cond'] == True))
        
    _plot_rec(account_table, 
            number_occuracy_big, 
            amount_tolerance =amount_tolerance ,
            period_tolerance=period_tolerance,
            client_col=client_col, 
            time_col=time_col, 
            amount_col=amount_col,
            config=config)




    return number_occuracy_big[number_occuracy_big['rec'] == True]





def DetectRecurrencyII(
                        trans_data : pd.DataFrame,
                        amount_tolerance : float=0.01,
                        period_tolerance : int=6, 
                        n_days : int=3,
                        client_col: str =None,
                        time_col: str = None, 
                        amount_col: str = None,
                        type_col:str = None,
                        config: dict = None
                        ):
    """It takes as arguments the dataframe of choosen customer, an integer "period_tolerance" that is the minimum number of occuracy of an amount that it be selected, a float number "amount_tolerance" that is the accepted range for the amount, an integer "n_days" that is the accepted variance in the payement day. It returns a list of couple (recurring amount, number of occuracy of the corresponding amount), and a dictionnary where the keys are the listed recurring amounts and it values are the corresponding dataframe."""
    
    if config is not None:
        client_col = config.customer_id
        amount_col = config.trans_amount
        time_col = config.trans_date

                                
    
    if isinstance(trans_data, pd.DataFrame):

        rec_amount_freq, rec_table_dict, rec_table_unnamed_dict, rec_amount_unnamed_freq = _detect_recurrency(trans_data,
                                                            amount_tolerance=amount_tolerance,
                                                            period_tolerance=period_tolerance,
                                                            client_col=client_col, 
                                                            time_col=time_col, 
                                                            amount_col=amount_col,
                                                            type_col=type_col,
                                                            config=config)

    else:

        rec_amount_freq = []
        rec_table_dict = []
        rec_table_unnamed_dict = []
        rec_amount_unnamed_freq = []

        for i in trans_data:
            # rec_table_unnamed_dict, rec_amount_unnamed_freq
            _rec_amount_freq, _rec_table_dict, _, _ = _detect_recurrency(i,
                                                            amount_tolerance=amount_tolerance,
                                                            period_tolerance=period_tolerance,
                                                            client_col=client_col, 
                                                            time_col=time_col, 
                                                            amount_col=amount_col,
                                                            type_col=type_col,
                                                            config=config)

            rec_amount_freq.append(_rec_amount_freq)
            rec_table_dict.append(_rec_table_dict)

    return  rec_amount_freq, rec_table_dict, rec_table_unnamed_dict, rec_amount_unnamed_freq





def _complete_table(
                    trans_data : pd.DataFrame,
                    amount_tolerance : float=0.01,
                    period_tolerance : int=5,
                    client_col: str =None,
                    time_col: str = None, 
                    amount_col: str = None,
                    config: dict = None
                   ):
    """
    It takes as arguments the dataframe of a choosen customer, an integer "period_tolerance" that is the minimum number of occuracy of an amount that it be selected, a float number "amount_tolerance" that is the accepted range for the amount, an integer "n_days" that is the accepted variance in the payement day. It returns the same table with additionnal columns that are needed by the functions "DetectRecurrencyI" and "DetectRecurrencyII".
    """    
    if config is not None:
        client_col = config.customer_id
        amount_col = config.trans_amount
        time_col = config.trans_date
        
    
    # Creation of the number of occuracy column
    # obtener resultados que están cerca del primer monto encontrado ()
    trans_data['freq'] = trans_data[amount_col].map(lambda x: 
                                        np.sum((trans_data[amount_col] >= x - x * amount_tolerance)
                                                        & 
                                                (trans_data[amount_col] <= x + x * amount_tolerance)))

    
    # Creation of the time columns
    trans_data[time_col] = trans_data[time_col].astype('datetime64')

    
    # El parámetro 0 en MonthEnd sólo especifica avanzar hasta el final del mes dado.
    # Tenga en cuenta que si hubiéramos usado MonthEnd(1), 
    # tendríamos la siguiente fecha, que es al final del mes.
    
    # último día del mes de la fecha en cuestion
    trans_data['end_of_month'] = pd.to_datetime(
        trans_data[time_col], format="%Y%m") + MonthEnd(0)
    
    # extraer el día 
    trans_data['day_of_month'] = trans_data[time_col].dt.day
    
    # número de días para finalizar el mes
    trans_data['number_day_end_month'] = trans_data.end_of_month.dt.day - trans_data.day_of_month
    
    # extraer sólo la fecha
    A = [d.date() for d in trans_data[time_col]]
    B = [d.date() for d in trans_data['end_of_month']]
    
    # cuenta el número de días válidos (días hábiles) dado el rango de fechas
    trans_data['number_business_day_end_month'] = np.busday_count(A, B)
    
    # Selecting the condidate for Recurring values 
    number_occuracy_big = trans_data[trans_data['freq'] >= period_tolerance].copy()

    return number_occuracy_big, trans_data



    
def _detect_recurrency(
                        trans_data : pd.DataFrame,
                        amount_tolerance : float=0.01,
                        period_tolerance : int=6, 
                        n_days : int=3,
                        client_col: str =None,
                        time_col: str = None, 
                        amount_col: str = None,
                        type_col:str = None,
                        config: dict = None
                        ):
        
    """It is a private function used by "DetectRecurrencyII". The function "_detect_recurrency" takes one dataframe and returns a list and a dictionary. The list contained the couple recurring amount and their frequency in the dataframe."""

    if config is not None:
        client_col = config.customer_id
        amount_col = config.trans_amount
        time_col = config.trans_date
        type_col = config.trans_type
  
    #  number_occuracy_big, trans_data
    trans_data, account_table = _complete_table(trans_data, 
                                amount_tolerance =amount_tolerance ,
                                period_tolerance=period_tolerance,
                                client_col=client_col, 
                                time_col=time_col, 
                                amount_col=amount_col,
                                config=config)
    

    trans_data = trans_data.set_index([amount_col]).sort_index()
    
    

    X_unique = set(trans_data.index)

    rec_amount_freq = []
    rec_table_dict = {}
    
    rec_amount_unnamed_freq = []
    rec_table_unnamed_dict = {}
    # loop over the amounts
    for x in X_unique:

        rec = None

        # Table of the wanted amount related x
        # A = trans_data.loc[pd.Interval(x - amount_tolerance * x, x + amount_tolerance * x)]
        A = trans_data.loc[x - x *amount_tolerance:  x + x * amount_tolerance]

        # FOR CREDIT TRANSACTION
        if ((A.shape[0] >= period_tolerance) & (A[type_col].value_counts().count() == 1)):

            # most freq day happens at least 3 times
            day_of_month_cond = A.day_of_month.value_counts().count() < n_days
            
            number_day_end_month_cond = A.number_day_end_month.value_counts().count() < n_days
            
            number_business_day_end_month_cond = A.number_business_day_end_month.value_counts().count() < n_days
            
            nickname = A.nickname.unique().tolist()
            
            A.sort_values(by='value_date',ascending=False,inplace=True)
            
            #A['days_diff'] = A.groupby(['user_uid','nickname'])['value_date'].diff().apply(lambda x: x/np.timedelta64(-1, 'D')).fillna(0).astype('int64')
            
            
            # This table will be selected if one of the previous condition is true
            if (day_of_month_cond | number_day_end_month_cond | number_business_day_end_month_cond):
                rec = A
            
            list_day_diff = A.days_diff.values
            mean_day_diff = scipy.stats.mode(list(filter(lambda x: x > n_days, list_day_diff)))[0][0]
            
            if rec is not None:
                if len(nickname) == 1:
                    rec_amount_freq.append((nickname[0], x, A.shape[0], mean_day_diff))
                    rec_table_dict[(nickname[0], x, A.shape[0])] = rec
                else :
                    rec_amount_unnamed_freq.append(('_'.join(nickname), x, A.shape[0], mean_day_diff))
                    rec_table_unnamed_dict[('_'.join(nickname), x, A.shape[0])] = rec

    return rec_amount_freq, rec_table_dict, rec_table_unnamed_dict, rec_amount_unnamed_freq




def _plot_rec(
            account_table : pd.DataFrame,
            number_occuracy_big : pd.DataFrame,
            amount_tolerance : float=0.01,
            period_tolerance : int = 6,
            client_col: str =None,
            time_col: str = None, 
            amount_col: str = None,
            config: dict = None
            ):

    """it takes as argument a panda series (a column), bins and ranges and plot a histogram."""
    
    
    if config is not None:
        client_col = config.customer_id
        amount_col = config.trans_amount
        time_col = config.trans_date
    
    
  #  number_occuracy_big = account_table[account_table['rec'] == True]
    plt.style.use('seaborn-deep')
    fig, ax = plt.subplots(figsize=(20, 10))


    x2=account_table[account_table['freq'] < period_tolerance][time_col]
    y2=account_table[account_table['freq'] < period_tolerance][amount_col]

    rec = set(number_occuracy_big[number_occuracy_big['rec'] == True][amount_col])
    colors = cm.rainbow(np.linspace(0, 1, len(rec)))

    for  x, col in zip(rec, colors):
        x1=number_occuracy_big[(number_occuracy_big[amount_col] >= x - x * amount_tolerance)
                                                            & 
                            (number_occuracy_big[amount_col] <= x + x * amount_tolerance)][time_col]
        y1=number_occuracy_big[(number_occuracy_big[amount_col] >= x - x * amount_tolerance)
                                                            & 
                            (number_occuracy_big[amount_col] <= x + x * amount_tolerance)][amount_col]

        ax.plot(x1, y1, 's', color=col, markersize=5)
    ax.plot(x2, y2, 'o', markerfacecolor='black', markersize=6,  alpha=0.5)

    ax.set_xlabel('Date of transaction', fontsize=20)
    ax.set_ylabel('Amount of transaction', fontsize=20)

    ax.grid()

    plt.xticks(fontsize=14, rotation=30)
    plt.yticks(fontsize=14, rotation=0)
    plt.show()
    return 



