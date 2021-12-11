import pandas as pd

if __name__ == "__main__":

    files = ['./raw_data/updater_raw_2021-12-04.csv',
             './raw_data/updater_raw_2021-12-05T190930_append_fail.csv']
    df_list = [pd.read_csv(filename) for filename in files]

    df_cat = pd.concat(df_list)

    print(len(df_cat))
    df_cat_sort = df_cat.sort_values('receiptID')

    df_cat_sort.to_csv('./raw_data/updater_raw_2021-11-26.csv', index=False)
