$(document).ready(function () {

    $('.project_sections .items .item').click(function (e) {
        $('.project_sections .items .item').removeClass('active');
        $(this).addClass('active');
    })

    $('.project_sections .items .item').click(function (e) {
        $('.project_sections .items .item').removeClass('active');
        $(this).addClass('active');
    })


    /*** owl carousel ***/

    $('#project_item').owlCarousel({
        loop:true,
        margin:10,
        nav:true,
        navText: [
        '<i class="fa fa-angle-left" aria-hidden="true"></i>',
        '<i class="fa fa-angle-right" aria-hidden="true"></i>'
    ],
        responsiveClass:true,
        autoplay:true,
        autoplayTimeout:5000,
        autoplayHoverPause:true,
        autoplaySpeed:5000,
        responsive:{
            0:{
                items:1,
                nav:true
            },
            700:{
                items:2,
                nav:false
            },
            1000:{
                items:3,
                nav:true,
                loop:true
            }
        }
    })
    $('#project_item2').owlCarousel({
      loop:true,
      margin:10,
      
      responsiveClass:true,
      autoplay:true,
      autoplayTimeout:5000,
      autoplayHoverPause:true,
      autoplaySpeed:5000,
      responsive:{
          0:{
              items:1,
              nav:true
          },
          700:{
              items:2,
              nav:false
          },
          1000:{
              items:3,
              nav:true,
              loop:false
          }
      }
  })
    $('#project_item3').owlCarousel({
      loop:true,
      margin:10,
      
      responsiveClass:true,
      autoplay:true,
      autoplayTimeout:5000,
      autoplayHoverPause:true,
      autoplaySpeed:5000,
      responsive:{
          0:{
              items:1,
              nav:true
          },
          700:{
              items:2,
              nav:false
          },
          1000:{
              items:3,
              nav:true,
              loop:false
          }
      }
  })
    $('.speak_item').owlCarousel({
        loop: true,
        
        responsiveClass:true,
        autoplay: true,
        center: true,
        nav: true,
        autoplayTimeout:5000,
        autoplayHoverPause:true,
        autoplaySpeed:5000,
        responsive:{
            0:{
                items:1,
                nav:true

            },
            700:{
                items:2,
                nav:false
            },
            1000:{
                items:3,
                nav:true,
                loop:true
            }
        }
    })
    $('.workshop_item').owlCarousel({
        loop:true,
        margin:10,
        
        nav:true,
        responsiveClass:true,
        autoplay:true,
        autoplayTimeout:10000,
        autoplayHoverPause:true,
        autoplaySpeed:5000,
        responsive:{
            0:{
                items:1,
                nav:true
            },
            700:{
                items:1,
                nav:true
            },
            1000:{
                items:1,
                nav:true,
                loop:true
            }
        }
    })
    
    $('.news_item').owlCarousel({
        loop:true,
        margin:10,
        nav:true,
        navText: [
        '<i class="fa fa-angle-left" aria-hidden="true"></i>',
        '<i class="fa fa-angle-right" aria-hidden="true"></i>'
    ],
        responsiveClass:true,
        autoplay:true,
        autoplayTimeout:5000,
        autoplayHoverPause:true,
        autoplaySpeed:5000,
        responsive:{
            0:{
                items:1,
                nav:true
            },
            700:{
                items:2,
                nav:false
            },
            1000:{
                items:3,
                nav:true,
                loop:true
            }
        }
    })
   
    $('#video').owlCarousel({
        loop:true,
        margin:10,
        
        responsiveClass:true,
        autoplay:true,
        autoplayTimeout:5000,
        autoplayHoverPause:true,
        autoplaySpeed:5000,
        responsive:{
            0:{
                items:1,
                nav:true
            },
            700:{
                items:2,
                nav:false
            },
            1000:{
                items:3,
                nav:true,
                
            }
        }
    })

    /*** video play ***/
    $('.play').click(function () {
        $('.play').addClass('d-none');
        $('.vide_if').removeClass('d-none');
    })


})
