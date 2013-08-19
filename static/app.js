document.ontouchstart = function(e){ 
    e.preventDefault(); 
}

$(window).on('scroll', function(e){
   scrollAmount = $(this).scrollTop();
   if(scrollAmount < 1){
      $(this).scrollTop(1);
   }
   if(scrollAmount > $(document).height() - $(window).height()){
      $(this).scrollTop($(window).height());
   }
});

window.flag_status = '';
window.weather;
window.hvac_settings;

function sigFigs(n, sig) {
    if(n == 0){ return 0;}
    var mult = Math.pow(10,
        sig - Math.floor(Math.log(n) / Math.LN10) - 1);
    return Math.round(n * mult) / mult;
}

$('#sidebar').fastClick(function(e){
    $('.pane').removeClass('active');    
    $('#' + $(e.target).attr('data-pane')).addClass('active');
    $.get('settings/current_tab/'+$(e.target).attr('data-pane'));

});

$('.hvac a').fastClick(function(e){

    window.e = e;
    setting = '';
    on_off = '';
    if($(e.target).html() == 'OFF'){
        $('.hvac a').removeClass('btn-primary').addClass('btn-default');
        $(e.target).addClass('btn-primary')
        setting = 'OFF'
        on_off = 'OFF'
    }
    if($(e.target).html() == 'HEAT'){
        $('.hvac_setting a').removeClass('btn-primary').addClass('btn-default');
        $(e.target).removeClass('btn-default').addClass('btn-primary');
        if($('.off').hasClass('btn-primary')){
            $('.off').removeClass('btn-primary').addClass('btn-default')
            $('.auto').removeClass('btn-default').addClass('btn-primary')
        }
        setting = 'HEAT'
        on_off = $('.on_off .btn-primary').html();
    }
    
    if($(e.target).html() == "ON"){
        $('.on_off a').removeClass('btn-primary').addClass('btn-default');
        if(!$('.hvac_setting a').hasClass('btn-primary')){
            $('.heat').removeClass('btn-default').addClass('btn-primary');
        }
        $(e.target).removeClass('btn-default').addClass('btn-primary');
        setting =  $('.hvac_setting .btn-primary').html();;
        on_off = 'ON';
    }
    
    if($(e.target).html() == "AUTO"){
        $('.on_off a').removeClass('btn-primary').addClass('btn-default');
        if(!$('.hvac_setting a').hasClass('btn-primary')){
            $('.heat').removeClass('btn-default').addClass('btn-primary');
        }
        $(e.target).removeClass('btn-default').addClass('btn-primary');
        setting =  $('.hvac_setting .btn-primary').html();;
        on_off = 'AUTO';
    }
    
    if($(e.target).html() == 'AC'){
        $('.hvac_setting a').removeClass('btn-primary').addClass('btn-default');
        $(e.target).removeClass('btn-default').addClass('btn-primary');
        if($('.off').hasClass('btn-primary')){
            $('.off').removeClass('btn-primary').addClass('btn-default')
            $('.auto').removeClass('btn-default').addClass('btn-primary')   
        }
        setting = 'AC'
        on_off = $('.on_off .btn-primary').html();
    }
    
    $.get('hvac/setting/'+setting+'/'+on_off);
    
});

$('#temp-plus').fastClick(function(e){
    addTemp(1);
});
$('#temp-minus').fastClick(function(e){
    addTemp(-1);    
});

$('.light:not(.control)').fastClick(function(e){

    $(e.target).toggleClass('on');
    var light_status = 'off'
    if($(e.target).hasClass('on')){
        light_status = 'on';
    }
    $.get('/lights/' + $(e.target).parent().attr('data-id')+'/' +light_status);
})

function addTemp(index){
    $temp = $('#current-temp .temp');
    temp = parseInt($temp.html()) + index
    if(temp > 90){
        temp = 65;
    }
    if(temp < 65){
        temp = 90;
    }
    $temp.html(temp + '&deg;')
    $.get('hvac/temp/'+temp + '/'+ window.id)
    
}

_.templateSettings = {
  interpolate : /\{\{(.+?)\}\}/g
};
window.id = Math.floor(new Date().getTime()*Math.random(1,10));

var pusher = new Pusher('bbfd2fdfc81124a36b18');

var weather_channel = pusher.subscribe('weather');
var hvac_channel = pusher.subscribe('hvac');
var light_channel = pusher.subscribe('lights');

weather_channel.bind('current_conditions', function(data) {
    window.weather = data;
    $.ajaxSetup({
        async: false
    });
    var weather_template = $.get('static/templates/weather.html')
    $('#weather-forecast').html(_.template(weather_template.responseText, weather));    
});

hvac_channel.bind('update_temp', function(data) {
    if(data.id != window.id){
        $('#current-temp .temp').html(data.temp);
    }
});

light_channel.bind('update_lights', function(data) {

    if(data.status == 'on'){
        $('[data-id="'+data.name+'"] i').addClass('on');
    }
    else{
        $('[data-id="'+data.name+'"] i').removeClass('on');
    }
});

$('.control').fastClick(function(e){
    if($(e.target).hasClass('on')){
        $.get('/lights/on');
    }
    else{
        $.get('/lights/off');
    }
});

light_channel.bind('all_lights', function(data) {

    if(data.status == 'on'){
        $('.light:not(.control)').addClass('on');
    }
    else{
        $('.light:not(.control)').removeClass('on');
    }
});

hvac_channel.bind('update_settings', function(data) {
    $('.hvac a').removeClass('btn-primary').addClass('btn-default');
    $('.hvac .'+data.on_off.toLowerCase()).removeClass('btn-default').addClass('btn-primary');
    $('.hvac .'+data.hvac_setting.toLowerCase()).removeClass('btn-default').addClass('btn-primary');
});
    
    
    
    
    
    

    
    
    
    
    