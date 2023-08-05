import { initEmojiSelect2 } from './emoji_widget/widget';
import { createPopper } from '@popperjs/core/lib/popper-lite';

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    let cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      let cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

async function createCommentPopovers() {
  document.querySelectorAll(".comment-popover").forEach(
    (tooltip) => {

      function show() {
        // Make the tooltip visible
        tooltip.classList.remove('d-none');

        // Enable the event listeners
        popperInstance.setOptions((options) => ({
          ...options,
          modifiers: [
            ...options.modifiers,
            { name: 'eventListeners', enabled: true },
          ],
        }));

        // Update its position
        popperInstance.update();

        if (!tooltip.dataset.emojiRendered) {
          initEmojiSelect2(
            $(tooltip.querySelector(".select2-emojies-reaction"))
          ).then(
            (instances) => {
              instances.on("select2:select", (event) => {
                let form = event.currentTarget.parentElement;
                let formData = new FormData(form);
                let arrayData = Array.from(formData.entries(), ([x, y]) => ({ [x]: y }));

                let data = arrayData.length ? Object.assign(...arrayData) : {};

                return fetch(
                  form.action,
                  {
                    "method": data.method ? data.method : form.method,
                    body: JSON.stringify(data),
                    headers: {
                      'X-CSRFTOKEN': getCookie("csrftoken"),
                      'Content-Type': 'application/json'
                    }
                  }
                ).then(
                  response => {
                    instances.val(null).trigger('change');  // reset the widget
                    return response;
                  }
                )
              })
            }
          );
        }

        tooltip.dataset.emojiRendered = true;

      }

      function hide() {
        if (!$(tooltip).is(":hover")) {
          // Hide the tooltip
          tooltip.classList.add('d-none');

          // Disable the event listeners
          popperInstance.setOptions((options) => ({
            ...options,
            modifiers: [
              ...options.modifiers,
              { name: 'eventListeners', enabled: false },
            ],
          }));
        }
      }

      function hideOnTooltip() {
        if (!$(popcorn).is(":hover")) {
          // Hide the tooltip
          tooltip.classList.add('d-none');

          // Disable the event listeners
          popperInstance.setOptions((options) => ({
            ...options,
            modifiers: [
              ...options.modifiers,
              { name: 'eventListeners', enabled: false },
            ],
          }));
        }
      }

      const showEvents = ['mouseenter', 'focus'];
      const hideEvents = ['mouseleave', 'blur'];

      const popcorn = document.querySelector(tooltip.dataset.targetComment);
      const popperInstance = createPopper(popcorn, tooltip, {
        placement: 'top-end',
        modifiers: [
          {
            name: 'offset',
            options: {
              offset: [0, -5],
            },
          },
        ]
      });

      showEvents.forEach((event) => {
        popcorn.addEventListener(event, show);
      });

      hideEvents.forEach((event) => {
        popcorn.addEventListener(event, hide);
        tooltip.addEventListener(event, hideOnTooltip);
      });
    }
  )
}

window.addEventListener("load", async function () {
  window.createCommentPopovers = createCommentPopovers;
  createCommentPopovers();
})
