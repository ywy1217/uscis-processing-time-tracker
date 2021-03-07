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
const fs = require('fs');
var stringify = require('csv-stringify');
const fastcsv = require('fast-csv');

var URL = 'https://egov.uscis.gov/casestatus/mycasestatus.do?appReceiptNum=RECEIPT_NUM';
var today = new Date();

var failedFile = './raw_data/updater_raw_2021-11-25_failed.csv';
var saveFile = './raw_data/updater_raw_'+today.toISOString().substring(0,19).replace(/:/g,"")+'_append_fail.csv';
var errFile = './raw_data/updater_raw_'+today.toISOString().substring(0,19).replace(/:/g,"")+'_failed.csv';
var totalRetrieved = 0;
var grandTotal = 0;
var startTime;

fs.writeFileSync(saveFile, 'receiptID,title,text\n');
fs.writeFileSync(errFile, 'receiptID,errmsg\n');
// load receiptNumbers from a failed table
var receiptNumbers = [];
fs.createReadStream(failedFile)
  .pipe(fastcsv.parse({ headers: true }))
  .on('error', error => console.error(error))
  .on('data', function(row){
    // console.log(row);
    receiptNumbers.push(row['receiptID']);
    // console.log(receiptNumbers);
  })
  .on('end', (rowCount) => {
    console.log(`Parsed ${rowCount} receipt numbers!`);
    grandTotal = receiptNumbers.length;
    startTime = Date.now();
    console.log('Start crawling: '+grandTotal);
    async.eachLimit(receiptNumbers, 1, retrieveReceiptNumber, function (err) {
      if (err) {
          console.error(err);
      }
      console.log('DONE');
      if (totalRetrieved < grandTotal) {
          console.log('Some retrievals failed!');
      } else {
          fs.unlinkSync(errFile);
      }

    });
  });


function retrieveReceiptNumber(receiptNumber, callback) {
  request({
      url: URL.replace('RECEIPT_NUM', receiptNumber),
      rejectUnauthorized: false,
      // proxy: 'http://localhost:8888',
      // tunnel: false
    },
    function (err, resp, body) {
      if (err) {
        console.error(err);
      }

      if (typeof body === "string") {
        var $ = cheerio.load(body);
        var title = $('.appointment-sec').find('.text-center').find('h1').text();
        var description = $('.appointment-sec').find('.text-center').find('p').text();
        var violation = $('label[for=accessviolation]').text();
        var formErrMsg = $('#formErrorMessages').text().trim();
      } else {
        // print erroneous non-string body that fails cheerio.load
        console.log(String(body).errorColor);
      }
            
      setTimeout(() => {  console.log("Wait 0.5s!"); }, 300);

      if (typeof body != "string" || title.length == 0) {
        if (typeof body === "string") {
          if (violation.length > 0) {
            console.log('access violation'.errorColor);
          }
  
          if (formErrMsg.length > 0) {
            var errMsg = formErrMsg;
            var shortErrMsg = $('#formErrorMessages').find('h4').text();
          } else {
            var errMsg = err;
            var shortErrMsg = err;
          }
        } else {
          var errMsg = err;
          var shortErrMsg = "undefined Body";
        }

        console.error(`Failed: ${receiptNumber}, Err: ${shortErrMsg}`.warn);

        var row = [[receiptNumber, errMsg]];

        stringify(row, function (err, output) {
          if (err) {
            console.error(err);
          }
          fs.appendFile(errFile, output, function (err) {
            if (err) {
              console.error(err);
            }
            callback();
          });
        })
      } else {
        var row = [
          [receiptNumber, title, description]
        ];

        stringify(row, function (err, output) {
          if (err) {
            console.error(err);
          }
          fs.appendFile(saveFile, output, function (err) {
            if (err) {
              console.error(err);
            }
            totalRetrieved = totalRetrieved + 1;
            console.log('Retrieved: '+receiptNumber+','+ totalRetrieved +'/'+ grandTotal+
            '. Time Lapsed ('+Math.floor((Date.now() - startTime) / 60000)+'min) Time Remaining ('+
            +Math.floor((Date.now() - startTime) * (grandTotal-totalRetrieved)/totalRetrieved / 60000)+'min)');
            callback();
          });
        });
      }
    });
}
