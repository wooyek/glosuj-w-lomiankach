/**
 * Copyright 2013 Janusz Skonieczny
 */

$(function () {
    var b = {expires: 365};
    $("a.switch-login").click(function (d) {
        d.preventDefault();
        d = $(this).attr("href").slice(1);
        $(".login-box, .registration-box").attr("data-method", d);
        $.cookie("login-method", d, b)
    });
    $("#openid-form #providers a").click(function (e) {
        var provider = $(this);
        $("#openid-form #providers a").removeClass("selected");
        provider.addClass("selected");
        $("#openid-form .provider").removeClass("selected");
        e.preventDefault();
        if (provider.data("url").indexOf("{id}") === -1) {
            $("#openid-form .buttons").removeClass("selected");
            $("#openid-form").trigger("submit")
        } else {
            $.cookie("openid-provider", provider.attr("href"), b);
            $("#openid-form .buttons").addClass("selected")
        }
        $(provider.attr("href")).addClass("selected").find("input").focus()
    });
    $("#openid-form").submit(function () {
        var url = $("#openid-form #providers .selected").data("url");
        var id = $("#openid-form .provider.selected input").val();
        $("#openid_provider").val(url.replace("{id}", id));
        $("#openid_username").val(id)
    });
});
