# This file differentiates two crawl tables to understand the statistics of status change between the two snapshots
import glob
import pandas as pd
import re
import dataProcessing as dp
import matplotlib.pyplot as plt

folder = "./processed_data"
file_to_skip = 0

# load data
updater_file_list = glob.glob(folder + "/updater_table*.csv")
updater_file_list.sort(reverse=True)
print('--------------------------------------\n--------------------------------------\n'
      'Here are the files you can choose from:\n--------------------------------------')
[print(file) for file in updater_file_list]
print('--------------------------------------')
if file_to_skip > 0:
    print('Skipping', file_to_skip, 'file')
new_table_csv = updater_file_list[0 + file_to_skip]
old_table_csv = updater_file_list[1 + file_to_skip]
updater_date_new = re.search('\d\d\d\d-\d\d-\d\d', new_table_csv).group(0)
updater_date_old = re.search('\d\d\d\d-\d\d-\d\d', old_table_csv).group(0)
print('The following files are being used for diff:\n--------------------------------------')
print('new table:', new_table_csv)
print('old table:', old_table_csv)
print('--------------------------------------')
new_table = pd.read_csv(new_table_csv)
old_table = pd.read_csv(old_table_csv)

# print status of each file on console
print('-----------------Old Table---------------------')
print('Total length:', len(old_table))
print('--------------------------------------')
print(old_table.groupby('status')['receiptID'].count())
print('-----------------New Table---------------------')
print('Total length:', len(new_table))
print('--------------------------------------')
print(new_table.groupby('status')['receiptID'].count())
print('-----------------Diff Table---------------------')
diff_table = pd.merge(old_table, new_table, how='right', on='receiptID', suffixes=("_pre", "_new"))
diff_table = diff_table[diff_table['status_pre'] != diff_table['status_new']]
print(diff_table)
print('--------------------------------------')

# print status change statistics
reports = diff_table.groupby('status_new')['receiptID'].count().sort_values(ascending=False)
reports_str = str(reports).split('\n')
reports_str[0] = '<Status Change Statistics>'
reports_str = '\n'.join(reports_str[:-1])
print(reports_str)
print('--------------------------------------')

num_bins = 50
colors = ['green', 'yellow', 'gray']
fig, ax = plt.subplots(nrows=2, ncols=2)
fig.set_size_inches(12, 6)
ax = [x for pair in ax.tolist() for x in pair]
ax[0].axis('off')
ax[0].text(1, -0.5,
           'one bin=' + str(int((dp.ID_scope[1] - dp.ID_scope[0]) / num_bins)) + ' cases\nNote only ~1/3 are I-485',
           style='oblique', ha='right', va='bottom', ma='right', fontsize=8)
ax[0].text(.5, .9, '<Status Change Statistics: ' + updater_date_old + '==>' + updater_date_new + '>',
           style='oblique', ha='center', va='center', color='red')
text_h = 0.7
for i in range(0, len(reports)):
    ax[0].text(.2, text_h, reports.keys()[i], style='oblique', ha='left', va='center', ma='left')
    ax[0].text(.8, text_h, reports[i], style='oblique', ha='right', va='center', ma='right')
    text_h = text_h - 0.15
ax[0].text(.2, text_h, 'Total', style='oblique', ha='left', va='center', ma='left', color='blue')
ax[0].text(.8, text_h, reports.sum(), style='oblique', ha='right', va='center', ma='right', color='blue')

# plot results - only look at the histograms of the top 3 tiers of change
for i in range(0, 3):
    status = reports.keys()[i]
    stats = diff_table[diff_table['status_new'] == status]['receiptID'].apply(dp.strip_prefix)
    ax[i + 1].hist(stats, num_bins, range=[dp.ID_scope[0], dp.ID_scope[1]],
                   color=colors[i])
    ax[i + 1].axvline(2190392085, color='red', linewidth=1, linestyle=':')
    # ax[i + 1].axvline(2190420000, color='red', linewidth=1, linestyle=':')
    ax[i + 1].tick_params(axis='x', labelrotation=45)
    ax[i + 1].set_xlabel('Receipt Number')
    ax[i + 1].set_ylabel('Count')
    ax[i + 1].set_title(status)
fig.tight_layout()
# plt.show()

saveFile = './reports/Status_Change_' + updater_date_old + '_VS_' + updater_date_new + '_GenAT' \
           + dp.now_to_str() + '.csv'

if __name__ == '__main__':
    # save results under <reports> folder
    # diff_table.to_csv(saveFile, index=False)
    fig.savefig('./reports/Status_Change_' + updater_date_old + '_VS_' + updater_date_new + '_GenAT' \
                + dp.now_to_str() + '.png')
