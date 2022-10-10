$(document).ready(function () {

    $(".navbar-link").click(function () {
        $(this).toggleClass("active2")
        $(this).siblings().removeClass("active2")
    });

    $('#country').click(function() {

        $(".select-label").addClass("iranopt2");

    });

    // $('#country').change(function() {
    //     var $selectedoption = $(this).find(":selected").text();
    //     if ($selectedoption == "Iran") {
    //         $("#opt").addClass("iranopt");
    //       } else {};

    // });

    $('#country').change(function() {
        var $selectedoption = $(this).find(":selected").text();
        if ($selectedoption == "Iran") {
            $(".payment-info-head-text").addClass("payment-text-irn");
          } else {
            $(".payment-info-head-text").removeClass("payment-text-irn");
          };

    });


})
