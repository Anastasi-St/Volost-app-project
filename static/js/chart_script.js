$(document).ready(function() {

    $.getJSON('static/js/statistics.json', function(stats) {
        const ctx = $('#posChart');

        const labels = Object.keys(stats);
        labels.splice(-1);

        const data = {
            labels: labels,
            datasets: [{
                label: stats['pos'],
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
                                family: 'Arial',
                                size: 16
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

    $.getJSON('static/js/lemmas.json', function(stats) {
            const ctx = $('#lemChart');

            const labels = Object.keys(stats);
            labels.splice(-1);

            const data = {
                labels: labels,
                datasets: [{
                    label: stats['lem'],
                    backgroundColor: 'rgb(86, 83, 183)',
                    borderColor: 'rgb(86, 83, 183)',
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
                                    family: 'Arial',
                                    size: 16
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