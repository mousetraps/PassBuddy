var port;

function getUrl() {
    //chrome.extension.sendMessage({url: location.href}, function(response) {});
    port.postMessage({"url": location.href});
}

function fillData(data) {
    form_info = JSON.parse(data);
    $(form_info.username_jquery_selector).val(username);
    $(form_info.password_jquery_selector).val(password);
}

function addLoadEvent(func) { 
    var oldonload = window.onload; 
    if (typeof window.onload != 'function') { 
	window.onload = func; 
    } else { 
	window.onload = function() { 
	    if (oldonload) { 
	        oldonload(); 
	    } 
	    func(); 
	} 
    } 
} 

addLoadEvent(function() {
	port = chrome.extension.connect({name: "pwfill"});
	console.log(port);
	port.onMessage.addListener(function(msg) {
		if(msg.fn == "getUrl") {
		    getUrl();
		} else if(msg.fn == "fillData") {
		    fillData(msg.data);
		} else {
		    console.log("unrecognized message to content script");
		}
	    });
    });
