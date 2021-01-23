console.log("Cus, tady Ricci.");

var selectd = "";

const divs = document.querySelectorAll("div");

divs.forEach(element => {
    element.addEventListener("mouseup", selectedMouseUp);
});

// ----- new elements initialization --------------------

var crazy_div_id = "lknasdlnasldfnlasdnf";
const crazy_btn_id = "lknsadfdfasdlnasldfnlasdnf";
var crazy_btn2_id = "lknsadadasdlnasldfnlasdnf";
var crazy_input_id = "lknsainputdadasdlnasldfnlasdnf";
var crazy_inputsubmit_id = "submitinputdadasdlnasldfnlasdnf";


// --- inline text swap button -------------------
var button = document.createElement("button");
button.id = crazy_btn_id;
button.innerHTML = "Zkus vymyslet pokračování";
button.addEventListener("click", function() {
    // transformHighlighted()
    alert("Ted by se nahradil zvyrazneny text");
});

var button2 = document.createElement("button");
button2.innerHTML = "Co si o tom myslíš?";
button2.id = crazy_btn2_id;
button2.addEventListener("click", function() {
    alert("Ted by prisla odpoved ze serveru s komentarem naseho\
     robota. S nim by se popripade dalo dale konverzovat.");
});

var input_field = document.createElement("input");
input_field.type = "text";
input_field.id = crazy_input_id;

var input_submit = document.createElement("button");
input_submit.innerHTML = "Pokračuj na téma .."
input_submit.id = crazy_inputsubmit_id;

var btn_div = document.createElement("div");
btn_div.id = crazy_btn_id;
btn_div.style.position = "absolute";
btn_div.style.top =0;
btn_div.style.left = "0";
btn_div.style.display = "none";

var body = document.getElementsByTagName("body")[0];
btn_div.appendChild(button);
btn_div.appendChild(button2);
btn_div.appendChild(input_field);
btn_div.appendChild(input_submit);

body.appendChild(btn_div);

input_submit.addEventListener("click", translate_with_condition(selectd,input_field.value))

// --- functions -----------------------------

// make buttons disappear
function documentMouseDown(event){}

// 
async function postData(url, data){
    const params = new URLSearchParams(data).toString();
    const url2 = url + "/" + params;
    console.log(url2);
    
    return fetch(url2)
    .then(response => {
        console.log("in response text.");
        return response.text();
    }).then((resp) => {
        console.log('in json.parse()');
        resolve(resp ? JSON.parse(resp) : {})
    }).catch((error) => {
        console.log('in reject' + url);
    });
}

function selectedMouseUp(event) {
    const selected = window.getSelection().toString().trim();

    if(selected.length){
        const x = event.clientX;
        const y = event.clientY;

        btn_div.style.left = `${x}px`;
        btn_div.style.top = `${x}px`;

        btn_div.style.display = "block";
    }

    selectd = selected;

    console.log(selected);
}

// asks for response that is 
function translate_with_condition(highlighted, direction){
    var data = {prompt:highlighted, input:direction};
    var url = "http://localhost:8080";

    try {
        postData(url,data).then(data => {
            console.log(data)
        })
        /*.then(
           swapText(highlighted, data) 
        )*/;  
    } catch (error) {
        console.log('there was an error.');
    } 
}

// --- extension behaviour -----------------
document.addEventListener("mousedown", documentMouseDown);