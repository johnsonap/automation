$('#sidebar').on('click', function(e){
    $('.pane').hide();
    window.e = e;
    $('#' + $(e.target).attr('data-pane')).show()
});