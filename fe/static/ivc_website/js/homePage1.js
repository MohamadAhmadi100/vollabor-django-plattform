
$(document).on("scroll", function(){
		if
      ($(document).scrollTop() > 86){
		  $("#banner").addClass("shrink");
		}
		else
		{
			$("#banner").removeClass("shrink");
			
		}
		
	
	
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
});
	



	
	
	
	
$('#myCarousel').carousel({
            interval: false
        });

        //scroll slides on swipe for touch enabled devices

        $("#myCarousel").on("touchstart", function(event){

            var yClick = event.originalEvent.touches[0].pageY;
            $(this).one("touchmove", function(event){

                var yMove = event.originalEvent.touches[0].pageY;
                if( Math.floor(yClick - yMove) > 1 ){
                    $(".carousel").carousel('next');
                }
                else if( Math.floor(yClick - yMove) < -1 ){
                    $(".carousel").carousel('prev');
                }
            });
            $(".carousel").on("touchend", function(){
                $(this).off("touchmove");
            });
        });
		
		
 $(document).ready(function(){
	 
	 var researchBtn = document.getElementById("researchBtn"); 
		researchBtn.addEventListener('click',function(){
			document.getElementById("researchDiv").style.borderRightColor = "darkorange";
			document.getElementById("competitionDiv").style.borderRightColor = "silver";
			document.getElementById("industrialDiv").style.borderRightColor = "silver";
			
			
			$("#researchCards").removeClass("d-none");
			$("#competitionCards").addClass("d-none");
			$("#industrialCards").addClass("d-none");
			
		});
		
	 var competitionBtn = document.getElementById("competitionBtn"); 
		competitionBtn.addEventListener('click',function(){
			document.getElementById("researchDiv").style.borderRightColor = "silver";
			document.getElementById("competitionDiv").style.borderRightColor = "darkorange";
			document.getElementById("industrialDiv").style.borderRightColor = "silver";
			
			
			$("#competitionCards").removeClass("d-none");
			$("#researchCards").addClass("d-none");
			$("#industrialCards").addClass("d-none");
			
		});
		
	var industrialBtn = document.getElementById("industrialBtn"); 
		industrialBtn.addEventListener('click',function(){
			document.getElementById("researchDiv").style.borderRightColor = "silver";
			document.getElementById("competitionDiv").style.borderRightColor = "silver";
			document.getElementById("industrialDiv").style.borderRightColor = "darkorange";
			
			
			$("#industrialCards").removeClass("d-none");
			$("#researchCards").addClass("d-none");
			$("#competitionCards").addClass("d-none");
			
		});
		
		
	var suggestionText = document.getElementById("suggestionTitle"); 
		suggestionText.addEventListener('click',function(){
			document.getElementById("suggestionBoxDiv").style.display = "block";
						
		});
		
		
		
///////////////////////////News Slides////////////////////////////////////
/*	var itemsMainDiv = ('.MultiCarousel');
    var itemsDiv = ('.MultiCarousel-inner');
    var itemWidth = "";

    $('.leftLst, .rightLst').click(function () {
        var condition = $(this).hasClass("leftLst");
        if (condition)
            click(0, this);
        else
            click(1, this)
    });

    ResCarouselSize();




    $(window).resize(function () {
        ResCarouselSize();
    });

    //this function define the size of the items
    function ResCarouselSize() {
        var incno = 0;
        var dataItems = ("data-items");
        var itemClass = ('.item');
        var id = 0;
        var btnParentSb = '';
        var itemsSplit = '';
        var sampwidth = $(itemsMainDiv).width();
        var bodyWidth = $('body').width();
        $(itemsDiv).each(function () {
            id = id + 1;
            var itemNumbers = $(this).find(itemClass).length;
            btnParentSb = $(this).parent().attr(dataItems);
            itemsSplit = btnParentSb.split(',');
            $(this).parent().attr("id", "MultiCarousel" + id);


            if (bodyWidth >= 1200) {
                incno = itemsSplit[3];
                itemWidth = sampwidth / incno;
            }
            else if (bodyWidth >= 992) {
                incno = itemsSplit[2];
                itemWidth = sampwidth / incno;
            }
            else if (bodyWidth >= 768) {
                incno = itemsSplit[1];
                itemWidth = sampwidth / incno;
            }
            else {
                incno = itemsSplit[0];
                itemWidth = sampwidth / incno;
            }
            $(this).css({ 'transform': 'translateX(0px)', 'width': itemWidth * itemNumbers });
            $(this).find(itemClass).each(function () {
                $(this).outerWidth(itemWidth);
            });

            $(".leftLst").addClass("over");
            $(".rightLst").removeClass("over");

        });
    }


    //this function used to move the items
    function ResCarousel(e, el, s) {
        var leftBtn = ('.leftLst');
        var rightBtn = ('.rightLst');
        var translateXval = '';
        var divStyle = $(el + ' ' + itemsDiv).css('transform');
        var values = divStyle.match(/-?[\d\.]+/g);
        var xds = Math.abs(values[4]);
        if (e == 0) {
            translateXval = parseInt(xds) - parseInt(itemWidth * s);
            $(el + ' ' + rightBtn).removeClass("over");

            if (translateXval <= itemWidth / 2) {
                translateXval = 0;
                $(el + ' ' + leftBtn).addClass("over");
            }
        }
        else if (e == 1) {
            var itemsCondition = $(el).find(itemsDiv).width() - $(el).width();
            translateXval = parseInt(xds) + parseInt(itemWidth * s);
            $(el + ' ' + leftBtn).removeClass("over");

            if (translateXval >= itemsCondition - itemWidth / 2) {
                translateXval = itemsCondition;
                $(el + ' ' + rightBtn).addClass("over");
            }
        }
        $(el + ' ' + itemsDiv).css('transform', 'translateX(' + -translateXval + 'px)');
    }

    //It is used to get some elements from btn
    function click(ell, ee) {
        var Parent = "#" + $(ee).parent().attr("id");
        var slide = $(Parent).attr("data-slide");
        ResCarousel(ell, Parent, slide);
    }*/


//////////////////////////////////////////////////////////	 

$num = $('.my-card').length;

$even = $num / 2;

$odd = ($num + 1) / 2;

 

if ($num % 2 == 0) {

  $('.my-card:nth-child(' + $even +')').addClass('active');

  $('.my-card:nth-child(' + $even +')').prev().addClass('prev');

  $('.my-card:nth-child(' + $even +')').next().addClass('next');

}else {

  $('.my-card:nth-child(' + $odd +')').addClass('active');

  $('.my-card:nth-child(' + $odd +')').prev().addClass('prev');

  $('.my-card:nth-child(' + $odd +')').next().addClass('next');

}

 

$('.my-card').click(function() {

  $slide = $('.active').width();

  //console.log($('.active').position().left);

   

  if ($(this).hasClass('next')) {

    $('.card-carousel').stop(false,true).animate({left:'-=' + $slide});

  }else if ($(this).hasClass('prev')) {

    $('.card-carousel').stop(false,true).animate({left:'+=' + $slide});

  }

   

  $(this).removeClass('prev next');

  $(this).siblings().removeClass('prev active next');

   

  $(this).addClass('active');

  $(this).prev().addClass('prev');

  $(this).next().addClass('next');

});

 

 

// Keyboard nav

$('html body').keydown(function(e) {

  if (e.keyCode == 37) {// left

    $('.active').prev().trigger('click');

  }

  else if (e.keyCode == 39) {// right

    $('.active').next().trigger('click');

  }

});







///////////////////////////////////////////////////////////
 })
 
 

		