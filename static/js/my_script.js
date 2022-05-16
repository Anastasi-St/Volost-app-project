$(document).ready(function() {
    var table = $('#docsTable').DataTable({
        "language": {
            "url": "https://cdn.datatables.net/plug-ins/1.11.5/i18n/ru.json"
        },
        "dom": "lrtip",
        "lengthMenu":  [ [50, 100, 500, -1], [50, 100, 500, "Все"] ],
        "aaSorting": [],
        "bStateSave": true,
        "fnStateSave": function (oSettings, oData) {
            localStorage.setItem( 'DataTables', JSON.stringify(oData) );
            //oData.oFilter.sSearch = "";
        },
        "fnStateLoad": function (oSettings) {
            return JSON.parse( localStorage.getItem('DataTables') );
        },

        "columnDefs": [
            { type: 'de_datetime', targets: 2 },
            { type: 'de_date', targets: 8 },
            { type: 'de_date', targets: 9 },
            { type: 'num', targets: 10},
            { type: 'de_date', targets: 21 },
            { type: 'de_date', targets: 22 },
            { type: 'num', targets: 23},
            { type: 'de_date', targets: 24 },
            { type: 'num', targets: 25},
        ]
    });

    $('.dataTables_length').addClass('bs-select');

    $("#searchButton").click(function() {
        var value = $("#searchBar").val().toLowerCase();
        table
        .column(1)
        .search(value)
        .draw();
    });

    $("#searchBar").keypress(function(e) {
        if(e.which === 13) {
            e.preventDefault();
            table.column(1).search($(this).val()).draw();
        }
    });

    $("#advancedSearch").click(function(e) {
        e.stopPropagation();
        $(".searchForm").toggle();
    });

    // $("#resetForm").click(function() {
    //    $('input:checkbox').removeAttr('checked');
    //    $("select#searchForm").multiselect('refresh');
    //});

    $("#shortTable").on('click', function() {
        var cols = table.columns([4, 5, 6, 7, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]);
        $("#docsTable").css('width', '93vw');
        cols.visible(false);
    });
    $("#fullTable").on('click', function() {
        var cols = table.columns([4, 5, 6, 7, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]);
        cols.visible(true);
    });

    $(".multiple").multiselect(
        {
            nonSelectedText: "Ничего не выбрано",
            allSelectedText: "Выбрано всё",
            maxHeight: 150,
            numberDisplayed: 5,
            nSelectedText: "выбрано"
        }
    );

    $( "#slider-range" ).slider({
          range: true,
          min: new Date('2010.01.01').getTime() / 1000,
          max: new Date('2014.01.01').getTime() / 1000,
          step: 86400,
          values: [ new Date('2010.01.01').getTime() / 1000, new Date('2014.02.01').getTime() / 1000 ],
          slide: function( event, ui ) {
            $( "#amount" ).val( (new Date(ui.values[ 0 ] *1000).toDateString() ) + " - " + (new Date(ui.values[ 1 ] *1000)).toDateString() );
          }
        });

    $( "#amount" ).val( (new Date($( "#slider-range" ).slider( "values", 0 )*1000).toDateString()) +
          " - " + (new Date($( "#slider-range" ).slider( "values", 1 )*1000)).toDateString());

    $("#textButton").click(function() {
        if (!$("#textButton").hasClass("active")) {
            $("#img").hide();
            $("#imgButton").removeClass("active");
            $("#textButton").addClass("active");
            $("#text").show();
        };
    });

    $("#imgButton").click(function() {
        if (!$("#imgButton").hasClass("active")) {
            $("#text").hide();
            $("#textButton").removeClass("active");
            $("#imgButton").addClass("active");
            $("#img").show();
        };
    });
});