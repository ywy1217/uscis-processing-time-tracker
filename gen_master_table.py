# Build the master table upon a Crawl table
import pandas
import dataProcessing as dp
import datetime
from scipy import interpolate
import matplotlib.pyplot as plt


sourceFile = './processed_data/crawl_expand_master_table_2021-04-08_GenAT2021-04-09T223129.csv'
crawl_date = dp.re.search('\d\d\d\d-\d\d-\d\d', sourceFile).group(0)
saveFile = './processed_data/master_table_'+crawl_date+'_GenAT'\
           + str(dp.numpy.datetime64(datetime.datetime.now(), 's')).replace(':', '')+'.csv'

master_table = pandas.read_csv(sourceFile)

# Find milestone dates from event date in crawl_table
master_table['receipt_Date'] = master_table.apply(dp.parse_date, axis=1, args=['Received'])
master_table['fingerprint_Date'] = master_table.apply(dp.parse_date, axis=1, args=['Fingerprint'])
master_table['RFE_Date'] = master_table.apply(dp.parse_date, axis=1, args=['RFE'])
master_table['interview_Date'] = master_table.apply(dp.parse_date, axis=1, args=['Interview'])
master_table['rejection_Date'] = master_table.apply(dp.parse_date, axis=1, args=['Rejected'])
master_table['approval_Date'] = master_table.apply(dp.parse_date, axis=1, args=['Approved'])

# Interpolate/Extrapolate receipt dates based available information
# master_table['receipt_Date'] = master_table.apply()
# note that receiptID is in ascending order chronologically

cases_receipt_date_recorded = master_table[master_table['receipt_Date'] != ""]
cases_chronological_index = cases_receipt_date_recorded.index
receipt_dates_recorded = cases_receipt_date_recorded.apply(dp.date2num, axis=1)
# print(cases_chronological_index)
# interp_f = interpolate.interp1d(cases_chronological_index, receipt_dates_recorded, fill_value="extrapolate")
# fit_p1 = dp.numpy.poly1d(dp.numpy.polyfit(cases_chronological_index, receipt_dates_recorded, 1))
fit_pn = dp.numpy.poly1d(dp.numpy.polyfit(cases_chronological_index, receipt_dates_recorded, 2))
# xnew = master_table.index
# ynew = fit_p1(xnew)
# ynew_n = fit_pn(xnew)
# plt.plot(cases_chronological_index, receipt_dates_recorded, 'o', xnew, ynew, '-', xnew, ynew_n, '--')
# plt.show()

master_table['row_index'] = master_table.index
master_table['ESTIMATE_receipt_Date'] = master_table.apply(dp.estimate_date, axis=1, args=[fit_pn, 'receipt_Date'])

master_table.drop(['eventDate', 'row_index'], axis='columns', inplace=True)
print(master_table)
master_table.to_csv(saveFile, index=False)
