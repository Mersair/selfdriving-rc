const imuConfig = {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'x',
            backgroundColor: 'rgb(39,252,255)',
            borderColor: 'rgb(39,252,255)',
            data: [],
            fill: false,
        },
        {
            label: 'y',
            backgroundColor: 'rgb(28,73,255)',
            borderColor: 'rgb(28,73,255)',
            data: [],
            fill: false,
        },
        {
            label: 'z',
            backgroundColor: 'rgb(87,152,255)',
            borderColor: 'rgb(87,152,255)',
            data: [],
            fill: false,
        }],
    },
    options: {
        legend: {
            display: true,
            position: 'top',
        },
        responsive: true,
        title: {
            display: true,
            text: 'IMU'
        },
        tooltips: {
            intersect: true,
            custom: function(tooltip) {
                if (!tooltip) return;
                // disable displaying the color box;
                tooltip.displayColors = false;
            },
            callbacks: {
                title: function(tooltipItems, data) {
                    return '';
                },
                label: function(tooltipItem, data) {
                    return tooltipItem.yLabel;
                }
            }
        },
        hover: {mode: 'point'},
        scales: {
            xAxes: [{
                gridLines: {
                    color: "#666"
                },
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Time'
                }
            }],
            yAxes: [{
                gridLines: {
                    color: "#666"
                },
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Value'
                }
            }]
        }
    }
};

const uscConfig = {
    type: 'radar',
    data: {
        labels: ["u1", "u2", "u3", "u4", "u5", "u6", "u7"],
        datasets: [{
            label: '',
            backgroundColor: 'rgb(209,51,255)',
            borderColor: 'rgb(209,51,255)',
            data: [],
            fill: false,
        }],
    },
    options: {
        legend: {
            display: true,
            position: 'top',
        },
        responsive: true,
        title: {
            display: true,
            text: 'Ultrasonic'
        },
        tooltips: {
            intersect: true,
            custom: function(tooltip) {
                if (!tooltip) return;
                // disable displaying the color box;
                tooltip.displayColors = false;
            },
            callbacks: {
                title: function(tooltipItems, data) {
                    return '';
                },
                label: function(tooltipItem, data) {
                    return tooltipItem.yLabel;
                }
            }
        },
        hover: {mode: 'point'},
        scales: {
            xAxes: [{
                gridLines: {
                    color: "#666"
                },
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Time'
                }
            }],
            yAxes: [{
                gridLines: {
                    color: "#666"
                },
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Value'
                }
            }]
        }
    }
};

const hefConfig = {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: '',
            backgroundColor: 'rgb(209,51,255)',
            borderColor: 'rgb(209,51,255)',
            data: [],
            fill: false,
        }],
    },
    options: {
        legend: {
            display: false
        },
        responsive: true,
        title: {
            display: true,
            text: 'Hall Effect'
        },
        tooltips: {
            intersect: true,
            custom: function(tooltip) {
                if (!tooltip) return;
                // disable displaying the color box;
                tooltip.displayColors = false;
            },
            callbacks: {
                title: function(tooltipItems, data) {
                    return '';
                },
                label: function(tooltipItem, data) {
                    return tooltipItem.yLabel;
                }
            }
        },
        hover: {mode: 'point'},
        scales: {
            xAxes: [{
                gridLines: {
                    color: "#666"
                },
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Time'
                }
            }],
            yAxes: [{
                gridLines: {
                    color: "#666"
                },
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Value'
                }
            }]
        }
    }
};

const batConfig = {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: '',
            backgroundColor: '#2FFF65',
            borderColor: '#2FFF65',
            data: [],
            fill: false,
        }],
    },
    options: {
        legend: {
            display: false
        },
        responsive: true,
        title: {
            display: true,
            text: 'Battery'
        },
        tooltips: {
            intersect: true,
            custom: function(tooltip) {
                if (!tooltip) return;
                // disable displaying the color box;
                tooltip.displayColors = false;
            },
            callbacks: {
                title: function(tooltipItems, data) {
                    return '';
                },
                label: function(tooltipItem, data) {
                    return tooltipItem.yLabel;
                }
            }
        },
        hover: {mode: 'point'},
        scales: {
            xAxes: [{
                gridLines: {
                    color: "#666"
                },
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Time'
                }
            }],
            yAxes: [{
                gridLines: {
                    color: "#666"
                },
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Value'
                }
            }]
        }
    }
};

const tmpConfig = {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: '',
            backgroundColor: '#FF652F',
            borderColor: '#FF652F',
            data: [],
            fill: false,
        }],
    },
    options: {
        legend: {
            display: false
        },
        responsive: true,
        title: {
            display: true,
            text: 'Temperature'
        },
        tooltips: {
            intersect: true,
            custom: function(tooltip) {
                if (!tooltip) return;
                // disable displaying the color box;
                tooltip.displayColors = false;
            },
            callbacks: {
                title: function(tooltipItems, data) {
                    return '';
                },
                label: function(tooltipItem, data) {
                    return tooltipItem.yLabel;
                }
            }
        },
        hover: {mode: 'point'},
        scales: {
            xAxes: [{
                gridLines: {
                    color: "#666"
                },
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Time'
                }
            }],
            yAxes: [{
                gridLines: {
                    color: "#666"
                },
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Value'
                }
            }]
        }
    }
};

const hmdConfig = {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: '',
            backgroundColor: '#FFE400',
            borderColor: '#FFE400',
            data: [],
            fill: false,
        }],
    },
    options: {
        legend: {
            display: false
        },
        responsive: true,
        title: {
            display: true,
            text: 'Humidity'
        },
        tooltips: {
            intersect: true,
            custom: function(tooltip) {
                if (!tooltip) return;
                // disable displaying the color box;
                tooltip.displayColors = false;
            },
            callbacks: {
                title: function(tooltipItems, data) {
                    return '';
                },
                label: function(tooltipItem, data) {
                    return tooltipItem.yLabel;
                }
            }
        },
        hover: {mode: 'point'},
        scales: {
            xAxes: [{
                gridLines: {
                    color: "#666"
                },
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Time'
                }
            }],
            yAxes: [{
                gridLines: {
                    color: "#666"
                },
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Value'
                }
            }]
        }
    }
};