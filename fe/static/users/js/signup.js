$(document).ready(function () {

    $(".navbar-link").click(function () {
        $(this).toggleClass("active2")
        $(this).siblings().removeClass("active2")
    });


    $('.inp1').focus(function () {
        $('.inp-box1 .inp-box-label').addClass('add-label');
    });
    $('.inp2').focus(function () {
        $('.inp-box2 .inp-box-label').addClass('add-label');
    });
    $('.inp3').focus(function () {
        $('.inp-box3 .inp-box-label').addClass('add-label');
    });
    $('.inp4').focus(function () {
        $('.inp-box4 .inp-box-label').addClass('add-label');
    });
    $('.inp5').focus(function () {
        $('.inp-box5 .inp-box-label').addClass('add-label');
    });
    $('.inp6').focus(function () {
        $('.inp-box6 .inp-box-label').addClass('add-label');
    });
    $('.inp7').focus(function () {
        $('.inp-box7 .inp-box-label').addClass('add-label');
    });
    $('.inp8').focus(function () {
        $('.inp-box8 .inp-box-label').addClass('add-label');
    });
    $('.inp9').focus(function () {
        $('.inp-box9 .inp-box-label').addClass('add-label');
    });
    $('.inp10').focus(function () {
        $('.inp-box10 .inp-box-label').addClass('add-label');
    });
    $('.inp11').focus(function () {
        $('.inp-box11 .inp-box-label').addClass('add-label');
    });


    $('.intern-check label').click(function () {
        $('.tick').toggleClass('tick-check');
    });


    $(function(){
        function rescaleCaptcha(){
          var width = $('.g-recaptcha').parent().width();
          var scale;
          if (width < 302) {
            scale = width / 302;
          } else{
            scale = 1.0; 
          }
      
          $('.g-recaptcha').css('transform', 'scale(' + scale + ')');
          $('.g-recaptcha').css('-webkit-transform', 'scale(' + scale + ')');
          $('.g-recaptcha').css('transform-origin', '0 0');
          $('.g-recaptcha').css('-webkit-transform-origin', '0 0');
        }
      
        rescaleCaptcha();
        $( window ).resize(function() { rescaleCaptcha(); });
      
      });


})
