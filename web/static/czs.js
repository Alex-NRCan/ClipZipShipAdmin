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

function queryExtent(schema, table_name, crs, data_host, data_port, data_name, data_user, data_password, successCallback, failedCallback) {
    callAPI("POST", "/extent/" + schema + "/" + table_name + "/" + crs, {
        db_host: data_host,
        db_port: data_port,
        db_name: data_name,
        db_user: data_user,
        db_password: data_password
    },
    successCallback, failedCallback);
}

function addParent(payload, successCallback, failedCallback) {
     callAPI("PUT", "/parents", payload,
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
        window.location.replace("/fr/home");
    else
        window.location.replace("/en/home");
}

function _defaultSuccessCallback(res) {
    alert("Success!");
}

function _readErrorMessage(err, lang) {
    // If handling it
    if (err.responseJSON) {
        var msg = err.responseJSON.detail;

        // If French language
        if (lang == "fr" && err.responseJSON.detail_fr)
            msg = err.responseJSON.detail_fr;
        return msg;
    }

    else {
        return "Failed...";
    }
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

