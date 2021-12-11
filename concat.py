# Only for raw data concatenating without sort

f_out = open('./raw_data/out.csv', 'w')
f_out.write('receiptID,title,text\n')

files = ['./raw_data/crawl_raw_2021-06-18.csv', './raw_data/crawl_raw_2021-06-19T184555_append_fail.csv']

for filename in files:
    with open(filename, 'r') as f:
        next(f)
        for line in f:
            f_out.write(line)

f_out.close()
