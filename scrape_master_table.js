var cheerio = require('cheerio');
var request = require('request');
var async = require('async');
var fs = require('fs');
var stringify = require('csv-stringify');

var URL = 'https://egov.uscis.gov/casestatus/mycasestatus.do?appReceiptNum=RECEIPT_NUM';
var PREFIX = 'MSC';
var START_NUMBER = 2190301567;
var END_NUMBER = 2190442006;
var saveFile = 'master_table_raw.csv';
var totalRetrieved = 0;

var receiptNumbers = [];
for (var i = START_NUMBER; i < END_NUMBER; i++) {
  receiptNumbers.push(PREFIX + i);
}
fs.writeFileSync(saveFile, 'receiptID,title,text\n');
var grandTotal = receiptNumbers.length;
console.log('Start crawling: '+grandTotal);
const startTime = Date.now();

function retrieveReceiptNumber(receiptNumber, callback) {
  request({
      url: URL.replace('RECEIPT_NUM', receiptNumber),
      rejectUnauthorized: false,
      proxy: 'http://localhost:8888',
      tunnel: false
    },
    function (err, resp, body) {
      if (err) {
        console.error(err);
      }

      var $ = cheerio.load(body);
      var title = $('.appointment-sec').find('.text-center').find('h1').text();
      var description = $('.appointment-sec').find('.text-center').find('p').text();
      var form_num = description.match(/Form \w-\d\d\d/);
      var violation = $('label[for=accessviolation]').text();
      setTimeout(() => {  console.log("Wait 0.5s!"); }, 500);

      if (title.length == 0) {
        if (violation.length > 0) {
          console.log('access violation');
        }
        callback();
        
      } else if (form_num != "Form I-485") {
          console.log(receiptNumber + ' is ' + form_num + ', bypass');
		  callback();
      }
      else {
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
            console.log(receiptNumber + ' written');
            console.log('Retrieved: '+ totalRetrieved +'/'+ grandTotal+'. Time Lapsed ('+Math.floor((Date.now() - startTime) / 60000)+'min)');
            callback();
          });
        });

      }
    });
}

async.eachLimit(receiptNumbers, 7, retrieveReceiptNumber, function (err) {
    if (err) {
        console.error(err);
    }
    console.log('DONE');
});

