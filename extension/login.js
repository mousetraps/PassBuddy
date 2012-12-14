function successfulLogin(un, pw) {    
    localStorage.setItem("username", un);
    localStorage.setItem("master_password", pw);
    $("div#logindiv").css("display", "none");
    $("div#contentdiv").css("display", "block");
    $("div#greetingdiv").text("You are now logged in as " + un);
    $("div#logoutdiv").css("display", "block");
}

$(function() {

  // Log in
  $("button#login_submit").click(function() {
    var un = $("input#login_username").val();
    var mp = $("input#login_mp").val();
    // Server should set a secure session cookie that is sent with every subsequent request to it
    var hash = mphash(mp).toString();
    $.post(SERVER_URL_HTTPS + "/login", {"account": un, "password": hash}, function(data) {
	    successfulLogin(un, mp);
	    chrome.tabs.create({"url": SERVER_URL_HTTPS + "/login"});
    });
  });

});