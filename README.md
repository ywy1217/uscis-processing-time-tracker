# Track uscis processing time

## Disclaimer: read LICENSE and the following disclaimer before use
DO NOT use the software for commercial purpose.
DO NOT abuse the software (including but not limited to querying the data from any website at a very high frequency and data rate). Your IP may be blocked by doing that.
The user shall be responsible for any consequences of using this software.


## Start a master table (a manual process at the moment)
You will need to first use [scrape_master_table](./scrape_master_table.js) to scape an inital dataset, where you specify the receipt id range. Keep in mind that you you need modify the range in [dataProcessing](./dataProcessing.py) accordingly for post-processing.
Use [process_raw_updater_table](./process_raw_updater_table.py) and [gen_master_table](./gen_master_table.py) to generate the master table.

## Regularly scape data and generate reports
[scrape_updater_table](./scrape_updater_table.js) now does all the heavy-lifting work including, parsing the raw data, updating master table, generating tracker table (subset excluding closed cases) for future data crawling, and reporting the statistics of status change and processing time with the dataset in master table.

Sometimes, scrape_updater_table.js might not be able to finish scaping the entire tracker list (due to internet issue or power outage, or technical defects in the code). In that case, use [scrape_updater_failed_list](./scrape_updater_failed_list.js) and then [concat](./concat.py) the raw data. After consolidating one updater_table, make sure its filename ranks first in descending order if there are other updater_table files in the directory, before you call [run_all](./run_all).

### Acknowledgement
Scraper javacript is adapted from [Linan Qiu's repo](http://linanqiu.github.io/2016/05/24/OPT-I-765-Processing-Time/).
