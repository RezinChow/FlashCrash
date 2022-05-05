//## Copyright: King's College London
//Author: Hefeng Zhou

$("#bank-table").bootstrapTable("destroy");
$("#bank-table").bootstrapTable({
    class: "table table-bordered table-hover",
    contentType: "application/x-www-form-urlencoded; charset=UTF-8",
    url: "/bankList",
    method: "POST",
    dataType: "JSON",
    pagination: true,
    showColumns: true,
    showToggle: true,
    showRefresh: true,
    cache: false,
    uniqueId: "bankId",
    idField: "bankId",
    sortable: true,
    queryParams: function (params) {
        return {
            limit: params.limit,
            offset: params.offset,
            page: (params.offset / params.limit) + 1,
            order: params.order,
            ordername: params.sort,
        };
    },
    sidePagination: "server",
    pageNumber: 1,
    pageSize: 10,
    pageList: [10, 20],
    paginationLoop: false,
    columns: [{
        field: 'bankId',
        title: 'bankId银行id',
        sortable: true
    }, {
        field: 'bankName',
        title: 'bankName银行名称',
        sortable: true
    },  {
        field: 'leverageRate',
        title: 'leverageRate杠杆率',
        sortable: true
    }, {
        field: 'leverageSafeRate',
        title: 'leverageSafeRate安全杠杆率',
        sortable: true
    }]
    // }, {
    //     field: 'operate',
    //     title: 'operate',
    //     align: 'center',
    //     formatter: btnGroup,
    //     events: {
    //         'click .edit-btn': function (event, value, row) {
    //             editAsset(row.assetId, row);
    //         }
    //     }
    // }]
});

    // function btnGroup() {
    //     return '<a href="#!" class="btn btn-xs btn-default m-r-5 edit-btn" title="edit" data-toggle="modal" data-target="#exampleModal"><i class="mdi mdi-pencil"></i></a>';
    // }

    function addBank() {
        $("#bankId").val("");
        $("#bankId").prop("disabled", "disabled");
        $("#bankName").val("");
        $("#leverageRate").val("");
        $("#leverageSafeRate").val("");
    }

    function isNotNull() {
        var flag = true;
        $(".form-group input:gt(0)").each(function () {
            var Value = $(this).val().trim();
            if (!Value) {
                var errorMsg = $(this).prev().text() + "can not null";
                $(this).next().text(errorMsg);
                $(this).parent().addClass('has-error');
                flag = false;
            }
        });

        $(".form-group input").focus(function () {
            $(this).next().text('');
            $(this).parent().removeClass('has-error');
        });

        return flag;
    }

    function CloseModel() {
        $(".form-group input").next().text('');
        $(".form-group input").parent().removeClass('has-error');
    }

    function saveChange() {
        var assetId = $("#assetId").val();
        var assetName = $("#assetName").val();

        var flag = isNotNull();
        if (flag) {
            $.ajax({
                url: "/assetUpdate",
                type: "POST",
                dataType: "JSON",
                contentType: "application/json",
                data: JSON.stringify({
                    assetId: assetId,
                    assetName: assetName,
                }),
                success: function (data) {
                    window.location.reload();
                }
            })
        }
    }