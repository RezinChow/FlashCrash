// Copyright: King's College London
// Author: Hefeng Zhou
$("#relationship-table").bootstrapTable("destroy");
$("#relationship-table").bootstrapTable({
    class: "table table-bordered table-hover",
    contentType: "application/x-www-form-urlencoded; charset=UTF-8",
    url: "/relationshipList",
    method: "POST",
    dataType: "JSON",
    pagination: true,
    showColumns: true,
    showToggle: true,
    showRefresh: true,
    cache: false,
    uniqueId: "relationshipId",
    idField: "relationshipId",
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
        field: 'relationshipId',
        title: 'relationshipId关系id',
        sortable: true
    }, {
        field: 'agentId',
        title: 'agentId用户id',
        sortable: true
    }, {
        field: 'agentName',
        title: 'agentName用户名',
        sortable: true
    },{
        field: 'assetId',
        title: 'assetId资产id',
        sortable: true
    },{
        field: 'assetName',
        title: 'assetName资产名',
        sortable: true
    }, {
        field: 'holdingNumber',
        title: 'holdingNumber持有股数',
        sortable: true
    }]
    // }, {
    //     field: 'operate',
    //     title: 'operate',
    //     align: 'center',
    //     formatter: btnGroup,
    //     events: {
    //         'click .edit-btn': function (event, value, row) {
    //             editRelationship(row.agentId, row);
    //         }
    //     }
    // }]
});

    // function btnGroup() {
    //     return '<a href="#!" class="btn btn-xs btn-default m-r-5 edit-btn" title="edit" data-toggle="modal" data-target="#exampleModal"><i class="mdi mdi-pencil"></i></a>';
    // }

    function addRelationship() {
        $("#relationshipId").val("");
        $("#relationshipId").prop("disabled", "disabled");
        $("#agentId").val("");
        $("#agentId").prop("disabled", "disabled");
        $("#agentName").val("");
        $("#assetId").val("");
        $("#assetId").prop("disabled", "disabled");
        $("#assetName").val("");
        $("#holdingNumber").val("");
    }

    function sellAsset(relationshipId, row) {
        $("#relationshipId1").val(row.relationshipId);
        $("#relationshipId1").prop("readonly", "readonly");
        $("#holdingNumber1").val(row.holdingNumber);
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
        var agentId = $("#agentId").val();
        var agentName = $("#agentName").val();

        var flag = isNotNull();
        if (flag) {
            $.ajax({
                url: "/agentUpdate",
                type: "POST",
                dataType: "JSON",
                contentType: "application/json",
                data: JSON.stringify({
                    agentId: agentId,
                    agentName: agentName,
                }),
                success: function (data) {
                    window.location.reload();
                }
            })
        }
    }