$(document).ready(function() {

    $.getJSON('static/js/statistics.json', function(stats) {
        const ctx = $('#myChart');

        const labels = Object.keys(stats);

        const data = {
            labels: labels,
            datasets: [{
                label: 'Dataset',
                backgroundColor: 'rgb(255, 99, 132)',
                borderColor: 'rgb(255, 99, 132)',
                data: Object.values(stats),
            }]
          };

        const config = {
            type: 'bar',
            data: data,
            options: {
                responsive: false,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            font: {
                                family: 'Arial'
                            }
                        }
                    }
                }
            }
        };

        const myChart = new Chart(
            ctx,
            config
        );
    });


});