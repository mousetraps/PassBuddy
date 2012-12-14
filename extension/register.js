$(function() {

  // Register
  $("button#register_submit").click(function() {
    var un = $("input#login_username").val();
    var mp = $("input#login_mp").val();
    var hash = mphash(mp).toString();
    // Server should set a secure session cookie that is sent with every subsequent request to it
    $.post(SERVER_URL_HTTPS + "/register", {"username": un, "password": hash}, function(data) {
	    jdata = jQuery.parseJSON(data);
	    if(jdata.status == "OK") {
		successfulLogin(un);
	    } else {
		$("input#login_password").text("");
		$("div#error").text(jdata.error);
	    }
	});
    
      });
    });