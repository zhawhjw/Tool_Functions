var fs = require('fs');

fs.readFile('./test.json', 'utf8', function(err, contents) {
    JSON.parse(contents);
    console.log(contents.length);
});

console.log('after calling readFile');