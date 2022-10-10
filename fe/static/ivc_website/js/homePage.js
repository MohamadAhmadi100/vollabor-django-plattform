
window.onresize = doALoadOfStuff;

function doALoadOfStuff() {
    //var windowWidth = $(window).width();
	let windowWidth = screen.width;
	//alert(windowWidth);
	var LogDiv = document.getElementById("LogDiv");
	var collapsDiv = document.getElementById("collapsibleNavbar"); 
	var mainDiv = document.getElementById("mainDiv"); 
	if(windowWidth < 767 ){
		mainDiv.insertBefore(LogDiv, collapsDiv); 
		//$( "#LogDiv" ).insertBefore( $( "#collapsibleNavbar" ) );
		//var togBtn = document.getElementById("togBtn");
		//togBtn.addEventListener('click',function(){
		//	$("#collapsibleNavbar").addClass("shrink");
		//});
	}else{
		mainDiv.insertBefore(collapsDiv, LogDiv); 
		//$( "#collapsibleNavbar" ).insertBefore( $( "#LogDiv" ) );
	}
}
		
		





/*$(window).on('resize', function(event){
	
    
		
	
	
    });*/




$(document).on("scroll", function(){
		if
      ($(document).scrollTop() > 86){
		  $("#banner").addClass("shrink");
		}
		else
		{
			$("#banner").removeClass("shrink");
			
		}
		

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
	let windowWidth = screen.width;
	var togBtn = document.getElementById("togBtn");
	togBtn.addEventListener('click',function(){
		if(windowWidth < 767 ){
			$("#collapsibleNavbar").addClass("shrink");
		}else{
			$("#collapsibleNavbar").removeClass("shrink");
		}
	});
	
	 
	 
/*	 var researchBtn = document.getElementById("researchBtn"); 
		researchBtn.addEventListener('click',function(){
			document.getElementById("researchDiv").style.borderBottomColor = "darkorange";
			document.getElementById("competitionDiv").style.borderBottomColor = "silver";
			document.getElementById("industrialDiv").style.borderBottomColor = "silver";
			
			
			$("#researchCards").removeClass("d-none");
			$("#competitionCards").addClass("d-none");
			$("#industrialCards").addClass("d-none");
			
		});
		
	 var competitionBtn = document.getElementById("competitionBtn"); 
		competitionBtn.addEventListener('click',function(){
			document.getElementById("researchDiv").style.borderBottomColor = "silver";
			document.getElementById("competitionDiv").style.borderBottomColor = "darkorange";
			document.getElementById("industrialDiv").style.borderBottomColor = "silver";
			
			
			$("#competitionCards").removeClass("d-none");
			$("#researchCards").addClass("d-none");
			$("#industrialCards").addClass("d-none");
			
		});
		
	var industrialBtn = document.getElementById("industrialBtn"); 
		industrialBtn.addEventListener('click',function(){
			document.getElementById("researchDiv").style.borderBottomColor = "silver";
			document.getElementById("competitionDiv").style.borderBottomColor = "silver";
			document.getElementById("industrialDiv").style.borderBottomColor = "darkorange";
			
			
			$("#industrialCards").removeClass("d-none");
			$("#researchCards").addClass("d-none");
			$("#competitionCards").addClass("d-none");
			
		});*/
		
	
/*	var WSBtn = document.getElementById("WSBtn"); 
		WSBtn.addEventListener('click',function(){
			document.getElementById("WSDiv").style.borderBottomColor = "darkorange";
			document.getElementById("CourseDiv").style.borderBottomColor = "silver";
						
			$("#WSCards").removeClass("d-none");
			$("#CourseCards").addClass("d-none");
			
			
		});
		
	 var CourseBtn = document.getElementById("CourseBtn"); 
		CourseBtn.addEventListener('click',function(){
			document.getElementById("WSDiv").style.borderBottomColor = "silver";
			document.getElementById("CourseDiv").style.borderBottomColor = "darkorange";
			
			
			
			$("#CourseCards").removeClass("d-none");
			$("#WSCards").addClass("d-none");
			
			
		});*/








	
	var suggestionText = document.getElementById("suggestionTitle"); 
		suggestionText.addEventListener('click',function(){
		    if(document.getElementById("suggestionBoxDiv").style.display == "none"){
				document.getElementById("suggestionBoxDiv").style.display = "block";
			}else{
				document.getElementById("suggestionBoxDiv").style.display = "none";
			}
			
			
						
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



///////////////////////////////////////////////////////////


if ( $('.owl-2').length > 0 ) {
        $('.owl-2').owlCarousel({
            center: false,
            items: 1,
            loop: true,
            stagePadding: 0,
            margin: 20,
            smartSpeed: 1000,
            autoplay: true,
            nav: true,
            dots: true,
            pauseOnHover: false,
            responsive:{
                600:{
                    margin: 20,
                    nav: true,
                  items: 2
                },
                1000:{
                    margin: 20,
                    stagePadding: 0,
                    nav: true,
                  items: 3
                }
            }
        });            
    }










 })
 
 

		