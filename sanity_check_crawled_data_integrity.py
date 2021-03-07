# generate ID list within a given range against a master table, for rerunning scraper.js, making sure the master
# table didn't miss any I-485 cases

import pandas as pd
import dataProcessing as dp

ID_scope = (2190232878, 2190442006)
master_table_file = dp.get_latest_file(folder="./processed_data", table_prefix="master_table")
master_table = pd.read_csv(master_table_file, sep=',', converters={'receiptID': str, 'status': str,
                                                                   'receipt_Date': str, 'fingerprint_Date': str,
                                                                   'RFE_Date': str, 'interview_Date': str,
                                                                   'rejection_Date': str, 'approval_Date': str,
                                                                   'ESTIMATE_receipt_Date': str})

existing_list = master_table['receiptID']
print(existing_list)
full_list = ['MSC' + str(x) for x in range(ID_scope[0], ID_scope[1] + 1)]
print(len(full_list))
print(len(full_list) - len(existing_list))
diff_list = list(set(full_list) - set(existing_list))
diff_list.sort()
print(type(diff_list))
print(len(diff_list), ':', diff_list[0], diff_list[-1])
sanity_check_df = pd.Series(diff_list, name='receiptID')
saveFile = "./processed_data/sanity_check_complementary_master_table.csv"
sanity_check_df.to_csv(saveFile, index=False)
