// Helper function to generate the SVG tag for the clip path.
function get_svg(idx) {
    return `<svg width='0' height='0'>
            <defs>
                <clipPath id='clip-path_${idx}'>
                    <path id='neg_circ_${idx}' />
                </clipPath>
            </defs>
            </svg>`;
};

function get_overlay_style(z){
    return `position: absolute; top: 0px; left: 0px; z-index: ${z};`;
}


// Helper function to generate the blur layer.
function get_mask(w, h, idx){
    over_style = get_overlay_style(10);
    return `<div class='mask overlay' style='${over_style}; width: ${w}px; height: ${h}px; clip-path:url(#clip-path_${idx});'>  </div>`;


};

// Helper function to generate the window layer.
// The window layer is necessary because when the clip path is applied
// to the mask layer, the mouse will no longer be 'on' the mask layer.
// This layer doesn't change so the event listeners are attached to 
//  this.
function get_window(w, h){
    over_style = get_overlay_style(11);
    return `<div class='window overlay' style='${over_style} width: ${w}px; height: ${h}px;'>  </div>`;
};

// helper to get the clip path that covers the entire element.
// this will be the off-mouse clip path.
function get_full_path(w, h){
    return `m 0 0 H ${w} V ${h} H 0 z`;
};


$(window).on("load", function() {
    // the elements to be blurred are given the "blur-it" class
    $('.blur-it').each(function(index) {

            // if the found element is block-level, then
            // set it's display to inline-block to avoid collapsing
            // margins:
            // https://stackoverflow.com/questions/9519841/why-does-this-css-margin-top-style-not-work/9519896#9519896
            let elem_display = $(this).css('display');
            if (elem_display == 'block' || elem_display == 'table'){
                $(this).css('display', 'inline-block');
            }

            // get the width and height of the target object
            w = $(this).width();
            h = $(this).height();

            // wrap the target object in a div with position: relative
            // the mask and widow layers will be positioned relative
            // to this wrapper div.
            $(this).wrap(`<div class='blur-frame' style="position: relative;"></div>`);

            // the parent of the wrapper div is the newly-formed
            // wrapper.  prepend the parent with the svg, mask, and
            // window elements.
            $(this).parent().prepend([get_svg(index),
                                    get_mask(w, h, index),
                                    get_window(w, h)]);

            // add blurring to the mask layer
            b = $(this).attr("b")
            if (!b){
                b = '10px';
            } else {
                b = b + 'px';
            }
            $(this).siblings('.mask').css('backdrop-filter', `blur(${b})`);

            // determine the radius
            // set the radius on the svg element so that the
            // mouse over event listener can get it later.
            r = $(this).attr('r');
            if (!r) {
                r = 100;
            }
            $(this).siblings('svg').attr('r', r);


            // set the clip path to the be the entire element
            $(`#neg_circ_${index}`).attr("d", get_full_path(w, h));
    });

    $(".window").mousemove(function(event) {
        //the svg element should have an "r" attribute on it by now
        svg_elem = $(this).siblings('svg');
        r = svg_elem.attr('r');

        w = $(this).width();
        h = $(this).height();
        x = event.offsetX;
        y = event.offsetY + Number(r);

        d = `m 0 0 H ${w} V ${h} H ${x} V ${y}  a ${r} ${r}, 0, 1, 0, -1 0 h 1 V ${h} H 0 z`;

        svg_elem.find('path').attr("d", d);
    });

    $(".window").mouseleave(function() {
        w = $(this).width();
        h = $(this).height();

        $(this).siblings('svg').find('path').attr("d", get_full_path(w, h));
    });
});

$(window).resize( function() {
    $(".blur-it").each(function() {
        w = $(this).width();
        h = $(this).height();

        $(this).siblings(".overlay").width(w).height(h);
        $(this).siblings("svg").find("path").attr("d", get_full_path(w, h));
    });

});

