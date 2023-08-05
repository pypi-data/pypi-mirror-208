// simple obfuscation techique for emails. This turns an element like
// <a class='protect-through-replacement' href='mailto:testx@example.com' data-replacement="x">link</a>
// into
// <a class='protect-through-replacement' href='mailto:test@example.com' data-replacement="x">link</a>

function replace_on_mouseover() {
    var re = new RegExp(this.dataset.replacement, "g")
    this.href = this.href.replace(re,'');
}

$(document).ready(
    function () {
        $(".protect-through-replacement").on("mouseover", replace_on_mouseover)
    }
)
