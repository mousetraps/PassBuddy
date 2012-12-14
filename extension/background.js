var SERVER_URL_HTTPS = "https://passbuddy.appspot.com";
var LOGIN_COOKIE_NAME = "PBLOGIN";
chrome.cookies.remove({name: LOGIN_COOKIE_NAME, url: SERVER_URL_HTTPS}, function(details) { console.log(details); });
localStorage.removeItem("username");
localStorage.removeItem("master_password");

// Keep track of current tab
// From http://stackoverflow.com/questions/6451693/chrome-extension-how-to-get-current-webpage-url-from-background-html
currentURL="about:blank"; //A default url just in case below code doesn't work
currentID=-1; //A default id just in case below code doesn't work
chrome.tabs.onUpdated.addListener(function(tabId,changeInfo,tab){ //onUpdated should fire when the selected tab is changed or a link is clicked 
	console.log("tab updated");
	chrome.tabs.getSelected(null,function(tab){
		console.log("new url: " + tab.url);
		currentURL=tab.url;
		currentID=tab.id;
	    });
    });

