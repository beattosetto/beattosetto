function RenderDemoCard(value) {
    // If the value in form is blank, get an API call as the beatmap ID is 0
    let api_url = `/api/get_demo_card/${value || 0}`;
    // Use ajax to get the rendered beatmap card
    $.ajax({url: api_url, success: function(result) {
        document.getElementById('beatmap-card').innerHTML = '<div id="demo-beatmap-card"></div>';
        $('#demo-beatmap-card').replaceWith(result);
        $('.mediPlayer').mediaPlayer();
    }});
}