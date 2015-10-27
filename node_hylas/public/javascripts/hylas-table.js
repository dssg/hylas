$(document).ready(function() {
    $.getJSON('/data/top_features', function(jd) {
        $('#table').text(jd.data);
    });
});
