# This file updates master table using the latest processed updater table
# Make it compatible with some weird cases and legacy cases:
# --for example MSC2190314553 (first approved and then fingerprint updated)
# --Update the relevant milestone dates but don't change status
# Make sure milestone date doesn't get overridden if it already exists
# Make sure higher priority status prevails

import pandas as pd
import dataProcessing as dp
import re

folder = "./processed_data"
updater_table_file = dp.get_latest_file(folder=folder, table_prefix="updater_table", skip=0)
master_table_file = dp.get_latest_file(folder=folder, table_prefix="master_table")
crawl_date = re.search('\d\d\d\d-\d\d-\d\d', updater_table_file).group(0)
master_date = re.search('\d\d\d\d-\d\d-\d\d', master_table_file).group(0)

print('Loading the master table:', master_table_file)
orig_master_table = pd.read_csv(master_table_file, sep=',', converters={'receiptID': str, 'status': str,
                                                                        'receipt_Date': str, 'fingerprint_Date': str,
                                                                        'RFE_Date': str, 'interview_Date': str,
                                                                        'rejection_Date': str, 'approval_Date': str,
                                                                        'ESTIMATE_receipt_Date': str})
print('Loading the updater table:', updater_table_file)
updater_table = pd.read_csv(updater_table_file)

new_master_table = pd.merge(orig_master_table, updater_table, how='left', on='receiptID', suffixes=("_master", "_updater"))
del orig_master_table
del updater_table
# dp.update_master_table is applied on the 'actual' new_master_table, not its copy. Thus the effect is in place,
# even 'a' is not used anywhere. 'a' is for debug purpose only.
a = new_master_table.apply(dp.update_master_table, axis=1)
# new_master_table['flag'] = [pair[0] for pair in a]
# new_master_table['old_status'] = [pair[1] for pair in a]
new_master_table = new_master_table.rename(columns={'status_master': 'status'})
new_master_table.drop(['status_updater', 'eventDate'], axis='columns', inplace=True)

# save results
saveFile = folder + '/master_table_' + master_date + '_UpdatedBY_updater_table_' + \
           crawl_date + '_GenAT_' + dp.now_to_str() + '.csv'
new_master_table.to_csv(saveFile, index=False)
print('Results are saved:', saveFile)
