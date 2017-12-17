$(function(){
    $('html').keyup(function(e){
        switch(e.which){
            case 37: // Key[←]
                $("#prev").click();
                break;
 
            case 39: // Key[→]
                $("#next").click();
                break;
        }
    });
});