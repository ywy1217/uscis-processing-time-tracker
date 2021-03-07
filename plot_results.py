# this file serves as a template of plotting results of the snapshot of the status of all cases based on the crawl or master table
import pandas
import dataProcessing as dp
import matplotlib.pyplot as plt

ID_scope = (2190232878, 2190442006)  # master table was crawled within this range
colors = ['green', 'yellow', 'gray']
result_path = dp.get_latest_file(folder="./processed_data", table_prefix="crawl_table")
print('Generating plots for table:', result_path)
data = pandas.read_csv(result_path)
num_bins = 50

cat1 = data[data['status'] == 'Fingerprint']['receiptID']
cat1_num = cat1.apply(dp.strip_prefix)
cat2 = data[data['status'] == 'Processing']['receiptID']
cat2_num = cat2.apply(dp.strip_prefix)
cat3 = data[data['status'] == 'Received']['receiptID']
cat3_num = cat3.apply(dp.strip_prefix)
cat_num = [cat1_num, cat2_num, cat3_num]

fig, ax = plt.subplots()
n, bins, patches = ax.hist(cat1_num, num_bins, range=[ID_scope[0], ID_scope[1]],
                           label='Fingerprint Updated', facecolor='green', align='mid')
n_aug = [x for pair in zip(n, n) for x in pair]
bins_aug = [x for pair in zip(bins[0:-1], bins[1:]) for x in pair]
ax.plot(bins_aug, n_aug, color='black')

n, bins, patches = ax.hist(cat2_num, num_bins, range=[ID_scope[0], ID_scope[1]],
                           label='Processing', facecolor='yellow', align='mid')
n_aug = [x for pair in zip(n, n) for x in pair]
bins_aug = [x for pair in zip(bins[0:-1], bins[1:]) for x in pair]
ax.plot(bins_aug, n_aug)

n, bins, patches = ax.hist(cat3_num, num_bins, range=[ID_scope[0], ID_scope[1]],
                           label='Case Received', facecolor='gray', align='mid')
n_aug = [x for pair in zip(n, n) for x in pair]
bins_aug = [x for pair in zip(bins[0:-1], bins[1:]) for x in pair]
ax.plot(bins_aug, n_aug)

# Draw case numbers or interest
plt.axvline(2190392085)
plt.axvline(2190420000)

ax.set_xlabel('Receipt Number')
ax.set_ylabel('Count')
ax.set_title('Histogram of Fingerprint Cases')
plt.legend(loc='upper center')

# Stacked Hist plots
fig1, ax1 = plt.subplots()
ax1.hist(cat_num, num_bins, range=[ID_scope[0], ID_scope[1]],
         label=['Fingerprint Updated', 'Processing', 'Case Received'],
         color=colors, stacked=True)
plt.axvline(2190392085)
plt.axvline(2190420000)
ax1.set_xlabel('Receipt Number')
ax1.set_ylabel('Count')
ax1.set_title('Histogram of Fingerprint Cases')
plt.legend(loc='upper center')

plt.show()

