$(document).ready(function () {
    $('.suggestion_box form .form-control').on('focus', function () {
        // $('.form-label').css({"color":"red"})
        $('.form-label').css({"font-weight": "normal"})
        let label = $(this.parentElement.children[0]);
        label.css({"font-weight": "bold"});
        console.log(label)
    });

    $('.btn_form').click(function (e) {
        e.preventDefault();
        console.log('fuck u')
    })
})