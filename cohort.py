import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import datetime as dt
from textwrap import wrap
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from pathlib import Path

def calc_Average(path):
    myFile = Path(path)
    aveRetained = 0

    if myFile.is_file():
        transaction_df = pd.read_csv(path)
        # Data Pre-processing
        # Replace the ' 's with NaN
        transaction_df = transaction_df.replace(" ",np.NaN)
        # Impute the missing values with mean imputation
        transaction_df = transaction_df.fillna(transaction_df.mean())

        for col in transaction_df.columns:
            # Check if the column is of object type
            if transaction_df[col].dtypes == 'object':
                # Impute with the most frequent value
                transaction_df[col] = transaction_df[col].fillna(transaction_df[col].value_counts().index[0])
        transaction_df['Date Issue'] =  pd.to_datetime(transaction_df['Date Issue'],errors='coerce', format='%Y-%m-%d')


        # A function that will parse the date Time based cohort:  1 day of month
        def get_month(x): return dt.datetime(x.year, x.month, 1) 
        # Create transaction_date column based on month and store in TransactionMonth
        transaction_df['TransactionMonth'] = transaction_df['Date Issue'].apply(get_month) 
        # Grouping by customer_id and select the InvoiceMonth value
        grouping = transaction_df.groupby('Client Number')['TransactionMonth'] 
        # Assigning a minimum InvoiceMonth value to the dataset
        transaction_df['CohortMonth'] = grouping.transform('min')


        transaction_df['TransactionYear'] = transaction_df['Date Issue'].dt.year
        # Grouping by customer_id and select the InvoiceMonth value
        grouping = transaction_df.groupby('Client Number')['TransactionYear'] 
        # Assigning a minimum InvoiceMonth value to the dataset
        transaction_df['CohortYear'] = grouping.transform('min')

        def get_date_int(df, column):
            year = df[column].dt.year
            month = df[column].dt.month
            day = df[column].dt.day
            return year, month, day
        # Getting the integers for date parts from the `InvoiceDay` column
        transcation_year, transaction_month, _ = get_date_int(transaction_df, 'TransactionMonth')
        # Getting the integers for date parts from the `CohortDay` column
        cohort_year, cohort_month, _ = get_date_int(transaction_df, 'CohortMonth')

        #  Get the  difference in years
        years_diff = transcation_year - cohort_year
        # Calculate difference in months
    
        transaction_df['CohortIndex'] = years_diff + 1 
        
        # Counting daily active user from each chort
        grouping = transaction_df.groupby(['CohortYear', 'CohortIndex'])
        # Counting number of unique customer Id's falling in each group of CohortMonth and CohortIndex
        cohort_data = grouping['Client Number'].apply(pd.Series.nunique)
        cohort_data = cohort_data.reset_index()
        # Assigning column names to the dataframe created above
        cohort_counts = cohort_data.pivot(index='CohortYear',
                                        columns ='CohortIndex',
                                        values = 'Client Number')

        cohort_sizes = cohort_counts.iloc[:,0]
        retention = cohort_counts.divide(cohort_sizes, axis=0)
        # Coverting the retention rate into percentage and Rounding off.
        retention.round(3)*100

        retained = retention.round(3)*100
        aveRetained = retained.mean().mean()
        aveRetained = round(aveRetained, 2)
        return aveRetained
    
    return aveRetained


def defaultAve():
    path = 'apps/static/assets/uploads/cohort_sample1.xlsx'
    myFile = Path(path)
    aveRetained = 0

    if myFile.is_file():
        transaction_df = pd.read_excel(path)

        # Data Pre-processing
        # Replace the ' 's with NaN
        transaction_df = transaction_df.replace(" ",np.NaN)
        # Impute the missing values with mean imputation
        transaction_df = transaction_df.fillna(transaction_df.mean())

        transaction_df = transaction_df.dropna(subset = ['customer_id'])

        for col in transaction_df.columns:
            # Check if the column is of object type
            if transaction_df[col].dtypes == 'object':
                # Impute with the most frequent value
                transaction_df[col] = transaction_df[col].fillna(transaction_df[col].value_counts().index[0])

        # A function that will parse the date Time based cohort:  1 day of month
        def get_month(x): return dt.datetime(x.year, x.month, 1) 
        # Create transaction_date column based on month and store in TransactionMonth
        transaction_df['TransactionMonth'] = transaction_df['transaction_date'].apply(get_month) 
        # Grouping by customer_id and select the InvoiceMonth value
        grouping = transaction_df.groupby('customer_id')['TransactionMonth'] 
        # Assigning a minimum InvoiceMonth value to the dataset
        transaction_df['CohortMonth'] = grouping.transform('min')
        # printing top 5 rows

        transaction_df['TransactionYear'] = transaction_df['transaction_date'].dt.year
        # Grouping by customer_id and select the InvoiceMonth value
        grouping = transaction_df.groupby('customer_id')['TransactionYear'] 
        # Assigning a minimum InvoiceMonth value to the dataset
        transaction_df['CohortYear'] = grouping.transform('min')

        def get_date_int(df, column):
            year = df[column].dt.year
            month = df[column].dt.month
            day = df[column].dt.day
            return year, month, day
        # Getting the integers for date parts from the `InvoiceDay` column
        transcation_year, transaction_month, _ = get_date_int(transaction_df, 'TransactionMonth')
        # Getting the integers for date parts from the `CohortDay` column
        cohort_year, cohort_month, _ = get_date_int(transaction_df, 'CohortMonth')

        #  Get the  difference in years
        years_diff = transcation_year - cohort_year
        # Calculate difference in months
    
        transaction_df['CohortIndex'] = years_diff + 1 
        
        # Counting daily active user from each chort
        grouping = transaction_df.groupby(['CohortYear', 'CohortIndex'])
        # Counting number of unique customer Id's falling in each group of CohortMonth and CohortIndex
        cohort_data = grouping['customer_id'].apply(pd.Series.nunique)
        cohort_data = cohort_data.reset_index()
        # Assigning column names to the dataframe created above
        cohort_counts = cohort_data.pivot(index='CohortYear',
                                        columns ='CohortIndex',
                                        values = 'customer_id')

        cohort_sizes = cohort_counts.iloc[:,0]
        retention = cohort_counts.divide(cohort_sizes, axis=0)
        # Coverting the retention rate into percentage and Rounding off.
        retention.round(3)*100

        retained = retention.round(3)*100
        aveRetained = retained.mean().mean()
        aveRetained = round(aveRetained, 2)
        return aveRetained
    
    return aveRetained




def visualize():
    # Load Sample Dataset
    path = 'apps/static/assets/uploads/cohort_sample1.xlsx'
    transaction_df = pd.read_excel(path)
    
    # Data Pre-processing
    # Replace the ' 's with NaN
    transaction_df = transaction_df.replace(" ",np.NaN)
    # Impute the missing values with mean imputation
    transaction_df = transaction_df.fillna(transaction_df.mean())

    transaction_df = transaction_df.dropna(subset = ['customer_id'])

    for col in transaction_df.columns:
        # Check if the column is of object type
        if transaction_df[col].dtypes == 'object':
            # Impute with the most frequent value
            transaction_df[col] = transaction_df[col].fillna(transaction_df[col].value_counts().index[0])

    # A function that will parse the date Time based cohort:  1 day of month
    def get_month(x): return dt.datetime(x.year, x.month, 1) 
    # Create transaction_date column based on month and store in TransactionMonth
    transaction_df['TransactionMonth'] = transaction_df['transaction_date'].apply(get_month) 
    # Grouping by customer_id and select the InvoiceMonth value
    grouping = transaction_df.groupby('customer_id')['TransactionMonth'] 
    # Assigning a minimum InvoiceMonth value to the dataset
    transaction_df['CohortMonth'] = grouping.transform('min')
    # printing top 5 rows

    transaction_df['TransactionYear'] = transaction_df['transaction_date'].dt.year
    # Grouping by customer_id and select the InvoiceMonth value
    grouping = transaction_df.groupby('customer_id')['TransactionYear'] 
    # Assigning a minimum InvoiceMonth value to the dataset
    transaction_df['CohortYear'] = grouping.transform('min')

    def get_date_int(df, column):
        year = df[column].dt.year
        month = df[column].dt.month
        day = df[column].dt.day
        return year, month, day
    # Getting the integers for date parts from the `InvoiceDay` column
    transcation_year, transaction_month, _ = get_date_int(transaction_df, 'TransactionMonth')
    # Getting the integers for date parts from the `CohortDay` column
    cohort_year, cohort_month, _ = get_date_int(transaction_df, 'CohortMonth')

    #  Get the  difference in years
    years_diff = transcation_year - cohort_year
    # Calculate difference in months
   
    transaction_df['CohortIndex'] = years_diff + 1 
    
    # Counting daily active user from each chort
    grouping = transaction_df.groupby(['CohortYear', 'CohortIndex'])
    # Counting number of unique customer Id's falling in each group of CohortMonth and CohortIndex
    cohort_data = grouping['customer_id'].apply(pd.Series.nunique)
    cohort_data = cohort_data.reset_index()
    # Assigning column names to the dataframe created above
    cohort_counts = cohort_data.pivot(index='CohortYear',
                                    columns ='CohortIndex',
                                    values = 'customer_id')

    cohort_sizes = cohort_counts.iloc[:,0]
    retention = cohort_counts.divide(cohort_sizes, axis=0)
    # Coverting the retention rate into percentage and Rounding off.
    retention.round(3)*100
    

    csfont = {'fontname':'Inter'}

    plt.figure(figsize=(10.8,8))
    plt.title('Customer Retention Matrix: Annual Cohorts', fontsize = 16, fontweight= 600, **csfont)
    plt.ylabel('Cohort Year',**csfont,fontsize=12,fontweight=600)
    plt.xlabel('Cohort Index',**csfont,fontsize=12,fontweight=600)
    # Creating the heatmap
    ax = sns.heatmap(retention,annot=True,fmt='.0%')
    fig = ax.get_figure()
    fig.savefig("./apps/static/assets/images/cohort/heatmap-general.png")
    return


def loadVis(all_details):

    transaction_df = pd.read_csv(all_details)
    # Data Pre-processing
    # Replace the ' 's with NaN
    transaction_df = transaction_df.replace(" ",np.NaN)
    # Impute the missing values with mean imputation
    transaction_df = transaction_df.fillna(transaction_df.mean())

    for col in transaction_df.columns:
        # Check if the column is of object type
        if transaction_df[col].dtypes == 'object':
            # Impute with the most frequent value
            transaction_df[col] = transaction_df[col].fillna(transaction_df[col].value_counts().index[0])
    transaction_df['Date Issue'] =  pd.to_datetime(transaction_df['Date Issue'],errors='coerce', format='%Y-%m-%d')

    # A function that will parse the date Time based cohort:  1 day of month
    def get_month(x): return dt.datetime(x.year, x.month, 1) 
    # Create transaction_date column based on month and store in TransactionMonth
    transaction_df['TransactionMonth'] = transaction_df['Date Issue'].apply(get_month) 
    # Grouping by customer_id and select the InvoiceMonth value
    grouping = transaction_df.groupby('Client Number')['TransactionMonth'] 
    # Assigning a minimum InvoiceMonth value to the dataset
    transaction_df['CohortMonth'] = grouping.transform('min')
    # printing top 5 rows

    transaction_df['TransactionYear'] = transaction_df['Date Issue'].dt.year
    # Grouping by customer_id and select the InvoiceMonth value
    grouping = transaction_df.groupby('Client Number')['TransactionYear'] 
    # Assigning a minimum InvoiceMonth value to the dataset
    transaction_df['CohortYear'] = grouping.transform('min')

    def get_date_int(df, column):
        year = df[column].dt.year
        month = df[column].dt.month
        day = df[column].dt.day
        return year, month, day
    # Getting the integers for date parts from the `InvoiceDay` column
    transcation_year, transaction_month, _ = get_date_int(transaction_df, 'TransactionMonth')
    # Getting the integers for date parts from the `CohortDay` column
    cohort_year, cohort_month, _ = get_date_int(transaction_df, 'CohortMonth')

    #  Get the  difference in years
    years_diff = transcation_year - cohort_year
    # Calculate difference in months

    transaction_df['CohortIndex'] = years_diff + 1 
    
    # Counting daily active user from each chort
    grouping = transaction_df.groupby(['CohortYear', 'CohortIndex'])
    # Counting number of unique customer Id's falling in each group of CohortMonth and CohortIndex
    cohort_data = grouping['Client Number'].apply(pd.Series.nunique)
    cohort_data = cohort_data.reset_index()
    # Assigning column names to the dataframe created above
    cohort_counts = cohort_data.pivot(index='CohortYear',
                                    columns ='CohortIndex',
                                    values = 'Client Number')

    cohort_sizes = cohort_counts.iloc[:,0]
    retention = cohort_counts.divide(cohort_sizes, axis=0)
    # Coverting the retention rate into percentage and Rounding off.
    retention.round(3)*100
    

    csfont = {'fontname':'Inter'}

    plt.figure(figsize=(10.8,8))
    plt.title('Car Insurance Policyholders: Customer Retention Matrix', fontsize = 16, fontweight= 600, **csfont)
    plt.ylabel('Cohort Year',**csfont,fontsize=12,fontweight=600)
    plt.xlabel('Cohort Index',**csfont,fontsize=12,fontweight=600)
    # Creating the heatmap
    ax = sns.heatmap(retention,annot=True,fmt='.0%')
    fig = ax.get_figure()
    fig.savefig("./apps/static/assets/images/cohort/heatmap-general.png")
    return

def actualCohort(all_details):

    transaction_df = pd.read_csv(all_details, encoding='latin1')
    transaction_df['idate'] =  pd.to_datetime(transaction_df['idate'],errors='coerce', format='%m/%d/%y')


    for col in transaction_df.columns:
        # Check if the column is of object type
        if transaction_df[col].dtypes == 'object':
            # Impute with the most frequent value
            transaction_df[col] = transaction_df[col].fillna(transaction_df[col].value_counts().index[0])

    # A function that will parse the date Time based cohort:  1 day of month
    def get_month(x): return dt.datetime(x.year, x.month, 1) 
    # Create transaction_date column based on month and store in TransactionMonth
    transaction_df['TransactionMonth'] = transaction_df['idate'].apply(get_month) 
    # Grouping by customer_id and select the InvoiceMonth value
    grouping = transaction_df.groupby('agcode1')['TransactionMonth'] 
    # Assigning a minimum InvoiceMonth value to the dataset
    transaction_df['CohortMonth'] = grouping.transform('min')

    transaction_df['TransactionYear'] = transaction_df['idate'].dt.year
    # Grouping by customer_id and select the InvoiceMonth value
    grouping = transaction_df.groupby('agcode1')['idate'] 
    # Assigning a minimum InvoiceMonth value to the dataset
    transaction_df['CohortYear'] = grouping.transform('min').dt.year

    def get_date_int(df, column):
        year = df[column].dt.year
        month = df[column].dt.month
        day = df[column].dt.day
        return year, month, day
    # Getting the integers for date parts from the `InvoiceDay` column
    transcation_year, transaction_month, _ = get_date_int(transaction_df, 'TransactionMonth')
    # Getting the integers for date parts from the `CohortDay` column
    cohort_year, cohort_month, _ = get_date_int(transaction_df, 'CohortMonth')

    #  Get the  difference in years
    years_diff = transcation_year - cohort_year
    # Calculate difference in months
    months_diff = transaction_month - cohort_month
    """ Extract the difference in months from all previous values
    "+1" in addeded at the end so that first month is marked as 1 instead of 0 for easier interpretation. 
    """
    transaction_df['CohortIndex'] = years_diff + 1 

    # Counting daily active user from each chort
    grouping = transaction_df.groupby(['CohortYear', 'CohortIndex'])
    # Counting number of unique customer Id's falling in each group of CohortMonth and CohortIndex
    cohort_data = grouping['agcode1'].apply(pd.Series.nunique)
    cohort_data = cohort_data.reset_index()
    # Assigning column names to the dataframe created above
    cohort_counts = cohort_data.pivot(index='CohortYear',
                                    columns ='CohortIndex',
                                    values = 'agcode1')
    
    cohort_sizes = cohort_counts.iloc[:,0]
    retention = cohort_counts.divide(cohort_sizes, axis=0)
    # Coverting the retention rate into percentage and Rounding off.
    retention.round(3)*100

    csfont = {'fontname':'Inter'}

    plt.figure(figsize=(10.8,8))
    plt.title('Car Insurance Policyholders: Customer Retention Matrix', fontsize = 16, fontweight= 600, **csfont)
    plt.ylabel('Cohort Year',**csfont,fontsize=12,fontweight=600)
    plt.xlabel('Cohort Index',**csfont,fontsize=12,fontweight=600)
    # Creating the heatmap
    ax = sns.heatmap(retention,annot=True,cmap="magma",fmt='.0%')
    fig = ax.get_figure()
    fig.savefig("./apps/static/assets/images/cohort/heatmap-general.png")
    return

def calc_Actual(path):

    transaction_df = pd.read_csv(path, encoding='latin1')
    transaction_df['idate'] =  pd.to_datetime(transaction_df['idate'],errors='coerce', format='%m/%d/%y')

    for col in transaction_df.columns:
    # Check if the column is of object type
        if transaction_df[col].dtypes == 'object':
            # Impute with the most frequent value
            transaction_df[col] = transaction_df[col].fillna(transaction_df[col].value_counts().index[0])
    def get_month(x): return dt.datetime(x.year, x.month, 1) 
    # Create transaction_date column based on month and store in TransactionMonth
    transaction_df['TransactionMonth'] = transaction_df['idate'].apply(get_month) 
    # Grouping by customer_id and select the InvoiceMonth value
    grouping = transaction_df.groupby('agcode1')['TransactionMonth'] 
    # Assigning a minimum InvoiceMonth value to the dataset
    transaction_df['CohortMonth'] = grouping.transform('min')

    transaction_df['TransactionYear'] = transaction_df['idate'].dt.year
    # Grouping by customer_id and select the InvoiceMonth value
    grouping = transaction_df.groupby('agcode1')['idate'] 
    # Assigning a minimum InvoiceMonth value to the dataset
    transaction_df['CohortYear'] = grouping.transform('min').dt.year

    def get_date_int(df, column):
        year = df[column].dt.year
        month = df[column].dt.month
        day = df[column].dt.day
        return year, month, day
    # Getting the integers for date parts from the `InvoiceDay` column
    transcation_year, transaction_month, _ = get_date_int(transaction_df, 'TransactionMonth')
    # Getting the integers for date parts from the `CohortDay` column
    cohort_year, cohort_month, _ = get_date_int(transaction_df, 'CohortMonth')

    #  Get the  difference in years
    years_diff = transcation_year - cohort_year
    # Calculate difference in months
    months_diff = transaction_month - cohort_month
    """ Extract the difference in months from all previous values
    "+1" in addeded at the end so that first month is marked as 1 instead of 0 for easier interpretation. 
    """
    transaction_df['CohortIndex'] = years_diff + 1 

    # Counting daily active user from each chort
    grouping = transaction_df.groupby(['CohortYear', 'CohortIndex'])
    # Counting number of unique customer Id's falling in each group of CohortMonth and CohortIndex
    cohort_data = grouping['agcode1'].apply(pd.Series.nunique)
    cohort_data = cohort_data.reset_index()
    # Assigning column names to the dataframe created above
    cohort_counts = cohort_data.pivot(index='CohortYear',
                                    columns ='CohortIndex',
                                    values = 'agcode1')
    
    cohort_sizes = cohort_counts.iloc[:,0]
    retention = cohort_counts.divide(cohort_sizes, axis=0)
    # Coverting the retention rate into percentage and Rounding off.
    retention.round(3)*100

    retained = retention.round(3)*100
    aveRetained = retained.mean().mean()
    aveRetained = round(aveRetained, 2)
    return aveRetained

def compreCohort(all_details):

    transaction_df = pd.read_csv(all_details, encoding='latin1')
    transaction_df = transaction_df.loc[transaction_df['pcategory'] == 'Comprehensive']
    transaction_df['idate'] =  pd.to_datetime(transaction_df['idate'],errors='coerce', format='%m/%d/%y')


    for col in transaction_df.columns:
        # Check if the column is of object type
        if transaction_df[col].dtypes == 'object':
            # Impute with the most frequent value
            transaction_df[col] = transaction_df[col].fillna(transaction_df[col].value_counts().index[0])

    # A function that will parse the date Time based cohort:  1 day of month
    def get_month(x): return dt.datetime(x.year, x.month, 1) 
    # Create transaction_date column based on month and store in TransactionMonth
    transaction_df['TransactionMonth'] = transaction_df['idate'].apply(get_month) 
    # Grouping by customer_id and select the InvoiceMonth value
    grouping = transaction_df.groupby('agcode1')['TransactionMonth'] 
    # Assigning a minimum InvoiceMonth value to the dataset
    transaction_df['CohortMonth'] = grouping.transform('min')

    transaction_df['TransactionYear'] = transaction_df['idate'].dt.year
    # Grouping by customer_id and select the InvoiceMonth value
    grouping = transaction_df.groupby('agcode1')['idate'] 
    # Assigning a minimum InvoiceMonth value to the dataset
    transaction_df['CohortYear'] = grouping.transform('min').dt.year

    def get_date_int(df, column):
        year = df[column].dt.year
        month = df[column].dt.month
        day = df[column].dt.day
        return year, month, day
    # Getting the integers for date parts from the `InvoiceDay` column
    transcation_year, transaction_month, _ = get_date_int(transaction_df, 'TransactionMonth')
    # Getting the integers for date parts from the `CohortDay` column
    cohort_year, cohort_month, _ = get_date_int(transaction_df, 'CohortMonth')

    #  Get the  difference in years
    years_diff = transcation_year - cohort_year
    # Calculate difference in months
    months_diff = transaction_month - cohort_month
    """ Extract the difference in months from all previous values
    "+1" in addeded at the end so that first month is marked as 1 instead of 0 for easier interpretation. 
    """
    transaction_df['CohortIndex'] = years_diff + 1 

    # Counting daily active user from each chort
    grouping = transaction_df.groupby(['CohortYear', 'CohortIndex'])
    # Counting number of unique customer Id's falling in each group of CohortMonth and CohortIndex
    cohort_data = grouping['agcode1'].apply(pd.Series.nunique)
    cohort_data = cohort_data.reset_index()
    # Assigning column names to the dataframe created above
    cohort_counts = cohort_data.pivot(index='CohortYear',
                                    columns ='CohortIndex',
                                    values = 'agcode1')
    
    cohort_sizes = cohort_counts.iloc[:,0]
    retention = cohort_counts.divide(cohort_sizes, axis=0)
    # Coverting the retention rate into percentage and Rounding off.
    retention.round(3)*100

    csfont = {'fontname':'Inter'}

    plt.figure(figsize=(10.8,8))
    plt.title('Customer Retention Matrix: Comprehensive Policy Category', fontsize = 16, fontweight= 600, **csfont)
    plt.ylabel('Cohort Year',**csfont,fontsize=12,fontweight=600)
    plt.xlabel('Cohort Index',**csfont,fontsize=12,fontweight=600)
    # Creating the heatmap
    ax = sns.heatmap(retention,annot=True,cmap="magma",fmt='.0%')
    fig = ax.get_figure()
    fig.savefig("./apps/static/assets/images/cohort/heatmap-comprehensive.png")
    return

def calc_Compre(path):

    transaction_df = pd.read_csv(path, encoding='latin1')
    transaction_df = transaction_df.loc[transaction_df['pcategory'] == 'Comprehensive']
    transaction_df['idate'] =  pd.to_datetime(transaction_df['idate'],errors='coerce', format='%m/%d/%y')

    for col in transaction_df.columns:
    # Check if the column is of object type
        if transaction_df[col].dtypes == 'object':
            # Impute with the most frequent value
            transaction_df[col] = transaction_df[col].fillna(transaction_df[col].value_counts().index[0])
    def get_month(x): return dt.datetime(x.year, x.month, 1) 
    # Create transaction_date column based on month and store in TransactionMonth
    transaction_df['TransactionMonth'] = transaction_df['idate'].apply(get_month) 
    # Grouping by customer_id and select the InvoiceMonth value
    grouping = transaction_df.groupby('agcode1')['TransactionMonth'] 
    # Assigning a minimum InvoiceMonth value to the dataset
    transaction_df['CohortMonth'] = grouping.transform('min')

    transaction_df['TransactionYear'] = transaction_df['idate'].dt.year
    # Grouping by customer_id and select the InvoiceMonth value
    grouping = transaction_df.groupby('agcode1')['idate'] 
    # Assigning a minimum InvoiceMonth value to the dataset
    transaction_df['CohortYear'] = grouping.transform('min').dt.year

    def get_date_int(df, column):
        year = df[column].dt.year
        month = df[column].dt.month
        day = df[column].dt.day
        return year, month, day
    # Getting the integers for date parts from the `InvoiceDay` column
    transcation_year, transaction_month, _ = get_date_int(transaction_df, 'TransactionMonth')
    # Getting the integers for date parts from the `CohortDay` column
    cohort_year, cohort_month, _ = get_date_int(transaction_df, 'CohortMonth')

    #  Get the  difference in years
    years_diff = transcation_year - cohort_year
    # Calculate difference in months
    months_diff = transaction_month - cohort_month
    """ Extract the difference in months from all previous values
    "+1" in addeded at the end so that first month is marked as 1 instead of 0 for easier interpretation. 
    """
    transaction_df['CohortIndex'] = years_diff + 1 

    # Counting daily active user from each chort
    grouping = transaction_df.groupby(['CohortYear', 'CohortIndex'])
    # Counting number of unique customer Id's falling in each group of CohortMonth and CohortIndex
    cohort_data = grouping['agcode1'].apply(pd.Series.nunique)
    cohort_data = cohort_data.reset_index()
    # Assigning column names to the dataframe created above
    cohort_counts = cohort_data.pivot(index='CohortYear',
                                    columns ='CohortIndex',
                                    values = 'agcode1')
    
    cohort_sizes = cohort_counts.iloc[:,0]
    retention = cohort_counts.divide(cohort_sizes, axis=0)
    # Coverting the retention rate into percentage and Rounding off.
    retention.round(3)*100

    retained = retention.round(3)*100
    aveRetained = retained.mean().mean()
    aveRetained = round(aveRetained, 2)
    return aveRetained


def ctplCohort(all_details):

    transaction_df = pd.read_csv(all_details, encoding='latin1')
    transaction_df = transaction_df.loc[transaction_df['pcategory'] == 'CTPL']
    transaction_df['idate'] =  pd.to_datetime(transaction_df['idate'],errors='coerce', format='%m/%d/%y')


    for col in transaction_df.columns:
        # Check if the column is of object type
        if transaction_df[col].dtypes == 'object':
            # Impute with the most frequent value
            transaction_df[col] = transaction_df[col].fillna(transaction_df[col].value_counts().index[0])

    # A function that will parse the date Time based cohort:  1 day of month
    def get_month(x): return dt.datetime(x.year, x.month, 1) 
    # Create transaction_date column based on month and store in TransactionMonth
    transaction_df['TransactionMonth'] = transaction_df['idate'].apply(get_month) 
    # Grouping by customer_id and select the InvoiceMonth value
    grouping = transaction_df.groupby('agcode1')['TransactionMonth'] 
    # Assigning a minimum InvoiceMonth value to the dataset
    transaction_df['CohortMonth'] = grouping.transform('min')

    transaction_df['TransactionYear'] = transaction_df['idate'].dt.year
    # Grouping by customer_id and select the InvoiceMonth value
    grouping = transaction_df.groupby('agcode1')['idate'] 
    # Assigning a minimum InvoiceMonth value to the dataset
    transaction_df['CohortYear'] = grouping.transform('min').dt.year

    def get_date_int(df, column):
        year = df[column].dt.year
        month = df[column].dt.month
        day = df[column].dt.day
        return year, month, day
    # Getting the integers for date parts from the `InvoiceDay` column
    transcation_year, transaction_month, _ = get_date_int(transaction_df, 'TransactionMonth')
    # Getting the integers for date parts from the `CohortDay` column
    cohort_year, cohort_month, _ = get_date_int(transaction_df, 'CohortMonth')

    #  Get the  difference in years
    years_diff = transcation_year - cohort_year
    # Calculate difference in months
    months_diff = transaction_month - cohort_month
    """ Extract the difference in months from all previous values
    "+1" in addeded at the end so that first month is marked as 1 instead of 0 for easier interpretation. 
    """
    transaction_df['CohortIndex'] = years_diff + 1 

    # Counting daily active user from each chort
    grouping = transaction_df.groupby(['CohortYear', 'CohortIndex'])
    # Counting number of unique customer Id's falling in each group of CohortMonth and CohortIndex
    cohort_data = grouping['agcode1'].apply(pd.Series.nunique)
    cohort_data = cohort_data.reset_index()
    # Assigning column names to the dataframe created above
    cohort_counts = cohort_data.pivot(index='CohortYear',
                                    columns ='CohortIndex',
                                    values = 'agcode1')
    
    cohort_sizes = cohort_counts.iloc[:,0]
    retention = cohort_counts.divide(cohort_sizes, axis=0)
    # Coverting the retention rate into percentage and Rounding off.
    retention.round(3)*100

    csfont = {'fontname':'Inter'}

    plt.figure(figsize=(10.8,8))
    plt.title('Customer Retention Matrix: Comprehensive Policy Category', fontsize = 16, fontweight= 600, **csfont)
    plt.ylabel('Cohort Year',**csfont,fontsize=12,fontweight=600)
    plt.xlabel('Cohort Index',**csfont,fontsize=12,fontweight=600)
    # Creating the heatmap
    ax = sns.heatmap(retention,annot=True,cmap="magma",fmt='.0%')
    fig = ax.get_figure()
    fig.savefig("./apps/static/assets/images/cohort/heatmap-ctpl.png")
    return

def calc_CTPL(path):

    transaction_df = pd.read_csv(path, encoding='latin1')
    transaction_df = transaction_df.loc[transaction_df['pcategory'] == 'CTPL']
    transaction_df['idate'] =  pd.to_datetime(transaction_df['idate'],errors='coerce', format='%m/%d/%y')

    for col in transaction_df.columns:
    # Check if the column is of object type
        if transaction_df[col].dtypes == 'object':
            # Impute with the most frequent value
            transaction_df[col] = transaction_df[col].fillna(transaction_df[col].value_counts().index[0])
    def get_month(x): return dt.datetime(x.year, x.month, 1) 
    # Create transaction_date column based on month and store in TransactionMonth
    transaction_df['TransactionMonth'] = transaction_df['idate'].apply(get_month) 
    # Grouping by customer_id and select the InvoiceMonth value
    grouping = transaction_df.groupby('agcode1')['TransactionMonth'] 
    # Assigning a minimum InvoiceMonth value to the dataset
    transaction_df['CohortMonth'] = grouping.transform('min')

    transaction_df['TransactionYear'] = transaction_df['idate'].dt.year
    # Grouping by customer_id and select the InvoiceMonth value
    grouping = transaction_df.groupby('agcode1')['idate'] 
    # Assigning a minimum InvoiceMonth value to the dataset
    transaction_df['CohortYear'] = grouping.transform('min').dt.year

    def get_date_int(df, column):
        year = df[column].dt.year
        month = df[column].dt.month
        day = df[column].dt.day
        return year, month, day
    # Getting the integers for date parts from the `InvoiceDay` column
    transcation_year, transaction_month, _ = get_date_int(transaction_df, 'TransactionMonth')
    # Getting the integers for date parts from the `CohortDay` column
    cohort_year, cohort_month, _ = get_date_int(transaction_df, 'CohortMonth')

    #  Get the  difference in years
    years_diff = transcation_year - cohort_year
    # Calculate difference in months
    months_diff = transaction_month - cohort_month
    """ Extract the difference in months from all previous values
    "+1" in addeded at the end so that first month is marked as 1 instead of 0 for easier interpretation. 
    """
    transaction_df['CohortIndex'] = years_diff + 1 

    # Counting daily active user from each chort
    grouping = transaction_df.groupby(['CohortYear', 'CohortIndex'])
    # Counting number of unique customer Id's falling in each group of CohortMonth and CohortIndex
    cohort_data = grouping['agcode1'].apply(pd.Series.nunique)
    cohort_data = cohort_data.reset_index()
    # Assigning column names to the dataframe created above
    cohort_counts = cohort_data.pivot(index='CohortYear',
                                    columns ='CohortIndex',
                                    values = 'agcode1')
    
    cohort_sizes = cohort_counts.iloc[:,0]
    retention = cohort_counts.divide(cohort_sizes, axis=0)
    # Coverting the retention rate into percentage and Rounding off.
    retention.round(3)*100

    retained = retention.round(3)*100
    aveRetained = retained.mean().mean()
    aveRetained = round(aveRetained, 2)
    return aveRetained

def basicCohort(all_details):

    transaction_df = pd.read_csv(all_details, encoding='latin1')
    transaction_df = transaction_df.loc[transaction_df['ptype'] == 'Basic']
    transaction_df['idate'] =  pd.to_datetime(transaction_df['idate'],errors='coerce', format='%m/%d/%y')


    for col in transaction_df.columns:
        # Check if the column is of object type
        if transaction_df[col].dtypes == 'object':
            # Impute with the most frequent value
            transaction_df[col] = transaction_df[col].fillna(transaction_df[col].value_counts().index[0])

    # A function that will parse the date Time based cohort:  1 day of month
    def get_month(x): return dt.datetime(x.year, x.month, 1) 
    # Create transaction_date column based on month and store in TransactionMonth
    transaction_df['TransactionMonth'] = transaction_df['idate'].apply(get_month) 
    # Grouping by customer_id and select the InvoiceMonth value
    grouping = transaction_df.groupby('agcode1')['TransactionMonth'] 
    # Assigning a minimum InvoiceMonth value to the dataset
    transaction_df['CohortMonth'] = grouping.transform('min')

    transaction_df['TransactionYear'] = transaction_df['idate'].dt.year
    # Grouping by customer_id and select the InvoiceMonth value
    grouping = transaction_df.groupby('agcode1')['idate'] 
    # Assigning a minimum InvoiceMonth value to the dataset
    transaction_df['CohortYear'] = grouping.transform('min').dt.year

    def get_date_int(df, column):
        year = df[column].dt.year
        month = df[column].dt.month
        day = df[column].dt.day
        return year, month, day
    # Getting the integers for date parts from the `InvoiceDay` column
    transcation_year, transaction_month, _ = get_date_int(transaction_df, 'TransactionMonth')
    # Getting the integers for date parts from the `CohortDay` column
    cohort_year, cohort_month, _ = get_date_int(transaction_df, 'CohortMonth')

    #  Get the  difference in years
    years_diff = transcation_year - cohort_year
    # Calculate difference in months
    months_diff = transaction_month - cohort_month
    """ Extract the difference in months from all previous values
    "+1" in addeded at the end so that first month is marked as 1 instead of 0 for easier interpretation. 
    """
    transaction_df['CohortIndex'] = years_diff + 1 

    # Counting daily active user from each chort
    grouping = transaction_df.groupby(['CohortYear', 'CohortIndex'])
    # Counting number of unique customer Id's falling in each group of CohortMonth and CohortIndex
    cohort_data = grouping['agcode1'].apply(pd.Series.nunique)
    cohort_data = cohort_data.reset_index()
    # Assigning column names to the dataframe created above
    cohort_counts = cohort_data.pivot(index='CohortYear',
                                    columns ='CohortIndex',
                                    values = 'agcode1')
    
    cohort_sizes = cohort_counts.iloc[:,0]
    retention = cohort_counts.divide(cohort_sizes, axis=0)
    # Coverting the retention rate into percentage and Rounding off.
    retention.round(3)*100

    csfont = {'fontname':'Inter'}

    plt.figure(figsize=(10.8,8))
    plt.title('Customer Retention Matrix: Comprehensive Policy Category', fontsize = 16, fontweight= 600, **csfont)
    plt.ylabel('Cohort Year',**csfont,fontsize=12,fontweight=600)
    plt.xlabel('Cohort Index',**csfont,fontsize=12,fontweight=600)
    # Creating the heatmap
    ax = sns.heatmap(retention,annot=True,cmap="magma",fmt='.0%')
    fig = ax.get_figure()
    fig.savefig("./apps/static/assets/images/cohort/heatmap-basic.png")
    return

def calc_Basic(path):

    transaction_df = pd.read_csv(path, encoding='latin1')
    transaction_df = transaction_df.loc[transaction_df['ptype'] == 'Basic']
    transaction_df['idate'] =  pd.to_datetime(transaction_df['idate'],errors='coerce', format='%m/%d/%y')

    for col in transaction_df.columns:
    # Check if the column is of object type
        if transaction_df[col].dtypes == 'object':
            # Impute with the most frequent value
            transaction_df[col] = transaction_df[col].fillna(transaction_df[col].value_counts().index[0])
    def get_month(x): return dt.datetime(x.year, x.month, 1) 
    # Create transaction_date column based on month and store in TransactionMonth
    transaction_df['TransactionMonth'] = transaction_df['idate'].apply(get_month) 
    # Grouping by customer_id and select the InvoiceMonth value
    grouping = transaction_df.groupby('agcode1')['TransactionMonth'] 
    # Assigning a minimum InvoiceMonth value to the dataset
    transaction_df['CohortMonth'] = grouping.transform('min')

    transaction_df['TransactionYear'] = transaction_df['idate'].dt.year
    # Grouping by customer_id and select the InvoiceMonth value
    grouping = transaction_df.groupby('agcode1')['idate'] 
    # Assigning a minimum InvoiceMonth value to the dataset
    transaction_df['CohortYear'] = grouping.transform('min').dt.year

    def get_date_int(df, column):
        year = df[column].dt.year
        month = df[column].dt.month
        day = df[column].dt.day
        return year, month, day
    # Getting the integers for date parts from the `InvoiceDay` column
    transcation_year, transaction_month, _ = get_date_int(transaction_df, 'TransactionMonth')
    # Getting the integers for date parts from the `CohortDay` column
    cohort_year, cohort_month, _ = get_date_int(transaction_df, 'CohortMonth')

    #  Get the  difference in years
    years_diff = transcation_year - cohort_year
    # Calculate difference in months
    months_diff = transaction_month - cohort_month
    """ Extract the difference in months from all previous values
    "+1" in addeded at the end so that first month is marked as 1 instead of 0 for easier interpretation. 
    """
    transaction_df['CohortIndex'] = years_diff + 1 

    # Counting daily active user from each chort
    grouping = transaction_df.groupby(['CohortYear', 'CohortIndex'])
    # Counting number of unique customer Id's falling in each group of CohortMonth and CohortIndex
    cohort_data = grouping['agcode1'].apply(pd.Series.nunique)
    cohort_data = cohort_data.reset_index()
    # Assigning column names to the dataframe created above
    cohort_counts = cohort_data.pivot(index='CohortYear',
                                    columns ='CohortIndex',
                                    values = 'agcode1')
    
    cohort_sizes = cohort_counts.iloc[:,0]
    retention = cohort_counts.divide(cohort_sizes, axis=0)
    # Coverting the retention rate into percentage and Rounding off.
    retention.round(3)*100

    retained = retention.round(3)*100
    aveRetained = retained.mean().mean()
    aveRetained = round(aveRetained, 2)
    return aveRetained

def premiumCohort(all_details):

    transaction_df = pd.read_csv(all_details, encoding='latin1')
    transaction_df = transaction_df.loc[transaction_df['ptype'] == 'Premium']
    transaction_df['idate'] =  pd.to_datetime(transaction_df['idate'],errors='coerce', format='%m/%d/%y')


    for col in transaction_df.columns:
        # Check if the column is of object type
        if transaction_df[col].dtypes == 'object':
            # Impute with the most frequent value
            transaction_df[col] = transaction_df[col].fillna(transaction_df[col].value_counts().index[0])

    # A function that will parse the date Time based cohort:  1 day of month
    def get_month(x): return dt.datetime(x.year, x.month, 1) 
    # Create transaction_date column based on month and store in TransactionMonth
    transaction_df['TransactionMonth'] = transaction_df['idate'].apply(get_month) 
    # Grouping by customer_id and select the InvoiceMonth value
    grouping = transaction_df.groupby('agcode1')['TransactionMonth'] 
    # Assigning a minimum InvoiceMonth value to the dataset
    transaction_df['CohortMonth'] = grouping.transform('min')

    transaction_df['TransactionYear'] = transaction_df['idate'].dt.year
    # Grouping by customer_id and select the InvoiceMonth value
    grouping = transaction_df.groupby('agcode1')['idate'] 
    # Assigning a minimum InvoiceMonth value to the dataset
    transaction_df['CohortYear'] = grouping.transform('min').dt.year

    def get_date_int(df, column):
        year = df[column].dt.year
        month = df[column].dt.month
        day = df[column].dt.day
        return year, month, day
    # Getting the integers for date parts from the `InvoiceDay` column
    transcation_year, transaction_month, _ = get_date_int(transaction_df, 'TransactionMonth')
    # Getting the integers for date parts from the `CohortDay` column
    cohort_year, cohort_month, _ = get_date_int(transaction_df, 'CohortMonth')

    #  Get the  difference in years
    years_diff = transcation_year - cohort_year
    # Calculate difference in months
    months_diff = transaction_month - cohort_month
    """ Extract the difference in months from all previous values
    "+1" in addeded at the end so that first month is marked as 1 instead of 0 for easier interpretation. 
    """
    transaction_df['CohortIndex'] = years_diff + 1 

    # Counting daily active user from each chort
    grouping = transaction_df.groupby(['CohortYear', 'CohortIndex'])
    # Counting number of unique customer Id's falling in each group of CohortMonth and CohortIndex
    cohort_data = grouping['agcode1'].apply(pd.Series.nunique)
    cohort_data = cohort_data.reset_index()
    # Assigning column names to the dataframe created above
    cohort_counts = cohort_data.pivot(index='CohortYear',
                                    columns ='CohortIndex',
                                    values = 'agcode1')
    
    cohort_sizes = cohort_counts.iloc[:,0]
    retention = cohort_counts.divide(cohort_sizes, axis=0)
    # Coverting the retention rate into percentage and Rounding off.
    retention.round(3)*100

    csfont = {'fontname':'Inter'}

    plt.figure(figsize=(10.8,8))
    plt.title('Customer Retention Matrix: Comprehensive Policy Category', fontsize = 16, fontweight= 600, **csfont)
    plt.ylabel('Cohort Year',**csfont,fontsize=12,fontweight=600)
    plt.xlabel('Cohort Index',**csfont,fontsize=12,fontweight=600)
    # Creating the heatmap
    ax = sns.heatmap(retention,annot=True,cmap="magma",fmt='.0%')
    fig = ax.get_figure()
    fig.savefig("./apps/static/assets/images/cohort/heatmap-premium.png")
    return

def calc_Premium(path):

    transaction_df = pd.read_csv(path, encoding='latin1')
    transaction_df = transaction_df.loc[transaction_df['ptype'] == 'Premium']
    transaction_df['idate'] =  pd.to_datetime(transaction_df['idate'],errors='coerce', format='%m/%d/%y')

    for col in transaction_df.columns:
    # Check if the column is of object type
        if transaction_df[col].dtypes == 'object':
            # Impute with the most frequent value
            transaction_df[col] = transaction_df[col].fillna(transaction_df[col].value_counts().index[0])
    def get_month(x): return dt.datetime(x.year, x.month, 1) 
    # Create transaction_date column based on month and store in TransactionMonth
    transaction_df['TransactionMonth'] = transaction_df['idate'].apply(get_month) 
    # Grouping by customer_id and select the InvoiceMonth value
    grouping = transaction_df.groupby('agcode1')['TransactionMonth'] 
    # Assigning a minimum InvoiceMonth value to the dataset
    transaction_df['CohortMonth'] = grouping.transform('min')

    transaction_df['TransactionYear'] = transaction_df['idate'].dt.year
    # Grouping by customer_id and select the InvoiceMonth value
    grouping = transaction_df.groupby('agcode1')['idate'] 
    # Assigning a minimum InvoiceMonth value to the dataset
    transaction_df['CohortYear'] = grouping.transform('min').dt.year

    def get_date_int(df, column):
        year = df[column].dt.year
        month = df[column].dt.month
        day = df[column].dt.day
        return year, month, day
    # Getting the integers for date parts from the `InvoiceDay` column
    transcation_year, transaction_month, _ = get_date_int(transaction_df, 'TransactionMonth')
    # Getting the integers for date parts from the `CohortDay` column
    cohort_year, cohort_month, _ = get_date_int(transaction_df, 'CohortMonth')

    #  Get the  difference in years
    years_diff = transcation_year - cohort_year
    # Calculate difference in months
    months_diff = transaction_month - cohort_month
    """ Extract the difference in months from all previous values
    "+1" in addeded at the end so that first month is marked as 1 instead of 0 for easier interpretation. 
    """
    transaction_df['CohortIndex'] = years_diff + 1 

    # Counting daily active user from each chort
    grouping = transaction_df.groupby(['CohortYear', 'CohortIndex'])
    # Counting number of unique customer Id's falling in each group of CohortMonth and CohortIndex
    cohort_data = grouping['agcode1'].apply(pd.Series.nunique)
    cohort_data = cohort_data.reset_index()
    # Assigning column names to the dataframe created above
    cohort_counts = cohort_data.pivot(index='CohortYear',
                                    columns ='CohortIndex',
                                    values = 'agcode1')
    
    cohort_sizes = cohort_counts.iloc[:,0]
    retention = cohort_counts.divide(cohort_sizes, axis=0)
    # Coverting the retention rate into percentage and Rounding off.
    retention.round(3)*100

    retained = retention.round(3)*100
    aveRetained = retained.mean().mean()
    aveRetained = round(aveRetained, 2)
    return aveRetained