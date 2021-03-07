import re
import numpy
import pandas
import os
import glob
import datetime as dt

ID_scope = (2190190000, 2190599500)
date_pattern = re.compile(' (\w+ [0-9]+, \d\d\d\d),')
status_priority_map = {'Received': 1, 'Processing': 2, 'Fingerprint': 3,
                       'RFE': 4, 'Interview': 5, 'Rejected': 6, 'Approved': 6}
status_dateCol_map = {'Received': 'receipt_Date', 'Processing': None, 'Fingerprint': 'fingerprint_Date',
                      'RFE': 'RFE_Date', 'Interview': 'interview_Date', 'Rejected': 'rejection_Date',
                      'Approved': 'approval_Date'}
# This is a fake case
track_case = {'receiptID': 2190390000, # MSC
              'receipt_Date': '2020-10-01',
              'fingerprint_Date': '2021-01-01',
              'RFE_Date': '2021-05-01',
              'status': 'RFE',
              'lastUpdate': '2021-05-01'
              }


def categorize_status(row):
    if 'Case Was Received' in row['title']:
        return 'Received'  # Track receive date
    if 'Rejected' in row['title'] or 'Case Was Denied' in row['title'] or \
            'Withdraw' in row['title'] or 'Closed' in row['title']:
        return 'Rejected'  # Closed cases but not approved
    if 'Case Was Approved' in row['title'] or 'Card Was Delivered' in row['title'] \
            or 'Card Was Mailed' in row['title'] or 'Card Was Picked Up' in row['title'] \
            or 'Case Approval Was Certified' in row['title'] or 'New Card Is Being Produced' in row['title']:
        return 'Approved'
    if 'Case Was Updated To Show Fingerprints Were Taken' in row['title'] or \
            'Fingerprint and Biometrics Appointment Was Scheduled' in row['title']:
        return 'Fingerprint'  # Track biometric appointment date
    if 'Case is Ready to Be Scheduled for An Interview' in row['title'] or \
            'Interview Was Scheduled' in row['title'] or 'Interview Was Rescheduled' in row['title'] \
            or 'Interview Was Completed And My Case Must Be Reviewed' in row['title']:
        return 'Interview'  # Track interview scheduling date
    if 'Request for Additional Evidence Was Sent' in row['title'] or \
            'Request for Initial Evidence Was Sent' in row['title']:
        return 'RFE'  # Track RFE date
    return 'Processing'  # Not a milestone update


def extract_date(row):
    m = date_pattern.search(row['text'])
    try:
        extracted_date = numpy.datetime64(pandas.Timestamp(m.group(1)), 'D')
    except AttributeError:
        extracted_date = ''
    return extracted_date


def strip_prefix(row, prefix='MSC'):
    # print(row)
    id_value = row.split(prefix, 1)
    return int(id_value[1])


def parse_date(row, status_keyword=None):
    if row['status'] == status_keyword:
        return row['eventDate']
    return ''


# use row index to estimate dates based on fit_function fitted on row_index - dates
def estimate_date(row, fit_function=None, date_keyword=None):
    if row[date_keyword] != '':
        return row[date_keyword]
    elif fit_function is None:
        return row[date_keyword]
    else:
        # print(row['row_index'])
        # print(fit_function(row['row_index']))
        return num2date(fit_function(row['row_index']))


def date2num(row, ref_date=numpy.datetime64('2020-10-01'), date_key='receipt_Date'):
    if row is None or ref_date is None:
        return None
    ref_date = numpy.datetime64(ref_date)
    if type(row) is pandas.core.series.Series:
        date_delta = numpy.datetime64(row[date_key]) - ref_date
    elif type(row) is str:
        date_delta = numpy.datetime64(row) - ref_date
    else:
        date_delta = None
    return date_delta.astype(int)


def num2date(num, ref_date=numpy.datetime64('2020-10-01')):
    # print(num)
    # print(type(num))
    int_num = int(numpy.ceil(num))
    return ref_date + numpy.timedelta64(int_num, 'D')


def get_latest_file(folder="./", table_prefix="", skip=0):
    # os.chdir(folder)
    # print(table_prefix + "*.csv")
    file_list = glob.glob(folder + '/' + table_prefix + "*.csv")
    file_list.sort(reverse=True)
    # [print(file) for file in file_list]
    if len(file_list) < skip + 1:
        return None
    else:
        return file_list[0 + skip]


def update_master_table(row):
    flag = 0  # no change
    old_status = row['status_master']
    # print('Master Status:', row['status_master'], '| Updater Status:', row['status_updater'],
    # ' (Type:', type(row['status_updater']))
    # only update master table when status is changed
    # After left-join, there will be 'nan' cells in 'status_updater' for cases that do not exist in updater table. Skip them
    if str(row['status_updater']) != 'nan' and row['status_master'] != row['status_updater']:
        flag = 1
        # print('Master Status:', row['status_master'], '| Updater Status:', row['status_updater'],
        # ' (Type:', type(row['status_updater']))
        # Make sure new status doesn't overwrite higher priority status
        if status_priority_map[row['status_updater']] > status_priority_map[row['status_master']]:
            row['status_master'] = row['status_updater']

        # if row['status_updater'] != 'Processing':
        # print('Update', status_dateCol_map[row['status_updater']],
        #       row[status_dateCol_map[row['status_updater']]], 'to', row['eventDate'])
        # Make sure milestone date doesn't get overridden if it already exists
        if row['status_updater'] != 'Processing' and str(row[status_dateCol_map[row['status_updater']]]) == '':
            # print('Updated!')
            row[status_dateCol_map[row['status_updater']]] = row['eventDate']

    return flag, old_status


def now_to_str(str_fmt_key='s'):
    if str_fmt_key == 'D':
        return str(numpy.datetime64(dt.datetime.now(), 'D')).replace(':', '')
    else:
        return str(numpy.datetime64(dt.datetime.now(), 's')).replace(':', '')


def get_x_y_from_master_table(master_table, keys=None):
    x = None
    y = None
    if type(keys) is str:
        key1 = 'receiptID'
        key2 = keys
    else:
        assert (type(keys) is list and (len(keys) == 1 or len(keys) == 2))
        if len(keys) == 1:
            key1 = 'receiptID'
            key2 = keys[0]
        else:
            key1 = keys[0]
            key2 = keys[1]

    assert (key2 in ['fingerprint_Date', 'RFE_Date', 'interview_Date', 'approval_Date'])

    if key1 == 'receiptID':
        temp_table = master_table[master_table[key2] != '']
        x = temp_table[key1].apply(strip_prefix)
        y = temp_table[key2].apply(date2num)

    else:
        assert (key1 in ['receipt_Date', 'ESTIMATE_receipt_Date', 'fingerprint_Date', 'RFE_Date',
                         'interview_Date'])

        temp_table = master_table[
            ['' not in [date1, date2] for date1, date2 in zip(master_table[key1], master_table[key2])]]
        x = temp_table[key1].apply(date2num)
        y = temp_table[key2].apply(date2num)

    return x, y


def delete_the_file(filepath):
    if filepath is not None:
        print('\'%s\'' % filepath)
        if os.path.exists(filepath):
            os.unlink(filepath)
            print('DELETED')
        else:
            raise FileNotFoundError('Does Not Exist')
