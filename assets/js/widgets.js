/**
 * Copyright 2013 Janusz Skonieczny
 */

$(function () {
    function formatResult(o) {
        return o.cn;
    }

    function formatSelection(o) {
        return o.cn;
    }

    function dataId(o) {
        return o.id;
    }

    $("input.select2").each(function (i, e) {
        var self = $(this);
        var url = self.data("url");
        var query_field = self.data("query_field");
        var page_limit = 15;
        self.select2({
            placeholder: "Szukaj…",
            minimumInputLength: 3,
            ajax: {
                url: url,
                quietMillis: 100,
                data: function (term, page) { // page is the one-based page number tracked by Select2
                    var rv = {
                        page_limit: page_limit, // page size
                        page: page, // page number
                        query_field: query_field,
                        search: term
                    };
                    // rv [query_field] = term;
                    return rv
                },
                results: function (data, page) {
                    var more = (page * page_limit) < data.total; // whether or not there are more results available

                    // notice we return the value of more so Select2 knows if more results can be loaded
                    return {results: data.list, more: more};
                }
            },
            formatResult: formatResult,
            formatSelection: formatSelection,
            id: dataId,
            initSelection: function (element, callback) {
                var $element = $(element);
                var key = element.val();
                log.debug("key=", key);
                if (key == "None") {
                    return;
                }
                return $element.data("display_value")
/*
                if (typeof(Storage) !== "undefined" && typeof(localStorage.librarySearch) !== "undefined") {
                    var data = JSON.parse(localStorage.librarySearch);
                    log.debug("data=", data);
                    callback(data);
                }
*/
            },
            dropdownCssClass: "bigdrop", // apply css that makes the dropdown taller
            escapeMarkup: function (m) {
                return m;
            } // we do not want to escape markup since we are displaying html in results
        }).on("change", function (e) {
/*
                log.debug("selecting val=" + e.val + " choice=" + JSON.stringify(e.choice));
                if (typeof(Storage) !== "undefined") {
                    localStorage.librarySearch = JSON.stringify(e.added);
                }
*/
            });
    });
});
