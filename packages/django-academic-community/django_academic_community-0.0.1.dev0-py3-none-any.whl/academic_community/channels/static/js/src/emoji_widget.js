import $ from 'jquery';
import { initEmojiSelect2 } from "./emoji_widget/widget";

$(() => {

  window.emojiSelect2 = {
    init: initEmojiSelect2
  };
  initEmojiSelect2($('.select2-emojies')).then(
    (instances) => { window.emojiSelect2.instances = instances }
  )

});
