$(document).ready(function () {

    $(".default-option3").click(function () {
        $(this).parent().toggleClass("active");
    })
    $(".select-ul3 li label").click(function () {
        var currentele = $(this).html();
        $(".default-option3 li .option").html(currentele);
        $(this).parents(".select-wrap3").removeClass("active");
    });


    $(".default-option4").click(function () {
        $(this).parent().toggleClass("active");
    })
    $(".select-ul4 li label").click(function () {
        var currentele = $(this).html();
        $(".default-option4 li .option").html(currentele);
        $(this).parents(".select-wrap4").removeClass("active");
    });


    $(".default-option5").click(function () {
        $(this).parent().toggleClass("active");
    })
    $(".select-ul5 li label").click(function () {
        var currentele = $(this).html();
        $(".default-option5 li .option").html(currentele);
        $(this).parents(".select-wrap5").removeClass("active");
    });






    $('.sidebar-btn').click(function () {
        $('.ws-content-sidebar').toggleClass('ws-content-sidebar-toggle');
    });
    $('.sidebar-btn').click(function () {
        $(this).toggleClass('sidebar-btn-toggle');
    });

})

