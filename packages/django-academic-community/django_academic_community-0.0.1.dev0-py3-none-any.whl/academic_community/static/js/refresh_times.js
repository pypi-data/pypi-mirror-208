// automatically refresh time since some reference time passed
//
// these functions automatically act on elements with `.time-since` and
// updates the innerHTML of the elements. These elements should define a
// `data-time-created` attribute that holds the creation time in milliseconds,
// e.g. `<span class="time-since" data-time-created="1650649451106"></span>
//
const intervals = [
  { label: 'year', seconds: 31536000 },
  { label: 'month', seconds: 2592000 },
  { label: 'day', seconds: 86400 },
  { label: 'hour', seconds: 3600 },
  { label: 'minute', seconds: 60 },
];

function timeSince(date) {
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
  const interval = intervals.find(i => i.seconds < seconds);
  if (typeof(interval) !== "undefined") {
    const count = Math.floor(seconds / interval.seconds);
    return `${count} ${interval.label}${count !== 1 ? 's' : ''} ago`;
  } else {
    return "just now";
  }
}

function refreshTime(elem) {
elem.innerHTML = timeSince(new Date(parseInt(elem.dataset.timeCreated)));
}

function refreshAllTimeSince() {
  Array.prototype.forEach.call(
    document.getElementsByClassName("time-since"), refreshTime
  );
}

$(function () {
  refreshAllTimeSince();
  setInterval(refreshAllTimeSince, 5000);
})
