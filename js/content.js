function createOwnAccountsList(accounts, un) {
    var clickListeners = {};
    var res = "";
    res += "<button id=\"create_account\">Add Account</button><br/>";
    res += "<table id=\"accounts\">";
    for(var ai = 0; ai < accounts.length; ai++) {
	console.log(ai);
	var h = accounts[ai].host_url;
	var hu = accounts[ai].host_username;
	var grantees = accounts[ai].grantees;
	var acres = "<tr><td><button id=\"delete_account_" + ai + "\">X</button></td><td>" + h + "</td><td>" + hu + "</td><td>Shared with:<br/><ul>";
	for(var gi = 0; gi < grantees.length; gi++) {
	    var grantee = grantees[gi];
	    acres += "<li><button id=\"delete_grantee_" + ai + "_" + gi + "\">X</button><span id=\"grantee_" + ai + "_" + gi + "\">" + grantee + "</span></li>";
	    clickListeners["button#delete_grantee_" + ai + "_" + gi] = function(gunc, hc, huc) {
		return function() {
		    unshareAccount(un, gunc, hc, huc);
		};
	    }(grantee, h, hu);
	}
	acres += "</ul><input type=\"text\" id=\"add_grantee_name_" + ai + "\" /><button id=\"add_grantee_" + ai  + "\">Share</button></td></tr>";
	clickListeners["button#add_grantee_" + ai] = function(gieltc, hc, huc) {
	    return function() {
		shareAccount(un, gieltc, hc, huc);
	    };
	}("input#add_grantee_name_" + ai, h, hu);
	clickListeners["button#delete_account_" + ai] = function(hc, huc) {
	    return function() {
		deleteAccount(un, hc, huc);
	    };
	}(h, hu);
	console.log(acres);
	res += acres;
    }
    res += "</table>";
    $("div#own_accounts").html(res);
    for(var clickListenerElt in clickListeners) {
	console.log(clickListenerElt);
	$(clickListenerElt).click(clickListeners[clickListenerElt]);
    }
    $("button#create_account").click(function() {
	    console.log("trying to display the create account options");
	    $("div#create_account_options").css("display", "block");
	});
}

// These accounts should look like:
// {granter: [{host: "foo.com", host_username "me"}, ...], other_granter: ...}
function createGrantedAccountsList(accounts, username) {
    var clickListeners = {};
    var res = "";
    res += "<button id=\"refresh_granted_accounts\">Refresh</button><br/>";    
    res += "<table id=\"granted_accounts\">";
    for(var granter in accounts) {
	res += "<tr>";
	res += "<td rowspan=\"" + accounts[granter].length + "\">" + granter + "</td>";
	for(var hui = 0; hui < accounts[granter].length; hui++) {
	    if(hui > 0) {
		res += "<tr>";
	    }
	    var h = accounts[granter][hui].host_url;
	    var hu = accounts[granter][hui].host_username;
	    res += "<td>" + h + "</td><td>" + hu + "</td><td>" + "<form action=\"/proxy/init\" method=\"post\"><input type=\"hidden\" name=\"granter\" value=\"" + granter + "\"/><input type=\"hidden\" name=\"host_url\" value=\"" + h + "\"/><input type=\"hidden\" name=\"host_username\" value=\"" + hu + "\"/><input type=\"hidden\" name=\"username\" value=\"" + username + "\"/><button id = \"" + granter + "_" + hui + "\" type=\"submit\">Login as " + granter + "</button></form>" + "</td></tr>";
	    /*
	    clickListeners["button#" + granter + "_" + hui] = function(gunc, hc, huc, button_selectorc) {
		return function() {
		    goToGrantedAccount(username, gunc, hc, huc, button_selectorc);
		};
	    }(granter, h, hu, "button#" + granter + "_" + hui);
	    */
	}
    }
    res += "</table>";
    $("div#granted_accounts").html(res);
    for(var clickListenerElt in clickListeners) {
	console.log(clickListenerElt);
	$(clickListenerElt).click(clickListeners[clickListenerElt]);
    }
    $("button#refresh_granted_accounts").click(function() {
	    refreshGrantedAccounts(username);
	});
}

  // Get the users with whom you are sharing accounts. The session cookie obtained from login will be sent with this request.
function requestContent() {
    // Local storage for test
    /*
    if(localStorage.getItem("accounts") == null) {
	localStorage.setItem("accounts", JSON.stringify([{"host": "http://www.facebook.com", "host_username": "foob", "grantees": ["bar"]}, {"host": "http://www.google.com", "host_username": "boof", "grantees": ["bar", "baz"]}]));
    }

    if(localStorage.getItem("granted_accounts") == null) {
	localStorage.setItem("granted_accounts", JSON.stringify({"bar": [{"host": "http://www.facebook.com", "host_username": "barbar"}, {"host": "http://www.google.com", "host_username": "barbar2"}], "baz":[{"host": "http://www.mitfcu.org", "host_username": "zabbers"}]}));
    }

    createOwnAccountsList(JSON.parse(localStorage.getItem("accounts")), username);
    createGrantedAccountsList(JSON.parse(localStorage.getItem("granted_accounts")), username);
    return 1;
    */

    // data should contain status and accounts
    $.get("/own_accounts", {}, function(data) {
	    jdata = jQuery.parseJSON(data);
	    if(jdata.status == "OK") {
		$("div#greeting").text("Hello, " + jdata.username);
		createOwnAccountsList(jdata.accounts, jdata.username);
		refreshGrantedAccounts(jdata.username);
	    } else {
		$("div#error").text(jdata.error);
	    }
	});
}

function unshareAccount(granter_username, grantee_username, host, host_username) {	
    console.log(grantee_username);
    // Alter local storage - just for testing
    /*
    var jaccounts = JSON.parse(localStorage.getItem("accounts"));
    for(var ai = 0; ai < jaccounts.length; ai++) {
	console.log(host + " " + host_username);
	console.log(ai);
	console.log(jaccounts[ai]);
	if(jaccounts[ai].host_url == host && jaccounts[ai].host_username == host_username) {
	    console.log("found it");
	    var newgrantees = [];
	    for(var gi = 0; gi < jaccounts[ai].grantees.length; gi++) {
		if(jaccounts[ai].grantees[gi] != grantee_username) {
		    newgrantees.push(jaccounts[ai].grantees[gi]);
		} else {
		    console.log("not adding back grantee " + gi);
		}
	    }
	    jaccounts[ai].grantees = newgrantees;
	    break;
	}
    }
    localStorage.setItem("accounts", JSON.stringify(jaccounts));
    createOwnAccountsList(jaccounts, granter_username);
    return 1;
    */

    // Tell server to alter databases
    $.post("/unshare", {"username": granter_username, "grantee_username": grantee_username, "host_url": host, "host_username": host_username}, function(data) {
	    jdata = jQuery.parseJSON(data);
	    if(jdata.status == "OK") {
		requestContent();
	    } else {
		$("div#error").text(jdata.error);
	    }

	});
}

function shareAccount(granter_username, grantee_username_element, host, host_username) {
    var grantee_username = $(grantee_username_element).val();
    console.log(grantee_username);

    // Alter local storage - just for testing
    /*
    var jaccounts = JSON.parse(localStorage.getItem("accounts"));
    for(var ai = 0; ai < jaccounts.length; ai++) {
	console.log(host + " " + host_username);
	console.log(ai);
	console.log(jaccounts[ai]);
	if(jaccounts[ai].host_url == host && jaccounts[ai].host_username == host_username) {
	    console.log("found it");
	    var encrypted_password = localStorage.getItem("encrypted-password_" + host + "_" + host_username);
	    if(encrypted_password == null) {
		$("div#error").text("Could not find a stored password for this account. Try deleting and readding the account.");
		return;
	    }
	    var mp = window.prompt("Please enter your master password to share this account.");
	    if(mp == null) { // user canceled prompt; just return
		$("div#error").text("Failed to share this account.");
		return;
	    }
	    var password = decrypt(encrypted_password, mp);
	    jaccounts[ai].grantees.push(grantee_username);
	    break;
	}
    }
    localStorage.setItem("accounts", JSON.stringify(jaccounts));
    createOwnAccountsList(jaccounts, granter_username);
    return 1;
    */

    // Tell server to alter databases (get status and accounts back)
    /*
    var encrypted_password = localStorage.getItem("encrypted-password_" + host + "_" + host_username);
    if(encrypted_password == null) {
	$("div#error").text("Could not find a stored password for this account. Try deleting and readding the account.");
	return;
    }

    var mp = window.prompt("Please enter your master password to share this account.");
    if(mp == null) { // user canceled prompt; just return
	$("div#error").text("Failed to share this account.");
	return;
    }    
    var password = decrypt(encrypted_password, mp);
    */
    $.post("/share", {"username": granter_username, "grantee_username": grantee_username, "host_url": host, "host_username": host_username}, function(data) {
	    jdata = jQuery.parseJSON(data);
	    if(jdata.status == "OK") {
		requestContent();
	    } else {
		$("div#error").text(jdata.error);
	    }

	});
}

// Ask the server to give an update on accounts granted to username, including storing encrypted info in local storage
function refreshGrantedAccounts(username) {
    console.log("refreshGrantedAccounts called for " + username);
    /*
    var ga = JSON.parse(localStorage.getItem("granted_accounts"));
    for(var granter in ga) {
	for(var hui = 0; hui < ga[granter].length; hui++) {
	    var account = ga[granter][hui];
	    console.log(account);
	    localStorage.setItem("encrypted-info_" + granter + "_" + username + "_" + account.host_url + "_" + account.host_username, "jasldfjslfjslkdjflsd");
	}
    }
    createGrantedAccountsList(JSON.parse(localStorage.getItem("granted_accounts")), username);
    return 1;
    */
    $.get("/granted_accounts", {"username": username}, function(data) {
	    jdata = jQuery.parseJSON(data);
	    if(jdata.status == "OK") {
		/*
		for(var account in jdata.accounts) {
		    localStorage.setItem("encrypted-info_" + account.granter_username + "_" + account.grantee_username + "_" + account.host_url + "_" + account.host_username, account.encrypted_info);
		}
		*/
		createGrantedAccountsList(jdata.accounts, username);
	    } else {
		$("div#error").text(jdata.error);
	    }
	});
}

// Create a new account given the host, host username, and password. Ask for and encrypt with the master password. The server will check the master password to ensure it is correct, but will just send back and OK or not; if ok, proceed to encrypt the account info and store in local storage.
function createAccount(host, host_username, password, master_password) {
    // stub
    /*
    console.log("createAccount called for " + host + ", " + host_login_page + ", " + host_username + ", " + password + ", " + master_password);
    var encrypted_password = encrypt(password, master_password);
    localStorage.setItem("encrypted-password_" + host + "_" + host_username, encrypted_password);
    var accounts = JSON.parse(localStorage.getItem("accounts"));
    accounts.push({"host": host, "host_username": host_username, "grantees": []});
    localStorage.setItem("accounts", JSON.stringify(accounts));
    $("div#create_account_options").css("display", "none");
    $("div#create_account_options input").val("");
    createOwnAccountsList(accounts);
    return 1;
    */

    $.post("/add_account", {"username": localStorage.getItem("username"), "host_url": host, "host_username": host_username, "host_password": encrypt(password, master_password), "password": mphash(master_password).toString()}, function(data) {
	    jdata = jQuery.parseJSON(data);
	    if(jdata.status == "OK") {
		// Store the encrypted password for this account in local storage
		//var encrypted_password = encrypt(password, master_password);
		//localStorage.setItem("encrypted-password_" + host + "_" + host_username, encrypted_password);
		$("div#create_account_options").css("display", "none");
		$("div#create_account_options input").val("");
		requestContent();
	    } else {
		// Do nothing but show the error
		$("div#create_account_error").text(jdata.error);
	    }
	 });
}

function deleteAccount(username, host, host_username) {
    $.post("/remove_account", {"username": username, "host_url": host, "host_username": host_username}, function(data) {
jdata = jQuery.parseJSON(data);
	    if(jdata.status == "OK") {
		requestContent();
	    } else {
		// Do nothing but show the error
		$("div#error").text(jdata.error);
	    }	    
	});
}

$(function() {
    $("div#contentdiv").tabs();
    requestContent();
    });