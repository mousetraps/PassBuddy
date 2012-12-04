$(function() {

  // Register
  $("button#register_submit").click(function() {
    var un = $("input#login_username").val();
    var mp = $("input#login_mp").val();
    var hashedmp = mphash(mp);
    console.log("hashed mp:");
    console.log(hashedmp.toString());
    //successfulLogin(un);
    //return 1;

    // Server should set a secure session cookie that is sent with every subsequent request to it
    $.post("/register", {"username": un, "password": hashedmp.toString()}, function(data) {
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