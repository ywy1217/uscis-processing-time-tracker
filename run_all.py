# A hacky way of running all the standalone scripts

import process_raw_updater_table
import generate_tracker_table
import update_master_table
import diff_two_updater_tables as dtt
import analyze_master_table as amt
import dataProcessing as dp
import reportsTools as rt


dtt.diff_table.to_csv(dtt.saveFile, index=False)
saveFile = './reports/Combined_Updates_' + amt.update_date + '_From_' + amt.original_date + '_GenAT' \
               + dp.now_to_str() + '.pdf'
rt.save_pdf(saveFile)
