# Generate the tracker table
import pandas
import numpy
import re
import dataProcessing as dp

sourceFile = dp.get_latest_file(folder="./processed_data", table_prefix="updater_table", skip=0)

print('Processing updater table:', sourceFile)
crawl_date = re.search('\d\d\d\d-\d\d-\d\d', sourceFile).group(0)
saveFile = './processed_data/tracker_table_' + crawl_date + '_GenAT' \
           + dp.now_to_str() + '.csv'

raw_data = pandas.read_csv(sourceFile)
print('--------------------------------------')
print(raw_data.groupby('status')['receiptID'].count())
print('--------------------------------------')
tracker_table = raw_data[[x and y for x, y in zip(raw_data['status'] != 'Rejected', raw_data['status'] != 'Approved')]]
del raw_data
tracker_table.drop(['eventDate'], axis='columns', inplace=True)
print('Generated a tracker table on <' + saveFile + '>')
tracker_table.to_csv(saveFile, index=False)

if __name__ != '__main__':  # if NOT running as the main entry point
    # remove the old Tracker file
    print('Deleting old tracker files:')
    print('--------------------------------------')
    delete_file = dp.get_latest_file(folder="./processed_data", table_prefix="tracker_table", skip=1)
    while delete_file is not None:
        dp.delete_the_file(delete_file)
        delete_file = dp.get_latest_file(folder="./processed_data", table_prefix="tracker_table", skip=1)
