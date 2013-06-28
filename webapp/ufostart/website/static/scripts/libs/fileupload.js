﻿define(["tools/ajax"], function(ajax){

    var View = Backbone.View.extend({
        initialize:function(opts){
            var view = this
                , uploader = this.$(".file-picker-upload")
                , picture_template = _.template(this.$(".picture-template").html());

           filepicker.makeDropPane(uploader[0], {
                dragEnter: function() {
                    uploader.addClass("drop-target");
                },
                dragLeave: function() {
                    uploader.removeClass("drop-target");
                },
                onSuccess: function(fpfiles) {
                    uploader.html('<div class="info">Done!</div>').removeClass("empty");
                    var file = fpfiles[0];
                    uploader.html(picture_template({pic: file}));
                    view.$el.closest(".form-validated").validate().element(view.$el.find('input[type=hidden]').val(file.url));
                },
                onError: function(type, message) {
                    uploader.after().text('('+type+') '+ message);
                },
                onProgress: function(percentage) {
                    uploader.html('<div class="info">Uploading ('+percentage+'%)');
                }
            });
        }
    })
    , init = function(opts){
        return new View(opts);
    };
    return {init: init, View: View};
});