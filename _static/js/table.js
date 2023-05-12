$(window).on('load', function () {

    let tile_click_count = js_vars.tile_click_count;
    let opt_click_count = js_vars.opt_click_count;
    let col_names = js_vars.column_names;
    let options = js_vars.options;
    let numbers = js_vars.numbers;
    let blur_rad = js_vars.blur_rad;
    let circ_rad = js_vars.circ_rad;

    // Generate Table Contents
    // Generate Header
    $.each(col_names, function(i, val){
       let td =  $("<td>"+val+"</td>");
       td.attr({class: 'typical-cell'})
       $("#tableau thead tr").append(td);
    });

    // Generate Options
    let is_first = true;
    let main_td = $("<td>");
    $.each(options, function(i, val){
        // Create the radio button
        let tr = $("<tr>");
        let td = $("<td>", {class: 'typical-cell'});

        let id = 'choice_' + val;
        let inp_attr = {type: 'radio',
                        class: 'choice-rad',
                        name: 'choice',
                        id: id,
                        value: val,
                        };
        let inp = $("<input>", inp_attr);
        let lab = $("<label>", {for: id});
        lab.text(val);

        td.append(inp);
        td.append(lab);
        tr.append(td);

        // For the first row of the outer table, create the cell that holds the inner table
        if (is_first){
            is_first = false;
            let main_td_attr = { class: 'big_cell',
                        rowspan: options.length,
                        colspan: col_names.length - 1,
                        };
            main_td.attr( main_td_attr );
            tr.append(main_td);
        }


        $("#tableau tbody").append(tr);
    });

    // Main table body
    let blur_attr = {
        class: 'blur-it',
        b: blur_rad,
        r: circ_rad,
    };
    let main_tab = $('<table>', blur_attr);
    $.each(options, function(i, option){
       let tr = $('<tr>');
       $.each(numbers[i], function(j, val){
           let td = $('<td>',  {class: 'typical-cell'});
           td.text(val);
           tr.append(td);
        });
       main_tab.append(tr);
    });
    main_td.append(main_tab);


    $('.choice-rad').click(function(){
        let c = $(this).val();
        $('#choice').val(c);

        // Send click information
        opt_click_count += 1;
        liveSend({'func': 'option-click',
                        'seq': opt_click_count,
                        'option': c,
                        });

    });

    $('.cover').click(function(){
        $('.n-cell').css('visibility', 'hidden');
        $('.cover').css('background-color', 'black');

        $(this).css('background-color', 'white');
        $(this).children('.n-cell').css('visibility', 'visible');

        // Send results
        tile_click_count += 1;
        let td = $(this).parents('td');
        let x = td.attr('x');
        let y = td.attr('y');
        liveSend({'func': 'tile-click',
                        'seq': tile_click_count,
                        'x': x, 'y': y});
    });
});