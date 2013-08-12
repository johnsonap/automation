document.ontouchstart = function(e){ 
    e.preventDefault(); 
}

function sigFigs(n, sig) {
    if(n == 0){ return 0;}
    var mult = Math.pow(10,
        sig - Math.floor(Math.log(n) / Math.LN10) - 1);
    return Math.round(n * mult) / mult;
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

$('#sidebar').on('click', function(e){
    $('.pane').hide();
    window.e = e;
    $('#' + $(e.target).attr('data-pane')).show()
});

$('.hvac').on('click','a', function(e){
    console.log('sdfsd'); 
    window.e = e;
    
    if($(e.target).html() == 'OFF'){
        $('.hvac a').removeClass('btn-primary').addClass('btn-default');
        $(e.target).addClass('btn-primary')
    }
    if($(e.target).html() == 'HEAT'){
        $('.hvac_setting a').removeClass('btn-primary').addClass('btn-default');
        $(e.target).removeClass('btn-default').addClass('btn-primary');
        if($('.off').hasClass('btn-primary')){
            $('.off').removeClass('btn-primary').addClass('btn-default')
            $('.auto').removeClass('btn-default').addClass('btn-primary')
        }
    }
    
    if($(e.target).html() == "ON"){
        $('.on_off a').removeClass('btn-primary').addClass('btn-default');
        $(e.target).removeClass('btn-default').addClass('btn-primary');
    }
    
    if($(e.target).html() == "AUTO"){
        $('.on_off a').removeClass('btn-primary').addClass('btn-default');
        $(e.target).removeClass('btn-default').addClass('btn-primary');
    }
    
    if($(e.target).html() == 'AC'){
        $('.hvac_setting a').removeClass('btn-primary').addClass('btn-default');
        $(e.target).removeClass('btn-default').addClass('btn-primary');
        if($('.off').hasClass('btn-primary')){
            $('.off').removeClass('btn-primary').addClass('btn-default')
            $('.auto').removeClass('btn-default').addClass('btn-primary')
        }
    }
    
    $(e.target)
    
});

$('#temp-plus').on('click', function(){
    addTemp(1)
});
$('#temp-minus').on('click', function(){
    addTemp(-1)
});

function addTemp(index){
    temp = parseInt($('#current-temp .temp').html()) + index
    if(temp > 90){
        temp = 65;
    }
    if(temp < 65){
        temp = 90;
    }
    $.get('hvac/temp/'+temp)
    $('#current-temp .temp').html(temp)
}

var pusher = new Pusher('bbfd2fdfc81124a36b18');
    var channel = pusher.subscribe('weather');
    channel.bind('current_conditions', function(data) {
        console.log(data);
        $('#outsideTemp').html(Math.round(data.current_conditions.temp_f));
        wind = (sigFigs(data.current_conditions.wind_mph*.8,2));
        wind_str = wind+ ' knots, ' + data.current_conditions.wind_dir;
        if (wind < 1) wind_str = "Calm";
        $('#currentConditions p').html('High: ' + data.forecast[0].high.fahrenheit + '&deg;<br>Low: ' + data.forecast[0].low.fahrenheit +'&deg;<br>Wind: '+ wind_str +'<br>Relative Humidity: ' + data.current_conditions.relative_humidity)
    });