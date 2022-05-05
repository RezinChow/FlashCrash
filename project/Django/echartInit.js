// Copyright: King's College London
// Author: Hefeng Zhou

let mychart = echarts.init(document.getElementById('main'));
let option = null

let userY = 400
let assetY = 300
let fundY = 200
let bankY = 100

option = {
    title: {
        text: 'Topology'
    },
    tooltip: {},
    animationDurationUpdate: 1500,
    animationEasingUpdate: 'quinticInOut',
    series: [
        {
            type: 'graph',
            layout: 'none',
            symbolSize: 60,
            roam: true,
            label: {
                show: true
            },
            edgeSymbol: ['arrow', 'arrow'],
            edgeSymbolSize: [10, 10],
            edgeLabel: {
                fontSize: 20
            },
            data: [{
                name: 'Bank1',
                x: 300,
                y: 100
            }, {
                name: 'Bank2',
                x: 400,
                y: 100
            }, {
                name: 'Bank3',
                x: 500,
                y: 100
            }, {
                name: 'Fund1',
                x: 350,
                y: 200
            }, {
                name: 'Fund2',
                x: 450,
                y: 200
            }, {
                name: 'Asset1',
                x: 300,
                y: 300
            }, {
                name: 'Asset2',
                x: 400,
                y: 300
            }, {
                name: 'Asset3',
                x: 500,
                y: 300
            }, {
                name: 'External compensation',
                x: 400,
                y: 400
            }],
            // links: [],
            links: [{
                source: 'External compensation',
                target: 'Asset1'
            }, {
                source: 'External compensation',
                target: 'Asset2'
            }, {
                source: 'External compensation',
                target: 'Asset3'
            }, {
                source: 'Asset1',
                target: 'Fund2'
            }, {
                source: 'Asset2',
                target: 'Fund1'
            }, {
                source: 'Asset3',
                target: 'Fund1'
            }, {
                source: 'Asset3',
                target: 'Fund2'
            }, {
                source: 'Fund1',
                target: 'Bank1'
            }, {
                source: 'Fund1',
                target: 'Bank2'
            }, {
                source: 'Fund1',
                target: 'Bank3'
            }, {
                source: 'Fund2',
                target: 'Bank2'
            }, {
                source: 'Fund2',
                target: 'Bank3'
            }],
            lineStyle: {
                opacity: 0.9,
                width: 2,
                curveness: 0
            }
        }
    ]
};
mychart.setOption(option);

initSelect()