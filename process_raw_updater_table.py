import pandas
import dataProcessing as dp


def process_raw_updater_table(folder="./raw_data", table_prefix="updater_raw", skip=0):
    sourceFile = dp.get_latest_file(folder=folder, table_prefix=table_prefix, skip=skip)
    # sourceFile = './raw_data/master_table_raw_2021-04-08.csv'
    if sourceFile is not None:
        raw_data = pandas.read_csv(sourceFile)
        print('Processing raw data:', sourceFile)
        crawl_date = dp.re.search('\d\d\d\d-\d\d-\d\d', sourceFile).group(0)
        outputFile = './processed_data/' + table_prefix.split('_')[0] + '_table_' + crawl_date + '_GenAT' \
                     + dp.now_to_str() + '.csv'
        compressedFile = './raw_data/' + table_prefix.split('_')[0] + '_compressed_' + crawl_date + '_GenAT' \
                         + dp.now_to_str() + '.csv'

        print('--------------------------------------')
        print(raw_data.groupby('title').count()['receiptID'])
        print('--------------------------------------')
        raw_data['status'] = raw_data.apply(dp.categorize_status, axis=1)
        raw_data['eventDate'] = raw_data.apply(dp.extract_date, axis=1)
        # Compress raw data by reducing the text to Event Date

        # raw_data.drop(['title', 'text'], axis='columns', inplace=True)
        print('Results are saved:', outputFile)
        raw_data.to_csv(outputFile, columns=['receiptID', 'status', 'eventDate'], index=False)

        # Compress raw data by reducing the text to Event Date
        print('Raw data are compressed:', compressedFile)
        raw_data.to_csv(compressedFile, columns=['receiptID', 'title', 'eventDate'], index=False)

    else:
        print('Cannot find any file in \'%s\' with prefix \'%s\'' % (folder, table_prefix))
        raise FileNotFoundError(
            'Cannot find more than %d file(s) in \'%s\' with prefix \'%s\'' % (skip, folder, table_prefix))


if __name__ == "__main__":
    for loop_skip in range(0, 100):
        print('--------------------------------------')
        print('Processing File {}: '.format(loop_skip + 1))
        try:
            process_raw_updater_table(table_prefix='master_table', skip=loop_skip)
        except FileNotFoundError:
            break

else:
    process_raw_updater_table()
    # clean up files
    print('Deleting raw data file:')
    print('--------------------------------------')
    delete_file = dp.get_latest_file(folder="./raw_data", table_prefix="updater_raw", skip=0)
    dp.delete_the_file(delete_file)

# test
# row = {'text': 'As of January 22, 2021, fingerprints relating to your Form I-485, '
#                'Application to Register Permanent Residence or Adjust Status, Receipt '
#                'Number MSC2190232878, have been applied to your case.  If you move, go '
#                'to www.uscis.gov/addresschange  to give us your new mailing address.'}
# row = {'text': 'On March 1, 2021, we sent a request for initial evidence for your Form'
#                ' I-485, Application to Register Permanent Residence or Adjust Status, '
#                'Receipt Number MSC2190232884.  The request for evidence explains what we '
#                'need from you.  We will not take action on your case until we receive the '
#                'evidence or the deadline to submit it expires. Please follow the instructions '
#                'in the request for evidence.  If you do not receive your request for evidence'
#                ' by March 16, 2021, please go to www.uscis.gov/e-request  to request a copy of'
#                ' the notice.  If you move, go to www.uscis.gov/addresschange  to give us your '
#                'new mailing address.'}
# print(dp.extract_date(row))
