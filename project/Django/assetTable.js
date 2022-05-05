// Copyright: King's College London
// Author: Hefeng Zhou
$("#asset-table").bootstrapTable("destroy");
$("#asset-table").bootstrapTable({
    class: "table table-bordered table-hover",
    contentType: "application/x-www-form-urlencoded; charset=UTF-8",
    url: "/assetList",
    method: "POST",
    dataType: "JSON",
    pagination: true,
    showColumns: true,
    showToggle: true,
    showRefresh: true,
    cache: false,
    uniqueId: "assetId",
    idField: "assetId",
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
        field: 'assetId',
        title: 'assetId资产id',
        sortable: true
    }, {
        field: 'assetName',
        title: 'assetName资产名称',
        sortable: true
    },  {
        field: 'assetNumber',
        title: 'assetNumber资产股数',
        sortable: true
    }, {
        field: 'assetPrice',
        title: 'assetPrice资产价格',
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

    function addAsset() {
        $("#assetId").val("");
        $("#assetId").prop("disabled", "disabled");
        $("#assetName").val("");
        $("#assetNumber").val("");
        $("#assetPrice").val("");
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