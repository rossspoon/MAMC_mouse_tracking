$(window).on('load', function () {

    let click_order = 0;

    $('.choice-content').each(function(idx){
        row_len = $(this).siblings().length;
        x = idx % row_len;
        y = Math.floor(idx / row_len);
       $(this).attr("x", x);
       $(this).attr("y", y);
    });

    $('.choice-rad').click(function(){
        c = $(this).val();
       $('#choice').val(c);
    });

    $('.cover').click(function(){
        $('.n-cell').css('visibility', 'hidden');
        $('.cover').css('background-color', 'black');

        $(this).css('background-color', 'white');
        $(this).children('.n-cell').css('visibility', 'visible');

        // Send results
        click_order += 1;
        td = $(this).parents('td');
        x = td.attr('x');
        y = td.attr('y');
        liveSend({'func': 'cell-click', 'seq': click_order, 'x': x, 'y': y});
    });
});