function mphash(mp) {
    return CryptoJS.SHA256(mp);
}

function decrypt(ciphertext, key) {
    console.log("decrypt called on " + ciphertext + ", " + key);
    var res = sjcl.decrypt(key, ciphertext);
    console.log(res);
    return res;
}

function encrypt(message, key) {
    console.log("encrypt called on " + message + ", " + key);
    var res = sjcl.encrypt(key, message);
    console.log(res);
    return res;
}
