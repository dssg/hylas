//http://stackoverflow.com/questions/8749236/create-table-with-jquery-append
var cellCallBack = function(row, col, val) {
    $.getJSON('/data/distribution?col=' + col, function(jd) {
        var distribution=jd.data;
        plotHistogram($("#histogram"), distribution, 10, val);
    });
}

var makeCellCallBack = function(row, col, val) {
    return function() {
        cellCallBack(row, col, val)
    };
}


$(document).ready(function() {
    $.getJSON('/data/top_features', function(jd) {
        var topFeatures = jd.data;
        topFeatures.push('row_num');
        topFeatures.push('pred_proba');
        var table = $('<table></table>');
        var row = $('<tr></tr>');
        topFeatures.forEach(function(th) {
            var cell = $('<th></th>').text(th);
            row.append(cell);
        });
        table.append(row);
        $.getJSON('/data/top_units?n=10&cols=' + topFeatures.toString(), 
            function(jd) {
            var columns = jd.data;
            var nRows = columns[Object.keys(columns)[0]].length;
            for (var i = 0; i < nRows; i++) {
                var row = $('<tr></tr>');
                topFeatures.forEach(function(colName) {
                    var td = columns[colName][i];
                    var cell = $('<td></td>').text(td.toString().slice(0, 4));
                    cell.click(makeCellCallBack(columns['row_num'][i], 
                                                colName,
                                                td));
                    row.append(cell);
                });
                table.append(row)
            }
            $('#hylas_table').replaceWith(table);
        });
    });

});
