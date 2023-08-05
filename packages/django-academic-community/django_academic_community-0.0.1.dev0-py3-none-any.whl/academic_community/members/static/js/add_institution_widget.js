if (!$) {
    $ = django.jQuery;
}


function show_inst_form() {
    $("#institution-control").show();
    $("#department-card").hide();
    $("#unit-card").hide();
}

function show_dept_form() {
    $("#institution-card").hide();
    $("#department-card").show();
    $("#unit-card").hide();
}

function show_unit_form() {
    $("#institution-card").hide();
    $("#department-card").hide();
    $("#unit-card").show();
}

function hide_all_forms() {
    $("#institution-card").hide();
    $("#department-card").hide();
    $("#unit-card").hide();
}


function toggle_forms(instValue, deptValue, unitValue) {
    if (instValue) {
        if (deptValue) {
            if (unitValue) {
                hide_all_forms();
            } else {
                show_unit_form();
            }
        } else {
            show_dept_form();
        }
    } else {
        show_inst_form();
    }
}


function toggle_institution_form() {
    var instId = this.id;
    var deptId = instId.replace(/_0$/g, "_1");
    var unitId = instId.replace(/_0$/g, "_2");
    toggle_forms(this.value, "", "");
}


function toggle_department_form() {
    var deptId = this.id;
    var instId = deptId.replace(/_1$/g, "_0");
    var unitId = deptId.replace(/_1$/g, "_2");
    toggle_forms($(`#${instId}`)[0].value, this.value, "");
}


function toggle_unit_form() {
    var unitId = this.id;
    var instId = unitId.replace(/_2$/g, "_0");
    var deptId = unitId.replace(/_2$/g, "_1");
    toggle_forms($(`#${instId}`)[0].value, $(`#${deptId}`)[0].value, this.value);
}



$(document).ready(function () {

    $('select[name$="membership_Department"], select[name$="organization_Department"]')
        .change(toggle_department_form);

    $('select[name$="membership_Unit"], select[name$="organization_Unit"]')
        .change(toggle_unit_form);

    $('select[name$="membership_Institution"], select[name$="organization_Institution"]')
        .change(toggle_institution_form)
        .trigger("change");

});
