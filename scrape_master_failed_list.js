var colors = require('colors');
colors.setTheme({
  info: 'bgGreen',
  help: 'cyan',
  warn: 'yellow',
  success: 'bgBlue',
  errorColor: 'red'
});
var cheerio = require('cheerio');
var request = require('request');
var async = require('async');
var fs = require('fs');
var stringify = require('csv-stringify');
const fastcsv = require('fast-csv');

var URL = 'https://egov.uscis.gov/casestatus/mycasestatus.do?appReceiptNum=RECEIPT_NUM';
var today = new Date();

var failedFile = './processed_data/sanity_check_complementary_master_table.csv';
var saveFile = './raw_data/crawl_raw_'+today.toISOString().substring(0,10)+'.csv';
var errFile = './raw_data/crawl_raw_'+today.toISOString().substring(0,10)+'_failed.csv';
var totalRetrieved = 0;
var grandTotal = 0;
var startTime;

fs.writeFileSync(saveFile, 'receiptID,title,text\n');
fs.writeFileSync(errFile, 'receiptID,errmsg\n');
// load receiptNumbers from a failed table
var receiptNumbers = [];
fs.createReadStream(failedFile)
  .pipe(fastcsv.parse({ headers: true }))
  .on('error', error => console.error(error.errorColor))
  .on('data', function(row){
    // console.log(row);
    receiptNumbers.push(row['receiptID']);
    // console.log(receiptNumbers);
  })
  .on('end', (rowCount) => {
    console.log(`Parsed ${rowCount} receipt numbers!`.info);
    grandTotal = receiptNumbers.length;
    startTime = Date.now();
    console.log('Start crawling: '+grandTotal);
    async.eachLimit(receiptNumbers, 1, retrieveReceiptNumber, function (err) {
        if (err) {
            console.error(err.errorColor);
        }
        console.log('DONE'.success);
    });
  });


function retrieveReceiptNumber(receiptNumber, callback) {
  request({
      url: URL.replace('RECEIPT_NUM', receiptNumber),
      rejectUnauthorized: false,
      // Uncomment the following two lines to use proxy
      // remember to have another console running proxy via 'scrapoxy start conf.json -d'
      // You will need to have your own 'conf.json'. Refer to https://scrapoxy.readthedocs.io/en/master/quick_start/index.html
    //   proxy: 'http://localhost:8888',
    //   tunnel: false
    },
    function (err, resp, body) {
      if (err) {
        console.error(err.errorColor);
      }

      if (typeof body === "string") {
        var $ = cheerio.load(body);
      } else {
        // print erroneous non-string body that fails cheerio.load
        console.log(String(body).errorColor);
      }
      var title = $('.appointment-sec').find('.text-center').find('h1').text();
      var description = $('.appointment-sec').find('.text-center').find('p').text();
      var form_num = description.match(/Form \w-\d\d\d/);
      var violation = $('label[for=accessviolation]').text();
      var formErrMsg = $('#formErrorMessages').text().trim();
      setTimeout(() => {  console.log("Wait 0.5s!"); }, 500);

      if (title.length == 0) {
        if (violation.length > 0) {
          console.log('access violation'.errorColor);
        }

        if (formErrMsg.length > 0) {
            var errMsg = formErrMsg;
            var shortErrMsg = $('#formErrorMessages').find('h4').text();
        } else {
            var errMsg = err;
            var shortErrMsg = err;
            var row = [[receiptNumber, errMsg]];

            stringify(row, function (err, output) {
            if (err) {
                console.error(err.errorColor);
            }
            fs.appendFile(errFile, output, function (err) {
                if (err) {
                console.error(err.errorColor);
                }
            });
            })
        }
        console.error(`Failed: ${receiptNumber}, Err: ${shortErrMsg}`.warn);
        callback();

      } else if (form_num != "Form I-485") {
        console.log(receiptNumber + ' is ' + form_num + ', bypass');
		    callback();
      } else {
        var row = [
          [receiptNumber, title, description]
        ];

        stringify(row, function (err, output) {
          if (err) {
            console.error(err.errorColor);
          }
          fs.appendFile(saveFile, output, function (err) {
            if (err) {
              console.error(err.errorColor);
            }
            totalRetrieved = totalRetrieved + 1;
            console.log('Retrieved: '+ receiptNumber+','+ totalRetrieved +'/'+ grandTotal+'. Time Lapsed ('+Math.floor((Date.now() - startTime) / 60000)+'min)');
            callback();
          });
        });

      }
    });
}
