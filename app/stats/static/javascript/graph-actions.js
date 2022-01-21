function refreshGreencheckChart(graphDataBaseUrl){
    var timeScope = document.getElementById('time_scope').value;
    vegaEmbed('#greencheck_chart', graphDataBaseUrl + '/?scope=' + timeScope)
};