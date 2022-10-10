$(document).ready(function () {

    $(".status_change .dropdown-item").click(function () {
        var getStatusText = $(this).text();
        $('.dropdown-item').removeClass('active')
        $(this).addClass('active');
        $(this).closest(".status_dropdown").find(".status__btn").text(getStatusText);
        var generateStatusClass = `${$(this).attr('data-class')}-status`
        $(this).closest(".status_dropdown").attr("data-color", `${generateStatusClass}`);
    })

    $(".status_topic_change .dropdown-item").click(function () {
        $('.status_topic_change .dropdown-item').removeClass('active');
        $(this).addClass('active');
    })

    // var count = $('.post').length;
    // $('.count_all').html(count);
    // $('.count_now').html(1);
    // let number = 1 ;
    // let percent = 100 / count ;

    $(window).scroll(function () {
        var windowpos = $(window).scrollTop();


        // Scrollbar progression
        // pixels scrolled from top
        var scrollTop = $(window).scrollTop(),
            // document height
            docHeight = $(document).height(),
            // window height
            winHeight = $(window).height(),
            // percent of document scrolled
            scrollPercent = scrollTop / (docHeight - winHeight),
            scrollPercentRounded = Math.round(scrollPercent * 100);



    //     console.log(percent);
    //     let per = percent * number;
    //     if (scrollPercentRounded > per){
    //         number += 1
    //         console.log(number);
    //         $('.count_now').html(number);
    //     }else {
    //         number -= 1
    //          per = percent * number;
    //         $('.count_now').html(number);

    //     }


        // incement progress bar as user scrolls
        $(".progress-bar--increment").css("width", scrollPercentRounded + "%");
    });


    $(document).ready(function() {
        const win = $(window);
        const doc = $(document);
        const progressBar = $('.progress-bar');
        const progressLabel = $('.count_comment');
        const setValue = () => win.scrollTop();
        const setMax = () => doc.height() - win.height();
        const setPercent = () => Math.round(win.scrollTop() / (doc.height() - win.height()) * 100);
        
        progressLabel.text(setPercent() + '%');
        progressBar.attr({ value: setValue(), max: setMax() });
      
        doc.on('scroll', () => {
          progressLabel.text(setPercent() + '%');
          progressBar.attr({ value: setValue() });
        });
        
        win.on('resize', () => {
          progressLabel.text(setPercent() + '%');
          progressBar.attr({ value: setValue(), max: setMax() });
        })
      });


})
