// Copyright: King's College London
// Author: Hefeng Zhou

let chart = Highcharts.chart('container', hcOption(0))
let chart1 = Highcharts.chart('container1', hcOption(1))
let chart2 = Highcharts.chart('container2', hcOption(2))

function hcOption(stockId) {
    hc = {
        chart: {
            type: 'spline',
            marginRight: 10,
            events: {
                load: function () {
                    let series = this.series[0],
                        chart = this;
                    activeLastPointToolip(chart);
                                    
                    let y = 0
                    setInterval(function () {
                        let x = (new Date()).getTime();
                        $.ajax({
                            url: "/ssgj",
                            type: "POST",
                            dataType: "JSON",
                            contentType: "application/json",
                            data:JSON.stringify({
                                stockId: stockId,
                            }),

                            success: function (data) {
                                console.log(data);
                                y = data[2]
                            },
                            error: function (data) {
                                alert("操作失败");
                            }});
                        console.log(y);
                            // y = Math.random()

                        series.addPoint([x,y], true, true);
                        activeLastPointToolip(chart);
                    }, 2000);
                }
            }
        },
        title: {
            text: 'Real-time stock price'
        },
        xAxis: {
            type: 'datetime',
            tickPixelInterval: 150
        },
        yAxis: {
            title: {
                text: 'price'
            }
        },
        tooltip: {
            formatter: function () {
                return '<b>' + this.series.name + '</b><br/>' +
                       Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) + '<br/>' +
                    Highcharts.numberFormat(this.y, 2);
            }
        },
        legend: {
            enabled: true
        },
        series: [{
            name: 'stock price',
            data: (function () {

                let data = [],
                    time = (new Date()).getTime(),
                    i;
                for (i = -19; i <= 0; i += 1) {
                    data.push({
                            x: time + i * 1000,
                            y: 0
                    });
                }
                return data;
            }())
        }]
    }
    return hc
}

function activeLastPointToolip(chart) {
    var points = chart.series[0].points;
    chart.tooltip.refresh(points[points.length -1]);
}

Highcharts.setOptions({
    global: {
        useUTC: false
    }
})
