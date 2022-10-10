$(document).ready(function () {

    $(".default-option1").click(function () {
        $(this).parent().toggleClass("active");
    })
    $(".select-ul1 a").click(function () {
        $(this).parents(".select-wrap1").removeClass("active");
        $(this).addClass("active2");
        $(this).siblings().removeClass("active2");
    })


    $(".default-option2").click(function () {
        $(this).parent().toggleClass("active");
    })
    $(".select-ul2 a").click(function () {
        $(this).parents(".select-wrap2").removeClass("active");
        $(this).addClass("active2");
        $(this).siblings().removeClass("active2");
    })


    var $username = document.querySelector('.username')

    $username.addEventListener('blur', formValidation)

    function formValidation(e) {
        if (e.target.value.length > 0) {
            e.target.style.border = '1px solid green'
        } else {
            e.target.style.border = '1px solid red'
        }
    }

    var $price = document.querySelector('.price')

    $price.addEventListener('blur', formValidation)

    function formValidation(e) {
        if (e.target.value.length > 0) {
            e.target.style.border = '1px solid green'
        } else {
            e.target.style.border = '1px solid red'
        }
    }

  /*  var $time = document.querySelector('.time')

    $time.addEventListener('blur', formValidation)

    function formValidation(e) {
        if (e.target.value.length > 0) {
            e.target.style.border = '1px solid green'
        } else {
            e.target.style.border = '1px solid red'
        }
    }

    var $date = document.querySelector('.date')

    $date.addEventListener('blur', formValidation)

    function formValidation(e) {
        if (e.target.value.length > 0) {
            e.target.style.border = '1px solid green'
        } else {
            e.target.style.border = '1px solid red'
        }
    }

    var $duration = document.querySelector('.duration')

    $duration.addEventListener('blur', formValidation)

    function formValidation(e) {
        if (e.target.value.length > 0) {
            e.target.style.border = '1px solid green'
        } else {
            e.target.style.border = '1px solid red'
        }
    }*/

   // var $file = document.querySelector('.file')

   // $file.addEventListener('blur', formValidation)

    function formValidation(e) {
        if (e.target.value.length > 0) {
            e.target.style.border = '1px solid green'
        } else {
            e.target.style.border = '1px solid red'
        }
    }

    var $location = document.querySelector('.location')

    $location.addEventListener('blur', formValidation)

    function formValidation(e) {
        if (e.target.value.length > 0) {
            e.target.style.border = '1px solid green'
        } else {
            e.target.style.border = '1px solid red'
        }
    }

    var $description = document.querySelector('.description')

    $description.addEventListener('blur', formValidation)

    function formValidation(e) {
        if (e.target.value.length > 0) {
            e.target.style.border = '1px solid green'
        } else {
            e.target.style.border = '1px solid red'
        }
    }

    // var $description2 = document.querySelector('.description2')

    // $description2.addEventListener('blur', formValidation)

    // function formValidation(e) {
    //     if (e.target.value.length > 0) {
    //         e.target.style.border = '1px solid green'
    //     } else {
    //         e.target.style.border = '1px solid red'
    //     }
    // }

    //var $guaranted = document.querySelector('.guaranted')

   // $guaranted.addEventListener('blur', formValidation)

    //function formValidation(e) {
      //  if (e.target.value.length > 0) {
    //        e.target.style.border = '1px solid green'
     //   } else {
      //      e.target.style.border = '1px solid red'
    //    }
//    }

    // var $wsnumber = document.querySelector('.workshop-number')

    // $wsnumber.addEventListener('blur', formValidation)

    // function formValidation(e) {
    //     if (e.target.value > 0) {
    //         e.target.style.border = '1px solid green'
    //     } else {
    //         e.target.style.border = '1px solid red'
    //     }
    // }

    // var $wswithus = document.querySelector('.work-whith-us')

    // $wswithus.addEventListener('blur', formValidation)

    // function formValidation(e) {
    //     if (e.target.value > 0) {
    //         e.target.style.border = '1px solid green'
    //     } else {
    //         e.target.style.border = '1px solid red'
    //     }
    // }

    // var $years = document.querySelector('.years')

    // $years.addEventListener('blur', formValidation)

    // function formValidation(e) {
    //     if (e.target.value.html.length > 0) {
    //         e.target.style.border = '1px solid green'
    //     } else {
    //         e.target.style.border = '1px solid red'
    //     }
    // }

   /* const $btnNotification = document.querySelector('#btn-notification')

    $btnNotification.addEventListener('click', e => {
        e.preventDefault()

        createNotification()
    })

    function createNotification() {

        if ($username.value.length > 0 && $price.value.length > 0 && $time.value.length > 0 && $guaranted.value.length > 0 && $date.value.length > 0 && $duration.value.length > 0 && $file.value.length > 0 && $description.value.length > 0 && $location.value.length > 0 && $description2.value.length > 0) {
            $('#successalert').fadeIn(500);
            $('#successalert').fadeOut(10000);
            $('#eroralert').fadeOut(0);
        } else {
            $('#eroralert').fadeIn(500);
            $('#eroralert').fadeOut(10000);
            $('#successalert').fadeOut(0);
        }
    }*/

    /*$('#inputFile').on('click', function () {

        $('#inputFile').change(function (e) {

            $('.dragdrop').empty().html();
            var fileName = e.target.files[0].name;
            $('.dragdrop').html(fileName);

        });

    })*/

    $('#upload').on('click', function () {

        $('#upload').change(function (e) {

            $('.label').empty().html();
            var fileName = e.target.files[0].name;
            $('.label').html( fileName );
        });

    })





})

