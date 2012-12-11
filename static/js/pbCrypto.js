// TODO - any way to link js files? this depends on crypto.js, cryptoHelper.js, cryptojs-sha256

function hashMasterPassword(masterPassword) {
    return CryptoJS.SHA256(masterPassword);
}

// TODO - this is hideous, fix it later :)
var publicKey = Object();
var privateKey = Object();

function asymmetricEncrypt(message, publicKey) {
    return enc(message, publicKey);
}

function asymmetricDecrypt(ciphertext, privateKey){
    return dec(ciphertext, privateKey);
}

function symmetricEncrypt(message, key) {
    console.log("encrypt called on " + message + ", " + key);
    var res = sjcl.encrypt(key, message);
    console.log(res);
    return res;
}

function symmetricDecrypt(ciphertext, key) {
    console.log("decrypt called on " + ciphertext + ", " + key);
    var res = sjcl.decrypt(key, ciphertext);
    console.log(res);
    return res;
}

function packPublicKey(publicKey) {
    var string_public = JSON.stringify(publicKey);
    var safe_public = encodeURIComponent(string_public);

    return safe_public;
}

function packPrivateKey(privateKey) {

    var string_private = JSON.stringify(privateKey);
    var encr_string_private = symmetricEncrypt(string_private, sessionStorage.masterPassword);
    var safe_encr_private = encodeURIComponent(encr_string_private);

    return safe_encr_private;

}

function unpackPublicKey(publicKey) {

    var string_public = decodeURIComponent(publicKey);
    var json_public = JSON.parse(string_public);

    console.log("unpaccked: " + json_public);

    return json_public;

}

function unpackPrivateKey(privateKey) {


    var encr_string_private = decodeURIComponent(privateKey);
    var string_private = symmetricDecrypt(encr_string_private, sessionStorage.masterPassword);
    var json_private = JSON.parse(string_private);

    return json_private;

}