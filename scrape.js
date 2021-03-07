var cheerio = require('cheerio');
var request = require('request');
var async = require('async');
var fs = require('fs');
var stringify = require('csv-stringify');

var URL = 'https://egov.uscis.gov/casestatus/mycasestatus.do?appReceiptNum=RECEIPT_NUM';
var PREFIX = 'MSC';
var START_NUMBER = 2190232908;
var END_NUMBER = 2190232910;
// var END_NUMBER = 2190442006;
var saveFile = 'test_data.csv'

var receiptNumbers = [];
for (var i = START_NUMBER; i < END_NUMBER; i++) {
  receiptNumbers.push(PREFIX + i);
}
fs.writeFileSync(saveFile, 'receiptID,title,text\n');
console.log('Start crawling: '+receiptNumbers.length);

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

      if (title.length == 0) {
        if (violation.length > 0) {
          console.log('access violation');
        }

        callback();
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
            console.log(receiptNumber + ' written');
            callback();
          });
        });
      }
    });
}

async.eachLimit(receiptNumbers, 50, retrieveReceiptNumber, function (err) {
    if (err) {
        console.error(err);
    }
    console.log('DONE');
});
