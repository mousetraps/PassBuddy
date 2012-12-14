function getRandom() {
    var dfd = $.Deferred();

    $.ajax({
        type: "GET",
        url: "https://www.random.org/cgi-bin/randbyte",
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
    sessionStorage.setItem("masterPassword", getFormPassword());


    console.log( "got random string: " + message );
    seed(message);
    genkey(8,publicKey, privateKey); // TODO - 8 isn't safe, but it's faster for now
    console.log( "generated (public:" + publicKey + ", private:" + privateKey + ")" );

    var packedPublic = packPublicKey(publicKey);
    var packedPrivate = packPrivateKey(privateKey);

    dfd.resolve(packedPublic, packedPrivate);

    return dfd.promise();

}

function getFormUsername() {
    return $("#loginForm").find("input[name=account]")[0].value;
}

function getFormPassword() {
    return $("#loginForm").find("input[name=password]")[0].value;
}


function getSalt() {

    var username = getFormUsername();

    return $.get("/login",
        {
            "username": username,
            "action": "getSalt"
        }
    );
}

function decryptSalt(encryptedSalt) {
    var dfd = $.Deferred();

    var masterPassword = getFormPassword();
    var salt = symmetricDecrypt(JSON.parse(decodeURIComponent(encryptedSalt)), masterPassword);

    dfd.resolve(salt);
    return dfd.promise();
}

function onLoginSubmit() {


    getSalt().pipe(decryptSalt).pipe(
        function(salt) {
            var username = getFormUsername();
            var masterPassword = getFormPassword();
	    sessionStorage.setItem("masterPassword", masterPassword);

            var password = hashMasterPassword(masterPassword + salt);

            $.post("/login",
                {
                    'account': username,
                    'password': password
                },
                function(data) {

                    // TODO - refactor this out into deferred function
                    // TODO - send redirect form handler instead
                    console.log("redirecting to manage");
                    window.location = "/manage";

                }
            );
        }).done();
}

function onRegisterSubmit() {

    $.when(getRandom().pipe(getKeyPair), getRandom()).then(

        function(keyPair, salt) {

            // TODO: this isn't maintainable...
            var publicKey = keyPair[0];
            var privateKey = keyPair[1];

            var username = getFormUsername();

            var masterPassword = getFormPassword();

            var password = hashMasterPassword(masterPassword + salt);
            var encryptedSalt = encodeURIComponent(JSON.stringify(symmetricEncrypt(salt, masterPassword)));

            $.post("/login",
                {
                    'account': username,
                    'password': password,
                    'publicKey': publicKey,
                    'privateKey': privateKey,
                    'encryptedSalt': encryptedSalt

                },
                function(data) {

                    // TODO - refactor this out into deferred function
                    // TODO - send redirect form handler instead
                    console.log("redirecting to manage");
                    window.location = "/manage";

                }
            );
        }
    ).done();

}
