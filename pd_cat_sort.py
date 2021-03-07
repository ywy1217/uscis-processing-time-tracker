import pandas as pd

if __name__ == "__main__":
    # files = ['./processed_data/tracker_table_2021-04-03_GenAT2021-04-04T122915.csv',
    #          './processed_data/tracker_table_2021-04-08_GenAT2021-04-09T224606.csv']

    # files = ['./processed_data/master_table_2021-03-07_UpdatedBY_crawl_table_2021-04-03_GenAT_2021-04-03T122832.csv',
    #          './processed_data/master_table_2021-04-08_GenAT2021-04-09T223831.csv']

    files = ['./raw_data/crawl_raw_2021-11-25.csv',
             './raw_data/updater_raw_2021-11-26T033312_append_fail.csv']
    df_list = [pd.read_csv(filename) for filename in files]

    df_cat = pd.concat(df_list)

    print(len(df_cat))
    df_cat_sort = df_cat.sort_values('receiptID')

    df_cat_sort.to_csv('./raw_data/updater_raw_2021-11-26.csv', index=False)
