/*
 * jQuery.upload 
 *
 * Copyright jianjun.wang
 *
 */

;(function($) {
    $.upload = function(options) {
        var defaults = {
            url: "",
            wrapper: ".upload-wrapper",
            fileName: "file"
        }

        var endOptions = $.extend(defaults, options);

        init(endOptions)

        return this;
    };

    function init(data) {
        var options = data,
            wrappers = $( options.wrapper );

        var upBtns = wrappers.find(".upload-btn");

        //给上传按钮追加input=file
        upBtns.each(function(){

            var upBtn = $(this);

            var eleFile = $([
              '<input class="upload-file" type="file" name="'+ options.fileName +'"'
              ,(options.multiple ? ' multiple' : '') 
              ,'>'
            ].join('')),

            next = upBtn.next();

            if( next.hasClass("upload-file") ){
                next.remove();
            }

            upBtn.after( eleFile );
        });

        wrappers.find(".upload-delete").click(function(){
            $(this).parent().find("img").remove();                           
            $(this).parent().find("input").attr("value", "");
            $(this).remove();
        });

        //给上传按钮增加click事件，弹出文件选择框
        upBtns.click(function(){
            $(this).next().click();
        });

        var inpts = wrappers.find(".upload-file");
        inpts.on("change", function(){
            var me = $(this), 
                data = me.prev().attr('upload-data'),
                value = me.get(0).value,
                file = me.get(0).files[0];

            //校验文件格式            
            if(value == "") return;
      
            if(data){
                try{
                    data = new Function('return '+ data)();
                    data = $.extend({size: 0, exts: ""}, options, data)
                        
                } catch(e){
                  
                }
            }

            switch( data.accept ){
              case 'video': //视频文件
                if(!RegExp('\\w\\.('+ (data.exts || 'avi|mp4|wma|rmvb|rm|flash|3gp|flv') +')$', 'i').test(escape(value))){
                  showModalAlert('选择的视频中包含不支持的格式');
                  return me.get(0).value = 0;
                }
              break;
              case 'audio': //音频文件
                if(!RegExp('\\w\\.('+ (data.exts || 'mp3|wav|mid') +')$', 'i').test(escape(value))){
                  showModalAlert('选择的音频中包含不支持的格式');
                  return me.get(0).value = 0;
                }
              break;
              default: //图片文件
                if(!RegExp('\\w\\.('+ (data.exts || 'jpg|png|gif|bmp|jpeg$') +')', 'i').test(escape(value))){
                  showModalAlert('选择的图片中包含不支持的格式');
                  return me.get(0).value = 0;
                }
              break;
            }

            //检验文件大小
            if(data.size > 0 && !(isIE() && IEVersion() < 10)){
                
              var limitSize;
              
                if(file.size > 1024*data.size){
                  var size = data.size/1024;
                  size = size >= 1 ? (size.toFixed(2) + 'MB') : data.size + 'KB'
                  me.attr("value", "");
                  limitSize = size;
                }
              
              if(limitSize) {
                showModalAlert('文件不能超过'+ limitSize);
                return ;
              }
            }

            var fd = new FormData();
            fd.append("upload", 1);
            //fd.append("title", data.title);
            fd.append("width", data.width);
            fd.append("height", data.height);
            fd.append("file", file);

            var wrapper = $(this).parent();

            $.ajax({
                url: data.url,
                type: "POST",
                processData: false,
                contentType: false,
                data: fd,
                success: function( res ) {
                    //如果上传失败
                    if(typeof res !== 'object'){
                        try {
                          res = JSON.parse(res);
                        } catch(e){
                          res = {};
                          showModalAlert('请对上传接口返回有效JSON');
                          return false;
                        }
                    }

                    if( res.code == 0 ){
                    	 //上传成功
                        var img = wrapper.find(".upload-thumbnail")
                        if( img.length > 0){
                            img.attr("src", res.url);
                        }else{
                            img = $('<img  class="upload-thumbnail" style="width: 100%; padding-bottom: 10px" src="'+ res.url +'"/>');
                            wrapper.prepend(img);
                        }
                    
                        wrapper.prepend(img);

                        var del = $('<span class="upload-delete"></span>')
                        wrapper.prepend(del);
                        wrapper.find(".upload-delete").click(function(){
                            $(this).parent().find("img").remove();                           
                            $(this).parent().find("input").attr("value", "");
                            $(this).remove();
                        })

                        wrapper.find("input").attr("value", res.url);
                        
                    } else {
                       showModalAlert( res.msg );
                       return false;
                    }                    
                }
            });
        })
    }



    function isIE(){
        var userAgent = navigator.userAgent; //取得浏览器的userAgent字符串  
        var isIE = userAgent.indexOf("compatible") > -1 && userAgent.indexOf("MSIE") > -1; //判断是否IE<11浏览器  
        var isEdge = userAgent.indexOf("Edge") > -1 && !isIE; //判断是否IE的Edge浏览器  
        var isIE11 = userAgent.indexOf('Trident') > -1 && userAgent.indexOf("rv:11.0") > -1;

        if( isIE || isEdge || isIE11 ){
            return true ;
        }else{
            return false ;
        }
    }     
    function IEVersion() {
        var userAgent = navigator.userAgent; //取得浏览器的userAgent字符串  
        var isIE = userAgent.indexOf("compatible") > -1 && userAgent.indexOf("MSIE") > -1; //判断是否IE<11浏览器  
        var isEdge = userAgent.indexOf("Edge") > -1 && !isIE; //判断是否IE的Edge浏览器  
        var isIE11 = userAgent.indexOf('Trident') > -1 && userAgent.indexOf("rv:11.0") > -1;
        if(isIE) {
            var reIE = new RegExp("MSIE (\\d+\\.\\d+);");
            reIE.test(userAgent);
            var fIEVersion = parseFloat(RegExp["$1"]);
            if(fIEVersion == 7) {
                return 7;
            } else if(fIEVersion == 8) {
                return 8;
            } else if(fIEVersion == 9) {
                return 9;
            } else if(fIEVersion == 10) {
                return 10;
            } else {
                return 6;//IE版本<=7
            }   
        } else if(isEdge) {
            return 11;//edge
        } else if(isIE11) {
            return 11; //IE11  
        }
    }

})(jQuery);
