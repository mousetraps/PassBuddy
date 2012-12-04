$(function() {
	$("button#create_account_cancel").click(function () {
		$("div#create_account_options").css("display", "none");
		$("div#create_account_options input").val("");
	    });

	$("button#create_account_submit").click(function() {
		createAccount($("input#create_account_host").val(),
			      $("input#create_account_username").val(),
			      $("input#create_account_password").val(),
			      $("input#create_account_master_password").val()
			      );
		
	    });
    });