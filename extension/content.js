function putAccountsInLocalStorage(callback) {
    console.log("asking to put accts in local storage");
    $.get(SERVER_URL_HTTPS + "/manage", {"action": "json"}, function(data) {
	    jdata = jQuery.parseJSON(data);
	    for(var ai = 0; ai < jdata.length; ai++) {
		console.log(jdata[ai]);
		var unesc = jdata[ai].encr_host_password.replace(/\\\"/g, '"');
		unesc = unesc.replace(/^\"/, '');
		unesc = unesc.replace(/\"$/, '');
		jdata[ai].encr_host_password = unesc;
	    }
	    localStorage.setItem("accounts", JSON.stringify(jdata));
	    if(callback) { callback(); }
	});    
}

function fillPasswordWrapper() {
    console.log("backgroundpage thinks url is " + chrome.extension.getBackgroundPage().currentURL);
    putAccountsInLocalStorage(function() { fillPassword(chrome.extension.getBackgroundPage().currentURL) });
}

function fillPassword(host) {
    console.log("fill password request for " + host);
    var jaccounts = JSON.parse(localStorage.getItem("accounts"));
    for(var ai = 0; ai < jaccounts.length; ai++) {
	console.log(jaccounts[ai]);
	if(jaccounts[ai].host_url == host) {
	    //var unesc = jaccounts[ai].encr_host_password.replace(/\\\"/g, '"');
	    var unesc = jaccounts[ai].encr_host_password;
            //console.log(unesc);
	    //console.log(JSON.parse(unesc));
	    var password = decrypt(unesc, localStorage.getItem("master_password"));
	    console.log(password);
	    detectLoginFormAndFillPassword(host, jaccounts[ai].host_username, password);
	    break;
	}
    }
}

function detectLoginFormAndFillPassword(host, username, password) {
    $.get(SERVER_URL_HTTPS + "/detect_login_form", {"url": host}, function(data) {	    
	    console.log("got data back from detect login form: " + data);
	    form_info = JSON.parse(data);
	    fill_username_code = "";
	    fill_password_code = "";
	    if(form_info.username_selector.type == "id") {
		fill_username_code = "document.getElementById(\"" + form_info.username_selector.value + "\").value = \"" + username + "\";";
	    } else { //name, must have form name too then
		fill_username_code = "document." + form_info.form_selector.value + "." + form_info.username_selector.value + ".value = " + username + ";";
	    }
	    if(form_info.password_selector.type == "id") {
		fill_password_code = "document.getElementById(\"" + form_info.password_selector.value + "\").value = \"" + password + "\";";
	    } else { //name, must have form name too then
		fill_password_code = "document." + form_info.form_selector.value + "." + form_info.password_selector.value + ".value = " + password + ";";
	    }
	    fill_form_code = fill_username_code + fill_password_code;
	    console.log(fill_form_code);
	    chrome.tabs.executeScript(chrome.extension.getBackgroundPage().currentID, {
		    "code": fill_form_code
		});
	});
}
