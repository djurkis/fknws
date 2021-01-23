
const cp = require('child_process');
// const cors = require('cors');
const { stderr } = require('process');

const util = require('util');
const exec = util.promisify(cp.exec);

///////////////////////////////////////////////////////////////

var http = require('http');

var program = "./pt.sh";

async function get_response(prompt,input = ''){
    
    var command = program + " \"" +
    prompt + "\" " + "\"" +
    input + "\"";

    var data = await exec(command);
    return data[0];
}

var srvr = http.createServer(function (req,res) {
    console.log(req.url);

    if(req.method == 'GET'){
        console.log('GET');
        var params = new URLSearchParams(req.url.slice(1));

        let out = get_response(params.get('prompt'),params.get('input'));
        console.log(out);
        out.then((out) => {
            console.log('in out.then');
            console.log(out);

            req


            res.end();
        });
    }
});

srvr.listen(8080);