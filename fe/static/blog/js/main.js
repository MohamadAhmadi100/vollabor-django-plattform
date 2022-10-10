$(document).ready(function () {

    var letWidth = $(window).width();

    $('.sm_sidebar1').click(function () {
        if (letWidth > 1024) {
            if ($('.sidebar_filter').hasClass('show')) {
                $('.sidebar_filter').removeClass('show');
                $('.content').removeClass('show');
            } else {
                $('.sidebar_filter').addClass('show');
                $('.content').addClass('show');
            }
        }else {
            $('.filter_right').click(function () {
                $('.sidebar_bg').addClass('active');
            })
        }

    })

    if ($('.carousel-indicators button').length < 2  ){
        $('.carousel-indicators button').addClass('d-none');
    }

    $(window).on('resize', function (event) {
        $('.sm_sidebar button').click(function () {
            var windowWidth = $(window).width();
            if (windowWidth > 968) {
                if ($('.sidebar_filter').hasClass('show')) {
                    $('.sidebar_filter').removeClass('show');
                    $('.content').removeClass('show');
                } else {
                    $('.sidebar_filter').addClass('show');
                    $('.content').addClass('show');
                }
            } else {

                $('.filter_right').click(function () {
                    $('.sidebar_bg').addClass('active');
                })
            }

        })

    });


    $('.sidebar_right > .clos').click(function () {
        $('.sidebar_bg').removeClass('active');
    })

    /*** sidebar dropdown ***/
    $('.sidebar_filter .item ').click(function () {
        if ($(this).find('i').hasClass('active')) {
            $(this).find('i').removeClass('active');
            $(this).find('ul').removeClass('active');

        } else {
            $(this).find('i').addClass('active');
            $(this).find('ul').addClass('active');
        }

    })
    $('.sidebar_right .item ').click(function () {
        console.log('ali');
        if ($(this).find('i').hasClass('active')) {
            $(this).find('i').removeClass('active');
            $(this).find('ul').removeClass('active');
        } else {
            $(this).find('i').addClass('active');
            $(this).find('ul').addClass('active');
        }

    })


    /*** modal ***/
    //$('.js-example-basic-multiple').select2();


})
