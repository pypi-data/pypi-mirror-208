if (!$) {
    $ = django.jQuery;
}

function toggle_usage_fields() {
    var usageId = this.id;
    var componentId = usageId.replace(/usage$/g, "component");
    var modelAvailabilityId = usageId.replace(/usage$/g, "model_availability");
    option = $(`select[id=${usageId}] option:contains("Model development")`)[0];

    if (option.selected) {
        $(`#${componentId}`).attr("disabled", false);
        $(`#${modelAvailabilityId}`).attr("disabled", false);
    } else {
        $(`#${componentId}`).attr("disabled", true);
        $(`#${modelAvailabilityId}`).attr("disabled", true);
        $(`#${componentId}`).val("");
        $(`#${modelAvailabilityId}`).val("");
    }
}

$(document).ready(function () {

    $('select[name$="usage"]')
        .change(toggle_usage_fields)
        .trigger("change");
})
