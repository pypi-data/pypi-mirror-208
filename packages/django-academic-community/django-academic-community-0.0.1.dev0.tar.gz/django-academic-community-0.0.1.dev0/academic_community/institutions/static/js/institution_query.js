if (!$) {
    $ = django.jQuery;
}


var initialChoices = {};
var restResponseCache = {};

function setInitialChoices(i, elem) {
    initialChoices[elem.id] = [...elem.childNodes].map(o => parseInt(o.value));
}

function fill_departments(
    instId="id_institution",
    deptId="id_department",
    unitId="id_unit"
) {

    if (typeof (restUri) == "undefined") {
        var final_restUri = "../../../../../rest/";
    } else {
        var final_restUri = restUri;
    }

    var currInst = $(`#${instId}`)[0].value;

    function handleDepartments(department_set) {

        restResponseCache[uri] = department_set;

        var currDept = $(`#${deptId}`)[0].value;
        var currUnit = $(`#${unitId}`)[0].value;

        var menu = $(`#${deptId}`);
        menu.empty();
        $(`#${unitId}`).empty();
        menu.append($('<option></option>').attr('value', "").text("Select a department"));

        var validChoices = initialChoices[deptId];

        if (typeof (department_set) != "undefined") {

            $.each(department_set.filter(obj => validChoices.includes(obj.id)), function (idx, obj) {
                menu.append($('<option></option>').attr('value', obj.id).text(obj.name));
            });
        }

        menu.children(`option[value='${currDept}']`)
            .attr("selected", "selected");
        fill_units(deptId, unitId, currUnit);
        $(`#${unitId}`).children(`option[value='${currUnit}']`)
            .attr("selected", "selected");

        if (menu.children().length == 1) {
            menu.hide();
        } else {
            menu.show();
        }
    }

    var uri = `${final_restUri}institutions/${currInst}/`

    if (currInst != "" && typeof (restResponseCache[uri]) == "undefined") {

        $.ajax({
            url: uri,
            type: 'GET',
            data:  {},
            dataType: "json",
            success: function (resp) {
                handleDepartments(resp.department_set)
            },
            error: function(jqXHR, textStatus, errorThrown) {
                alert(errorThrown);
            }
        });
    } else {
        handleDepartments(restResponseCache[uri]);
    }

}

function fill_units(
    deptId="id_department",
    unitId="id_unit",
    selectedUnit="",
) {

    if (typeof (restUri) == "undefined") {
        var final_restUri = "../../../../../rest/";
    } else {
        var final_restUri = restUri;
    }

    var currDept = $(`#${deptId}`)[0].value;

    function handleUnits(unit_set) {
        restResponseCache[uri] = unit_set;
        var currUnit = (selectedUnit == "") ? $(`#${unitId}`)[0].value : selectedUnit;
        var menu = $(`#${unitId}`);
        menu.empty();
        menu.append($('<option></option>').attr('value', "").text("Select a unit"));

        var validChoices = initialChoices[unitId];

        if (typeof (unit_set) != "undefined") {
            $.each(unit_set.filter(obj => validChoices.includes(obj.id)), function (idx, obj) {
                menu.append($('<option></option>').attr('value', obj.id).text(obj.name));
            });

        }

        menu.children(`option[value='${currUnit}']`)
            .attr("selected", "selected");

        if (menu.children().length == 1) {
            menu.hide();
        } else {
            menu.show();
        }
    }

    var uri = `${final_restUri}departments/${currDept}/`

    if (currDept != "" && typeof (restResponseCache[uri]) == "undefined") {

        $.ajax({
            url: uri,
            type: 'GET',
            data: {},
            dataType: "json",
            success: function (resp) {
                handleUnits(resp.unit_set)
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert(errorThrown);
            }
        });
    } else {
        handleUnits(restResponseCache[uri]);
    }
}


function fill_department_form() {
    var instId = this.id;
    var deptId = instId.replace(/_0$/g, "_1");
    var unitId = instId.replace(/_0$/g, "_2");
    fill_departments(instId, deptId, unitId);
}


function fill_unit_form() {
    var deptId = this.id;
    var unitId = deptId.replace(/_1$/g, "_2");
    fill_units(deptId, unitId);
}


$(document).ready(function () {

    $(
        'select[name$="membership_Department"], \
        select[name$="organization_Department"], \
        select[name$="membership_Unit"], \
        select[name$="organization_Unit"], \
        select[name$="membership_Institution"], \
        select[name$="organization_Institution"]'
    ).each(setInitialChoices);

    $('select[name$="membership_Department"], \
       select[name$="organization_Department"], \
       select[name$="membership_Unit"], \
       select[name$="organization_Unit"]'
    )
        .removeAttr("required");

    $('select[name$="membership_Department"], select[name$="organization_Department"]')
        .change(fill_unit_form);

    $('select[name$="membership_Institution"], select[name$="organization_Institution"]')
        .change(fill_department_form)
        .trigger("change");

});
