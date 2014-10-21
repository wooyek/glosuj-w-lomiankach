
$(function(){
    var datepicker_options = $.datepicker.regional['pl'];
     datepicker_options.dateFormat = "yy-mm-dd";
     datepicker_options.showButtonPanel = true;
     datepicker_options.changeMonth = true;
     datepicker_options.changeYear = true;
     datepicker_options.showOtherMonths = true;
     datepicker_options.selectOtherMonths = true;
     datepicker_options.firstDay = 1;
     datepicker_options.showWeek = true;
     window.datepicker_options = datepicker_options;
     //    Plebe.current("#nav li a", function(elem){
 //        elem = $(elem)
 //        if (elem.parent().attr('id') != 'School_list') {
 //            elem.parent().addClass("current");
 //        } else if (elem.attr('href') == document.location.pathname){
 //            elem.parent().addClass("current");
 //        }
 //    });
     $.datepicker.setDefaults(datepicker_options);
    $('input#id_due').datepicker();
    $('input#id_perm').datepicker();
});
