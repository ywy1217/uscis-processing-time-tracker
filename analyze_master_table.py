# plot stacked histogram of the snapshot of the status
# Mark the tracked case in the plot

import pandas as pd
import dataProcessing as dp
import matplotlib.pyplot as plt
import re
import reportsTools as rt
import numpy as np
import statsTools as st
import uncertainties.unumpy as unp
from matplotlib.patches import Polygon
from statistics import median

sourceFile = dp.get_latest_file(folder="./processed_data", table_prefix="master_table")
print('--------------------------------------')
print('Analyzing master table:', sourceFile)
original_date = re.search('master_table_(\d\d\d\d-\d\d-\d\d)', sourceFile).group(1)
update_date = re.search('updater_table_(\d\d\d\d-\d\d-\d\d)', sourceFile).group(1)
master_table = pd.read_csv(sourceFile, converters={'receiptID': str, 'status': str,
                                                   'receipt_Date': str, 'fingerprint_Date': str,
                                                   'RFE_Date': str, 'interview_Date': str,
                                                   'rejection_Date': str, 'approval_Date': str,
                                                   'ESTIMATE_receipt_Date': str})

# Page0: print status change statistics
reports = master_table.groupby('status')['receiptID'].count().sort_values(ascending=False)
reports = reports.append(
    pd.Series([reports.pop('Rejected')], index=pd.Index(['Rejected'], name='status'), name='receiptID'))
reports_str = str(reports).split('\n')
reports_str[0] = '<Master Table Snapshot Statistics>'
reports_str = '\n'.join(reports_str[:-1])
print('------------- By Status --------------')
print(reports_str)
print('--------------------------------------')

num_bins = 50

fig_overview, (ax0_ov, ax1_ov) = plt.subplots(nrows=1, ncols=2)
fig_overview.set_size_inches(12, 6)
ax0_ov.axis('off')
ax0_ov.text(1, -0.2,
            'one bin=' + str(int((dp.ID_scope[1] - dp.ID_scope[0]) / num_bins)) + ' cases\nNote only ~1/3 are I-485',
            style='oblique', ha='right', va='bottom', ma='right', fontsize=8)
ax0_ov.text(.5, .9, '<Master Table (%s) Snapshot @ %s>' % (original_date, update_date),
            style='oblique', ha='center', va='center', color='red')
text_h = 0.7
for i in range(0, len(reports)):
    ax0_ov.text(.2, text_h, reports.keys()[i], style='oblique', ha='left', va='center', ma='left')
    ax0_ov.text(.8, text_h, reports[i], style='oblique', ha='right', va='center', ma='right')
    text_h = text_h - 0.08
ax0_ov.text(.2, text_h, 'Total', style='oblique', ha='left', va='center', ma='left', color='blue')
ax0_ov.text(.8, text_h, reports.sum(), style='oblique', ha='right', va='center', ma='right', color='blue')
total_minus_reject = reports.sum() - reports['Rejected']

# Page1: Stacked Histogram by Status
keys = list(dp.status_priority_map.keys())
keys.remove('Rejected')
cat_num = [master_table[master_table['status'] == key]['receiptID'].apply(dp.strip_prefix)
           for key in keys]
ax1_ov.hist(cat_num, num_bins, range=[dp.ID_scope[0], dp.ID_scope[1]],
            label=['Case Received', 'Processing', 'Fingerprint Updated', 'RFE', 'Interview', 'Approved'],
            color=list(rt.color_map.values()), stacked=True)
ax1_ov.axvline(2190392085, color='red', linewidth=1, linestyle=':')
ax1_ov.tick_params(axis='x', labelrotation=45)
ax1_ov.set_xlabel('Receipt Number')
ax1_ov.set_ylabel('Count')
ax1_ov.set_title('Stacked Histogram')
plt.legend(loc='best')
fig_overview.tight_layout()

# Page k(k>=2): Histogram by /date or status/ | milestone date scatter plot
keys = ['Fingerprint', 'RFE', 'Interview', 'Approved']
assert (np.prod([key in list(dp.status_priority_map.keys()) for key in keys]))
today_num = dp.date2num(dp.now_to_str('D'))
days_lapsed_tracked_case = {milestone: dp.date2num(dp.now_to_str('D'), dp.track_case[dp.status_dateCol_map[milestone]])
                            for milestone in ['Received', 'Fingerprint', 'RFE', 'Interview', 'Approved']}
for idx, key in enumerate(keys):

    track_date = dp.track_case[dp.status_dateCol_map[key]]
    track_num = dp.date2num(track_date)
    print('Reporting', key)

    # get case numbers by each status
    if key == 'Fingerprint':
        # if current status is fingerprint / interview / approved, take it as fingerprint recorded (rare cases may not have fingerprint date actually or missed in scraping)
        # if current status is RFE, include it only if the fingerprint date is on record
        cat_num_per_key = master_table[[(status in ['Fingerprint', 'Interview', 'Approved'])
                                        or ((status == 'RFE') and fingerdate != '') for status, fingerdate in
                                        zip(master_table['status'], master_table['fingerprint_Date'])]][
            'receiptID'].apply(dp.strip_prefix)
    else:
        cat_num_per_key = master_table[[status in [keys[kk] for kk in range(idx, len(keys))]
                                        for status in master_table['status']]]['receiptID'].apply(dp.strip_prefix)
    # cat_num[key] = cat_num_per_key
    # print(cat_num_per_key)
    print('> Generating Date vs Receipt ID')
    # --Milestone dates by receipt Number--
    fig_cat, ax_cat = plt.subplots(nrows=1, ncols=2)
    fig_cat.suptitle(key, fontsize='x-large', fontweight='bold')
    fig_cat.set_size_inches(12, 6)
    ax_cat[0].hist(cat_num_per_key, num_bins, range=[dp.ID_scope[0], dp.ID_scope[1]],
                   color=rt.color_map[key])
    ax_cat[0].set_xlabel('Receipt Number')
    ax_cat[0].set_ylabel('Count')
    ax_cat[0].tick_params(axis='x', labelrotation=45)
    ax_cat[0].axvline(2190392085, color='red', linewidth=1, linestyle=':')
    ax_cat[0].set_title('%d/%d Done, (excludes rejected)' % (len(cat_num_per_key), total_minus_reject))

    # --scatter plot: receiptID - milestone date--
    x, y = dp.get_x_y_from_master_table(master_table, keys=dp.status_dateCol_map[key])
    ax_cat[1].scatter(x, y, s=1, facecolors=rt.color_map[key], edgecolors='none', linewidths=0.5)

    xnew = np.arange(0, dp.ID_scope[1] - dp.ID_scope[0], 100)
    ynew, (lcb, ucb), (lpb, upb), fit_coefs = st.curve_fit_package(xnew, x - dp.ID_scope[0], y)
    xnew_plot = [kk + dp.ID_scope[0] for kk in xnew]

    ax_cat[1].plot(xnew_plot, ynew, c='black',
                   label='y=({:.3e}) x + ({:.3e})'.format(*(unp.nominal_values([fit_coefs[0], fit_coefs[1]]))))
    # uncertainty lines (95% confidence)
    poly = Polygon(list(zip(xnew_plot, lcb)) + list(zip(xnew_plot[::-1], ucb[::-1]))
                   , closed=True, fc='orange', ec='orange', alpha=0.2)
    ax_cat[1].add_patch(poly)
    # prediction band (95% confidence)
    poly = Polygon(list(zip(xnew_plot, lpb)) + list(zip(xnew_plot[::-1], upb[::-1])),
                   closed=True, fc='c', ec='c', alpha=0.1)
    ax_cat[1].add_patch(poly)

    ax_cat[1].set_xlabel('Receipt Number')
    ax_cat[1].set_ylabel('Days after 2020-10-01')
    ax_cat[1].tick_params(axis='x', labelrotation=45)
    ax_cat[1].axvline(2190392085, color='red', linewidth=1, linestyle=':')
    ax_cat[1].axhline(today_num, color='magenta', linewidth=1, linestyle=':')
    ax_cat[1].text(dp.ID_scope[0], today_num, 'TODAY', color='magenta', style='oblique', ha='right', va='bottom')
    if track_num is not None:
        ax_cat[1].axhline(track_num, color='magenta', linewidth=1, linestyle='-')
        ax_cat[1].text(dp.ID_scope[0], track_num, 'DONE', color='magenta', style='oblique', ha='right', va='bottom')
    plt.legend(loc='best')
    fig_cat.tight_layout()

    # milestone_date i -> milestone_date j: days histogram | scatter plot
    pre_milestones = ['receipt_Date', 'ESTIMATE_receipt_Date'] + \
                     [dp.status_dateCol_map[tempKey] for tempKey in keys[0:idx]]
    pre_status_keys = ['Received', 'Received'] + keys[0:idx]
    print('> Generating processing time from previous milestones', pre_milestones)
    for idx_i, (pre_status, pre_date) in enumerate(zip(pre_status_keys, pre_milestones)):
        print('> >', pre_date, '-->', key)
        x, y = dp.get_x_y_from_master_table(master_table, keys=[pre_date, dp.status_dateCol_map[key]])
        if len(x) < 5:
            print('Sample Size %d is too small for this scenario!' % len(x))
        else:
            xnew = np.arange(x.min(), x.max())
            ynew, (lcb, ucb), (lpb, upb), fit_coefs = st.curve_fit_package(xnew, x, y)
            # compute the processing time in [days]
            days_i_j = y - x
            mid_days = median(days_i_j)

            fig_i_2_j, ax_i_2_j = plt.subplots(nrows=1, ncols=2)
            fig_i_2_j.suptitle('%s --> %s' % (pre_date, key), fontsize=12, fontweight='bold')
            fig_i_2_j.set_size_inches(12, 6)
            # plot results - hist
            N, bins, patches = ax_i_2_j[0].hist(days_i_j, num_bins, color=rt.color_map[key])
            ax_i_2_j[0].set_xlabel('Processing Time [days]')
            ax_i_2_j[0].set_ylabel('Count')
            if days_lapsed_tracked_case[pre_status] is not None:
                ax_i_2_j[0].axvline(days_lapsed_tracked_case[pre_status], color='red', linewidth=1, linestyle=':')
                ax_i_2_j[0].text(days_lapsed_tracked_case[pre_status], N.max(), '%d days lapsed'
                                 % (days_lapsed_tracked_case[pre_status]), style='oblique',
                                 ha='center', va='bottom', ma='center', color='red')

                if track_num is not None:
                    days_lapsed_from_pre_to_cur = days_lapsed_tracked_case[pre_status] - days_lapsed_tracked_case[key]
                    ax_i_2_j[0].axvline(days_lapsed_from_pre_to_cur, color='red', linewidth=1, linestyle='-')
                    ax_i_2_j[0].text(days_lapsed_from_pre_to_cur, N.max()/2, '%d days done' % days_lapsed_from_pre_to_cur,
                                     style='oblique', ha='center', va='bottom', ma='center', color='red')

            ax_i_2_j[0].set_title('%d valid cases, med %d days' % (len(days_i_j), mid_days))

            # plot results - scatter plot and fit curve
            ax_i_2_j[1].scatter(x, y, s=1, facecolors=rt.color_map[key], edgecolors='none', linewidths=0.5)
            ax_i_2_j[1].plot(xnew, ynew, c='black', label='y=({:.3e}) x + ({:.3e})'
                             .format(*(unp.nominal_values([fit_coefs[0], fit_coefs[1]]))))
            # uncertainty lines (95% confidence)
            poly = Polygon(list(zip(xnew, lcb)) + list(zip(xnew[::-1], ucb[::-1]))
                           , closed=True, fc='orange', ec='orange', alpha=0.2)
            ax_i_2_j[1].add_patch(poly)
            # prediction band (95% confidence)
            poly = Polygon(list(zip(xnew, lpb)) + list(zip(xnew[::-1], upb[::-1])),
                           closed=True, fc='c', ec='c', alpha=0.1)
            ax_i_2_j[1].add_patch(poly)
            ax_i_2_j[1].set_xlabel(pre_date + '[days after 2020-10-01]')
            ax_i_2_j[1].set_ylabel(key + ' [days after 2020-10-01]')
            if dp.track_case[dp.status_dateCol_map[pre_status]] is not None:
                ax_i_2_j[1].axvline(dp.date2num(dp.track_case[dp.status_dateCol_map[pre_status]]),
                                    color='red', linewidth=1, linestyle=':')
            ax_i_2_j[1].axhline(today_num, color='magenta', linewidth=1, linestyle=':')
            ax_i_2_j[1].text(min(x), today_num, 'TODAY',
                             color='magenta', style='oblique', ha='right', va='bottom', ma='right')
            if track_num is not None:
                ax_i_2_j[1].axhline(track_num, color='magenta', linewidth=1, linestyle='-')
                ax_i_2_j[1].text(min(x), track_num, 'DONE',
                                 color='magenta', style='oblique', ha='right', va='bottom', ma='right')

            plt.legend(loc='best')
            fig_i_2_j.tight_layout()

    print('Done')
# plt.show()

saveFile = './reports/Snapshot_Master_Table_' + original_date + '_to_' + update_date + '_GenAT' \
               + dp.now_to_str() + '.pdf'

if __name__ == '__main__':
    # save results under <reports> folder
    rt.save_pdf(saveFile)
