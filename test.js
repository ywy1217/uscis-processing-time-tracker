var colors = require('colors');
colors.setTheme({
  info: 'bgGreen',
  help: 'cyan',
  warn: 'yellow',
  success: 'bgBlue',
  errorColor: 'red'
});

body = ['ab','cb'];
console.log(String(body).errorColor);