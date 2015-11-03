//http://stackoverflow.com/questions/8749236/create-table-with-jquery-append
var cellCallBack = function(row, col, val) {
    $.getJSON('/data/distribution?col=' + col, function(jd) {
        var distribution=jd.data;
        plotHistogram($('#histogram'), distribution, 10, val);
        $('td').css('background-color', 'white');
        $('.row_' + row).css('background-color', 'red'); 
        $('.col_' + col).css('background-color', 'yellow'); 
        $('#histogram_title').text('Distribution of feature ' + col);
    });
}

var makeCellCallBack = function(row, col, val) {
    return function() {
        cellCallBack(row, col, val)
    };
}

var populate_table = function(n_units, n_features) {
    $.getJSON('/data/top_features?n=' + n_features, function(jd) {
        var topFeatures = jd.data;
        topFeatures.push('row_num');
        topFeatures.push('pred_proba');
        var table = $('<table></table>');
        table.attr('id', 'hylas_table');
        var row = $('<tr></tr>');
        topFeatures.forEach(function(th) {
            var cell = $('<th></th>').text(th);
            row.append(cell);
        });
        table.append(row);
        $.getJSON('/data/top_units?n=' + n_units + '&cols=' + 
            topFeatures.toString(), 
            function(jd) {
            var columns = jd.data;
            var nRows = columns[Object.keys(columns)[0]].length;
            for (var i = 0; i < nRows; i++) {
                var row_num = columns['row_num'][i];
                var row = $('<tr></tr>');
                topFeatures.forEach(function(colName) {
                    var td = columns[colName][i];
                    var cell = $('<td></td>')
                        .text(td.toString().slice(0, 4))
                        .click(makeCellCallBack(row_num, 
                                                colName,
                                                td))
                        .addClass('col_' + colName)
                        .addClass('row_' + row_num);
                    row.append(cell);
                });
                table.append(row)
            }
            $('#hylas_table').replaceWith(table);
        });
    });
}

$(document).ready(function() {
    populate_table(10, 10);
    $('#btn_gen_table').click(function () {
        populate_table($('#txt_n_units').val(), $('#txt_n_features').val());
    });
});
