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

function addTemp(index){
    $temp = $('#current-temp .temp');
    temp = parseInt($temp.html()) + index
    if(temp > 90){
        temp = 65;
    }
    if(temp < 65){
        temp = 90;
    }
    $temp.html(temp)
    $.get('hvac/temp/'+temp + '/'+ window.id)
    
}

_.templateSettings = {
  interpolate : /\{\{(.+?)\}\}/g
};
window.id = Math.floor(new Date().getTime()*Math.random(1,10));

var pusher = new Pusher('bbfd2fdfc81124a36b18');

var weather_channel = pusher.subscribe('weather');

var hvac_channel = pusher.subscribe('hvac');

var flag_channel = pusher.subscribe('flag');

weather_channel.bind('current_conditions', function(data) {
    window.weather = data;
    $.ajaxSetup({
        async: false
    });
    var weather_template = $.get('static/templates/weather.html')
    $('#weather-forecast').html(_.template(weather_template.responseText, weather));    
    
    /*
$('#outsideTemp').html(Math.round(data.current_conditions.temp_f));
    var night = '';
    $('#outsideTemp').attr('class', night + data.current_conditions.icon) 
    wind = (sigFigs(data.current_conditions.wind_mph*.8,2));
    wind_str = wind+ ' knots, ' + data.current_conditions.wind_dir;
    if (wind < 1) wind_str = "Calm";
    $('#currentConditions p').html('High: ' + data.forecast[0].high.fahrenheit + '&deg;<br>Low: ' + data.forecast[0].low.fahrenheit +'&deg;<br>Wind: '+ wind_str +'<br>Relative Humidity: ' + data.current_conditions.relative_humidity)
    $('.outside span').html(Math.round(data.current_conditions.temp_f));
*/
});

hvac_channel.bind('update_temp', function(data) {
    if(data.id != window.id){
        $('#current-temp .temp').html(data.temp);
    }
});

flag_channel.bind('update_flag', function(data) {
    window.flag_status = data.flag_color
    $('.icon-flag').attr('class', 'icon-flag ' + data.flag_color);
});

hvac_channel.bind('update_settings', function(data) {
    $('.hvac a').removeClass('btn-primary').addClass('btn-default');
    $('.hvac .'+data.on_off.toLowerCase()).removeClass('btn-default').addClass('btn-primary');
    $('.hvac .'+data.hvac_setting.toLowerCase()).removeClass('btn-default').addClass('btn-primary');
});
    
    
    
    
    
    
    
    
    
    
    
    
    