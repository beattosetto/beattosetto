function RenderDemoCard(value) {
    // Use ajax to get the rendered beatmap card
    $.ajax({url: '/api/get_demo_card/' + value, success: function(result) {
        $('#demo-beatmap-card').replaceWith(result);
        $('.mediPlayer').mediaPlayer();
    }});
}