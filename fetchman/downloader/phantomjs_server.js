// phantom_server.js
var webserver = require("webserver");
var server = webserver.create();
var service = server.listen(8888, function(request, response) {
    var url = request.post["url"];
    console.log('method:' + request.method);
    console.log('url:' + url);
    var webPage = require("webpage");
    var page = webPage.create();
    page.settings.userAgent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36";
    page.settings.resourceTimeout = 5000;
    page.open(url, function start(status) {
        if (status == "success") {
            window.setTimeout(function() {
                content = page.content;
                response.statusCode = 200;
                response.write(content);
                response.close();
                page.close()
            }, 1000)
        } else {
            response.statusCode = 500;
            response.write("error");
            response.close();
            page.close()
        }
    })  
});
