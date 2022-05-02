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
                        oData.oFilter.sSearch = "";
                    },
                    "fnStateLoad": function (oSettings) {
                        return JSON.parse( localStorage.getItem('DataTables') );
                    },

                    "columnDefs": [
                        { type: 'de_datetime', targets: 2 },
                        { type: 'de_date', targets: 8 },
                        { type: 'de_date', targets: 9 },
                        { type: 'de_date', targets: 21 },
                        { type: 'de_date', targets: 22 },
                        { type: 'de_date', targets: 24 }
                    ]
                });

                $('.dataTables_length').addClass('bs-select');

                $("#searchButton").click(function() {
                    var value = $("#searchBar").val().toLowerCase();
                    table
                    .column(0)
                    .search(value)
                    .draw();
                });

                $("#searchBar").keypress(function(e) {
                    if(e.which === 13) {
                        e.preventDefault();
                        table.column(0).search($(this).val()).draw();
                    }
                });

                $("#advancedSearch").click(function() {
                    $("#searchForm").toggle("fast");
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
            });