(function () {

    const PublicationActionEndpoint =

    function(prefix, target_url) {

        this.prefix_ = prefix;
        this.target_url_ = target_url;

        this.update_markup_cache_clicked = this.update_markup_cache_clicked.bind(this);
        this.markup_cache_received = this.markup_cache_received.bind(this);

        const updateMarkupCacheButton = document.getElementById(this.prefix_ + "-update_markup_cache-button");
        updateMarkupCacheButton.addEventListener("click", this.update_markup_cache_clicked, false);
    };

    PublicationActionEndpoint.prototype.update_markup_cache_clicked = function (event) {

        const resultElement = document.getElementById(this.prefix_ + "-result_download");

        resultElement.style = "display: none;";

        const actionType = encodeURIComponent("update_markup_cache");

        const request = new XMLHttpRequest();

        request.open("GET", this.target_url_ + "?type=" + actionType, true);
        request.responseType = "json";
        request.onload = this.markup_cache_received;
        request.send();
    };

    PublicationActionEndpoint.prototype.markup_cache_received = function (event) {
        const request = event.target;

        if( request.readyState == 4 ) { //LOADED
            if( request.response ) {
                publications = request.response;

                result = "";

                Object.keys(publications).forEach(function (key) {
                    var value = publications[key];
                    //value = JSON.parse(value);
                    result += "<li>" + value + "</li>\n";
                });

                result = "<html>\n<head>\n"
                         + "<meta charset=\"utf-8\">\n"
                         + "<link href=\"fonts.css\" rel=\"stylesheet\" type=\"text/css\">\n"
                         + "<link href=\"source_reference.css\" rel=\"stylesheet\" type=\"text/css\">\n"
                         + "<link href=\"source_reference_dark_theme.css\" rel=\"stylesheet\" type=\"text/css\">\n"
                         + "</head>\n"
                         + "<body>\n"
                         + "<ul>\n"
                         + result
                         + "</ul>\n</body>\n</html>\n";

                console.log(result);

                var blob = new Blob([result], {type: 'application/text'});
                var blobURL = window.URL.createObjectURL(blob);

                const resultElement = document.getElementById(this.prefix_ + "-result_download");

                resultElement.href = blobURL;
                resultElement.download = "MarkupCache.html"
                resultElement.style = "display: inline;";
            }
        }
    };

    if( window.bibster == null ) {
        window.bibster = {};
    }

    window.bibster.PublicationActionEndpoint = PublicationActionEndpoint;
})();