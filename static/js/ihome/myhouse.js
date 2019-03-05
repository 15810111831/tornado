$(document).ready(function(){
    $.get("/api/profile/auth", function(data){
        if ("4101" == data.errorcode) {
            location.href = "/login.html";
        } else if ("0" == data.errorcode) {
            if ("" == data.data.real_name || "" == data.data.id_card || null == data.data.real_name || null == data.data.id_card) {
                $(".auth-warn").show();
                return;
            }
            $.get("/api/house/my", function(result){
                $("#houses-list").html(template("houses-list-tmpl", {houses:result.houses}));
            });
        }
    });
})