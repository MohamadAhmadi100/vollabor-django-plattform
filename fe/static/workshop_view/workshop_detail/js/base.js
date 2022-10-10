
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


		