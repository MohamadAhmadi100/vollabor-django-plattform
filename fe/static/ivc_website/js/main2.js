/*es*/
//start of fade
$(function() {  
    var html = $('html');
    // Detections
    if (!("ontouchstart" in window)) {
      html.addClass("noTouch");
    }
    if ("ontouchstart" in window) {
      html.addClass("isTouch");
    }
    if ("ontouchstart" in window) {
      html.addClass("isTouch");
    }
    if (document.documentMode || /Edge/.test(navigator.userAgent)) {
      if (navigator.appVersion.indexOf("Trident") === -1) {
        html.addClass("isEDGE");
      } else {
        html.addClass("isIE isIE11");
      }
    }
    if (navigator.appVersion.indexOf("MSIE") !== -1) {
      html.addClass("isIE");
    }
    if (
      navigator.userAgent.indexOf("Safari") != -1 &&
      navigator.userAgent.indexOf("Chrome") == -1
    ) {
      html.addClass("isSafari");
    }
  
    // On Screen
  
    $.fn.isOnScreen = function() {
      var elementTop = $(this).offset().top,
        elementBottom = elementTop + $(this).outerHeight(),
        viewportTop = $(window).scrollTop(),
        viewportBottom = viewportTop + $(window).height();
      return elementBottom > viewportTop && elementTop < viewportBottom;
    };
  
    function detection() {
      for (var i = 0; i < items.length; i++) {
        var el = $(items[i]);
  
        if (el.isOnScreen()) {
          el.addClass("in-view");
        } else {
          el.removeClass("in-view");
        }
      }
    }
  
    var items = document.querySelectorAll(
      "*[data-animate-in], *[data-detect-viewport]"
    ),
      waiting = false,
      w = $(window);
  
    w.on("resize scroll", function() {
      if (waiting) {
        return;
      }
      waiting = true;
      detection();
  
      setTimeout(function() {
        waiting = false;
      }, 100);
    });
  
    $(document).ready(function() {
      setTimeout(function() {
        detection();
      }, 500);
  
      for (var i = 0; i < items.length; i++) {
        var d = 0,
          el = $(items[i]);
        if (items[i].getAttribute("data-animate-in-delay")) {
          d = items[i].getAttribute("data-animate-in-delay") / 1000 + "s";
        } else {
          d = 0;
        }
        el.css("transition-delay", d);
      }
      
     if( document.getElementById("des_plc")){
     document.getElementById("des_plc").innerText = truncateText('des_plc', 150);
     }
    
        if(document.getElementById("news_section")){
            var NewsCards = document.getElementById("news_section").querySelectorAll(".news_card"); 
            
            for (let i = 0; i < NewsCards.length; i++) {
                 NewsCards[i].addEventListener("click", function() {
                   var news_num = NewsCards[i].id;
                   var img_src = document.getElementById("news_img"+ news_num).src;
                   var title = document.getElementById("title"+ news_num).innerHTML;
                   var description = document.getElementById("news_des"+ news_num).value;
                   var NewsLink = document.getElementById("news_link"+ news_num).value;
                   //alert(description);
                   document.getElementById("img_plc").src = img_src;
                   document.getElementById("title_plc").innerHTML = title;
                   document.getElementById("des_plc").innerHTML = "";
                   document.getElementById("des_plc").innerHTML = description;
                   document.getElementById("des_plc").innerText = truncateText('des_plc', 150);
                   document.getElementById("MoreBtn").href = NewsLink;
                 });
            }
            
        }   
        
    });
    
 

function truncateText(id, maxLength) {
    
        var element = document.getElementById(id),
            truncated = element.innerText;
    
        if (truncated.length > maxLength) {
            truncated = truncated.substr(0,maxLength) + '...';
        }
        return truncated;
    
}   
    
    
    
    
  });
//end of fade
    
    
//start m
(function() {
  "use strict";

  /**
   * Easy selector helper function
   */
  const select = (el, all = false) => {
    el = el.trim()
    if (all) {
      return [...document.querySelectorAll(el)]
    } else {
      return document.querySelector(el)
    }
  }

  /**
   * Easy event listener function
   */
  const on = (type, el, listener, all = false) => {
    let selectEl = select(el, all)
    if (selectEl) {
      if (all) {
        selectEl.forEach(e => e.addEventListener(type, listener))
      } else {
        selectEl.addEventListener(type, listener)
      }
    }
  }

  /**
   * Easy on scroll event listener 
   */
  const onscroll = (el, listener) => {
    el.addEventListener('scroll', listener)
  }

  /**
   * Navbar links active state on scroll
   */
  let navbarlinks = select('#navbar .scrollto', true)
  const navbarlinksActive = () => {
    let position = window.scrollY + 200
    navbarlinks.forEach(navbarlink => {
      if (!navbarlink.hash) return
      let section = select(navbarlink.hash)
      if (!section) return
      if (position >= section.offsetTop && position <= (section.offsetTop + section.offsetHeight)) {
        navbarlink.classList.add('active')
      } else {
        navbarlink.classList.remove('active')
      }
    })
  }
  window.addEventListener('load', navbarlinksActive)
  onscroll(document, navbarlinksActive)

  /**
   * Scrolls to an element with header offset
   */
  const scrollto = (el) => {
    let header = select('#header')
    let offset = header.offsetHeight

    if (!header.classList.contains('header-scrolled')) {
      offset -= 16
    }

    let elementPos = select(el).offsetTop
    window.scrollTo({
      top: elementPos - offset,
      behavior: 'smooth'
    })
  }

  /**
   * Toggle .header-scrolled class to #header when page is scrolled
   */
  let selectHeader = select('#header')
  if (selectHeader) {
    const headerScrolled = () => {
      if (window.scrollY > 100) {
        selectHeader.classList.add('header-scrolled')
      } else {
        selectHeader.classList.remove('header-scrolled')
      }
    }
    window.addEventListener('load', headerScrolled)
    onscroll(document, headerScrolled)
  }

  /**
   * Back to top button
   */
  let backtotop = select('.back-to-top')
  if (backtotop) {
    const toggleBacktotop = () => {
      if (window.scrollY > 100) {
        backtotop.classList.add('active')
      } else {
        backtotop.classList.remove('active')
      }
    }
    window.addEventListener('load', toggleBacktotop)
    onscroll(document, toggleBacktotop)
  }

  /**
   * Mobile nav toggle
   */
  on('click', '.mobile-nav-toggle', function(e) {
    select('#navbar').classList.toggle('navbar-mobile')
    this.classList.toggle('bi-list')
    this.classList.toggle('bi-x')
  })

  /**
   * Mobile nav dropdowns activate
   */
  on('click', '.navbar .dropdown > a', function(e) {
    if (select('#navbar').classList.contains('navbar-mobile')) {
      e.preventDefault()
      this.nextElementSibling.classList.toggle('dropdown-active')
    }
  }, true)

  /**
   * Scrool with ofset on links with a class name .scrollto
   */
  on('click', '.scrollto', function(e) {
    if (select(this.hash)) {
      e.preventDefault()

      let navbar = select('#navbar')
      if (navbar.classList.contains('navbar-mobile')) {
        navbar.classList.remove('navbar-mobile')
        let navbarToggle = select('.mobile-nav-toggle')
        navbarToggle.classList.toggle('bi-list')
        navbarToggle.classList.toggle('bi-x')
      }
      scrollto(this.hash)
    }
  }, true)

  /**
   * Scroll with ofset on page load with hash links in the url
   */
  window.addEventListener('load', () => {
    if (window.location.hash) {
      if (select(window.location.hash)) {
        scrollto(window.location.hash)
      }
    }
  });

  /**
   * Preloader
   */
  let preloader = select('#preloader');
  if (preloader) {
    window.addEventListener('load', () => {
      preloader.remove()
    });
  }

  /**
   * Hero carousel indicators
   */
  let heroCarouselIndicators = select("#hero-carousel-indicators")
  let heroCarouselItems = select('#heroCarousel .carousel-item', true)

  heroCarouselItems.forEach((item, index) => {
    (index === 0) ?
    heroCarouselIndicators.innerHTML += "<li data-bs-target='#heroCarousel' data-bs-slide-to='" + index + "' class='active'></li>":
      heroCarouselIndicators.innerHTML += "<li data-bs-target='#heroCarousel' data-bs-slide-to='" + index + "'></li>"
  });

  /**
   * Porfolio isotope and filter
   */
  window.addEventListener('load', () => {
    let portfolioContainer = select('.portfolio-container');
    if (portfolioContainer) {
      let portfolioIsotope = new Isotope(portfolioContainer, {
        itemSelector: '.portfolio-item',
        layoutMode: 'fitRows'
      });

      let portfolioFilters = select('#portfolio-flters li', true);

      on('click', '#portfolio-flters li', function(e) {
        e.preventDefault();
        portfolioFilters.forEach(function(el) {
          el.classList.remove('filter-active');
        });
        this.classList.add('filter-active');

        portfolioIsotope.arrange({
          filter: this.getAttribute('data-filter')
        });
      }, true);
    }

  });

  /**
   * Initiate portfolio lightbox 
   */
  const portfolioLightbox = GLightbox({
    selector: '.portfolio-lightbox'
  });

  /**
   * Testimonials slider
   */
  new Swiper('.testimonials-slider', {
    speed: 600,
    loop: true,
    autoplay: {
      delay: 5000,
      disableOnInteraction: false
    },
    slidesPerView: 'auto',
    pagination: {
      el: '.swiper-pagination',
      type: 'bullets',
      clickable: true
    }
  });

})()
//end m



//start tp
    $('.project_sections .items .item').click(function (e) {
        $('.project_sections .items .item').removeClass('active');
        $(this).addClass('active');
    })

    $('.project_sections .items .item').click(function (e) {
        $('.project_sections .items .item').removeClass('active');
        $(this).addClass('active');
    })


//end tp



var prevScrollpos = window.pageYOffset;

/* Get the header element and it's position */
var headerDiv = document.querySelector("header");
var headerBottom = headerDiv.offsetTop + headerDiv.offsetHeight;

window.onscroll = function() {
  var currentScrollPos = window.pageYOffset;

  /* if we're scrolling up, or we haven't passed the header,
     show the header at the top */
  if (prevScrollpos > currentScrollPos  || currentScrollPos < headerBottom){  
      headerDiv.style.top = "0";
  }
  else{
      /* otherwise we're scrolling down & have passed the header so hide it */
      headerDiv.style.top = "-7.2rem";
  } 

  prevScrollpos = currentScrollPos;
}










 $(document).ready(function(){
	 
	 


});



$(window).on('resize', function(event){
	
    // Do stuff here
	var windowWidth = $(window).width();
	//alert(windowWidth);
	if(windowWidth < 768 ){
		$( "#LogDiv" ).insertBefore( $( "#collapsibleNavbar" ) );

	}else{
		$( "#collapsibleNavbar" ).insertBefore( $( "#LogDiv" ) );
	}
	
	
	
});


		

