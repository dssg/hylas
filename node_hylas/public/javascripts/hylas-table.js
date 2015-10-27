//http://stackoverflow.com/questions/8749236/create-table-with-jquery-append
$(document).ready(function() {
    $.getJSON('/data/top_features', function(jd) {
        var table = $('<table></table>');
        var row = $('<tr></tr>');
        jd.data.forEach( function(th) {
            var cell = $('<th></th>').text(th);
            row.append(cell);
        });
        table.append(row);
        $('#hylas_table').append(table);
    });
});
