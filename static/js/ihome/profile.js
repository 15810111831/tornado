function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    $.get("/api/profile", function(data){
        if ("4101" == data.errorcode) {
            location.href = "/login.html";
        }
        else if ("0" == data.errorcode) {
            $("#user-name").val(data.data.name);
            if (data.data.avatar) {
                $("#user-avatar").attr("src", data.data.avatar);
            }
        }
    })
    $("#form-avatar").submit(function (e) {
        // 组织浏览器对于表单的默认行为
        e.preventDefault();
        $('.image_uploading').fadeIn('fast');
        var options = {
            url: "/api/profile/avatar",
            method: "post",
            dataType: "json",
            headers: {
                "X-XSRFTOKEN": getCookie("_xsrf")
            },
            success: function (data) {
                if ("0" == data.errorcode) {
                    $('.image_uploading').fadeOut('fast');
                    $("#user-avatar").attr("src", data.url)
                } else if ("4101" == data.errorcode) {
                    location.href = "/login.html";
                }
            }
        };
        $(this).ajaxSubmit(options);
    })
    $("#form-name").submit(function(e){
        e.preventDefault();
        var data = {};
        $(this).serializeArray().map(function(x){data[x.name] = x.value;});
        var jsonData = JSON.stringify(data);
        $.ajax({
            url:"/api/profile/name",
            type:"POST",
            data: jsonData,
            contentType: "application/json",
            dataType: "json",
            headers:{
                "X-XSRFTOKEN":getCookie("_xsrf"),
            },
            success: function (data) {
                if ("0" == data.errorcode) {
                    $(".error-msg").hide();
                    showSuccessMsg(); // 展示保存成功的页面效果
                } else if ("4001" == data.errorcode) {
                    $(".error-msg").show();
                } else if ("4101" == data.errorcode) { // 4101代表用户未登录，强制跳转到登录页面
                    location.href = "/login.html";
                }
            }
        });
    })
})

