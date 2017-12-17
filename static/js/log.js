jQuery(function($){
    $("form").submit(function(event){
        event.preventDefault();
        var $form = $(this);
        $.ajax({
            url: '/getlog',
            type: 'POST',
            data: $form.serialize(),
            success:function(resultdata) {
                $("#logdata").html(resultdata);
            },
            error: function(error) {
                alert('取得に失敗しました');
            }
        });
    });
});