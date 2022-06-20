function loginUser(username, password, lang, redirect_uri) {
    // Call the web login
    callWEB("post", "/login", {
        username: username,
        password: password
    },
    function(res) {
        // Store the cookie
        Cookies.set("web_token", res.access_token);

        // Call the API login
        callAPI("post", "/login", {
            username: username,
            password: password
        },
        function(res) {
            // Store the cookie
            Cookies.set("api_token", res.access_token);

            // If the user comes from an expired page
            if (redirect_uri) {
                // Redirect there
                window.location.replace(redirect_uri);
            }

            else {
                // Return home
                redirectHome(lang);
            }
        });
    });
}

function logoutUser(lang) {
    // Clear the web token
    Cookies.set("web_token", "", -1);

    // Call the API logout
    callAPI("delete", "/logout", null,
    function() {
        // Clear the API token
        Cookies.set("api_token", "", -1);

        // Return home
        redirectHome(lang);
    });
}

function createUser(paramsJson, successCallback, failedCallback) {
    // Call the API
    callAPI("post", "/user", paramsJson,
    successCallback, failedCallback);
}

function updateUser(username, paramsJson, successCallback, failedCallback) {
    // Call the API
    callAPI("patch", "/user/" + username, paramsJson,
    successCallback, failedCallback);
}

function deleteUser(username, successCallback, failedCallback) {
    // Call the API
    callAPI("delete", "/user/" + username, null,
    successCallback, failedCallback);
}


//////////
// Clip Zip Ship Admin
function queryMetadata(uuid, successCallback, failedCallback) {
    callAPI("GET", "/metadata/" + uuid, null,
        successCallback, failedCallback);
}

function queryExtent(table_name, successCallback, failedCallback) {
    callAPI("GET", "/extent/" + table_name, null,
        successCallback, failedCallback);
}

function addCollection(payload, successCallback, failedCallback) {
     callAPI("PUT", "/collections", payload,
        successCallback, failedCallback);   
}

//////////
// CORE

function redirectHome(lang) {
    if (lang == "fr")
        window.location.replace("/fr/accueil");
    else
        window.location.replace("/en/home");
}

function _defaultSuccessCallback(res) {
    alert("Success!");
}

function _defaultFailedCallback(err) {
    // If handling it
    if (err.responseJSON) {
        var detailFr = "";
        if (err.responseJSON.detail_fr)
            detailFr = "\n" + err.responseJSON.detail_fr;
        console.error(err.responseJSON);
        alert(err.responseJSON.detail + detailFr);
    }

    else {
        console.error(err);
        alert("Failed...");
    }
}


function callWEB(verb, url, paramsJson, success, failed) {
    // If the parameters are set
    var d = null;
    if (paramsJson)
        d = JSON.stringify(paramsJson);

    // Set the authentication headers automatically (if the user is authenticated)
    var headers = {};
    if (document.___CSRF_TOKEN) {
        headers["X-CSRFToken"] = document.___CSRF_TOKEN;
    }

    // Call
    $.ajax({
        type: verb,
        url: url,
        headers: headers,
        data: d,
        contentType: "application/json; charset=utf-8",
        success: success || _defaultSuccessCallback,
        error: failed || _defaultFailedCallback
    });
}

function callAPI(verb, url, paramsJson, success, failed) {
    // If the parameters are set
    var d = null;
    if (paramsJson)
        d = JSON.stringify(paramsJson);

    // Set the authentication headers automatically (if the user is authenticated)
    var headers = {};
    var api_token = Cookies.get("api_token");
    if (api_token) {
        headers["Authorization"] = "Bearer " + api_token;
    }

    // Call
    $.ajax({
        type: verb,
        url: document.___API_URL + url,
        headers: headers,
        data: d,
        contentType: "application/json; charset=utf-8",
        success: success || _defaultSuccessCallback,
        error: failed || _defaultFailedCallback
    });
}

