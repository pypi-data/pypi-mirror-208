import $ from 'jquery';
import 'select2/dist/js/select2.full';
import 'select2/dist/css/select2.css';
import './select2_overrides.css';
import emojiData from './grouped_emojies';

jQuery.event.special.touchstart = {
  setup: function( _, ns, handle ) {
      this.addEventListener("touchstart", handle, { passive: !ns.includes("noPreventDefault") });
  }
};
jQuery.event.special.touchmove = {
  setup: function( _, ns, handle ) {
      this.addEventListener("touchmove", handle, { passive: !ns.includes("noPreventDefault") });
  }
};
jQuery.event.special.wheel = {
  setup: function( _, ns, handle ){
      this.addEventListener("wheel", handle, { passive: true });
  }
};
jQuery.event.special.mousewheel = {
  setup: function( _, ns, handle ){
      this.addEventListener("mousewheel", handle, { passive: true });
  }
};

function matchNames(params, data) {
  // If there are no search terms, return all of the data
  if (!params.term || (params.term.trim() === '')) {
    return data;
  }

  // Skip if there is no 'children' property
  if (typeof data.children === 'undefined') {
    return null;
  }

  // `data.children` contains the actual options that we are matching against
  var filteredChildren = [];
  $.each(data.children, function (idx, child) {
    if (child.alt_names.some(name => name.toUpperCase().indexOf(params.term.toUpperCase()) == 0)) {
      filteredChildren.push(child);
    }
  });

  // If we matched any of the timezone group's children, then set the matched children on the group
  // and return the group object
  if (filteredChildren.length) {
    var modifiedData = $.extend({}, data, true);
    modifiedData.children = filteredChildren;

    // You can return modified objects from here
    // This includes matching the `children` how you want in nested data sets
    return modifiedData;
  }

  // Return `null` if the term should not be displayed
  return null;
}

async function initEmojiSelect2(elem, attrs) {
  if (typeof (attrs) === "undefined") {
    attrs = {}
  }
  attrs.data = emojiData;
  attrs.matcher = matchNames;
  attrs.dropdownCssClass = "select2-emoji-dropdown";
  return elem.select2(attrs);
}

export { initEmojiSelect2 };
