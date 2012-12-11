function getRandom() {
    var dfd = $.Deferred();

    $.ajax({
        type: "GET",
        url: "http://www.random.org/cgi-bin/randbyte",
        data: "nbytes=1024&format=hex",
        success: function(message){
            console.log("got random");
            dfd.resolve(message)
        }
    });

    console.log("getting random");

    return dfd.promise();
}


function getKeyPair(message) {
    var dfd = $.Deferred();


    // TODO - fuck.. code dup
    var password = $("#loginForm input[name=password]")[0].value;
    sessionStorage.masterPassword = password;


    console.log( "got random string: " + message );
    seed(message);
    genkey(8,publicKey, privateKey); // TODO - 8 isn't safe, but it's faster for now
    console.log( "generated (public:" + publicKey + ", private:" + privateKey + ")" );

    var packedPublic = packPublicKey(publicKey);
    var packedPrivate = packPrivateKey(privateKey);

    dfd.resolve(packedPublic, packedPrivate);

    return dfd.promise();

}


function submitLoginCredentials(publicKey, privateKey){
    return $.Deferred(function( dfd ) {

        var form = $("#loginForm");


        var password = form.find("input[name=password]")[0].value;
        var account = form.find("input[name=account]")[0].value;

        var hashedPassword = hashMasterPassword(password);

        // TODO - check whether sessionStorage is secure... another idea is to do something with variable scope
        sessionStorage.masterPassword = password;
        form.value = hashedPassword;

        console.log("local password: " + sessionStorage.masterPassword);
        console.log("hashed password: " + hashedPassword);


        console.log(publicKey + " " + privateKey);
        $.post("/login",
            {
                'account': account,
                'password': password,
                'publicKey': publicKey,
                'privateKey': privateKey

            },
            function(data) {

                // TODO - refactor this out into deferred function
                // TODO - send redirect form handler instead
                console.log("redirecting to manage");
                window.location = "/manage";

                dfd.resolve();

            }
        );


    }).promise();

}

function onLoginSubmit() {

    getRandom().pipe(getKeyPair).pipe(submitLoginCredentials).done();
}