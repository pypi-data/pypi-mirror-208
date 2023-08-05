import {
	CommunityEditorClassic,
	CommunityEditorBalloon,
	CommunityEditorInline,
	CommunityEditorBalloonBlock
} from './src/ckeditor';
import emojies from './src/emojies_extra';
import './src/ckeditor-css-overrides.css';
import ImageUpload from '@ckeditor/ckeditor5-image/src/imageupload.js';
import SimpleUploadAdapter from '@ckeditor/ckeditor5-upload/src/adapters/simpleuploadadapter.js';

let editors = {};

async function initCommunityEditor(elem) {

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

  async function query(uri, searchString, marker) {
    return fetch(
      uri + "?query=" + searchString, {
      headers: {
        'X-CSRFTOKEN': getCookie("csrftoken"),
        'Content-Type': 'application/json'
      }
    }).then(
      response => response.json().then(
        data => {
          data.forEach(d => {
            d.id = marker + d.id;
            d.text = d.out_name;
          })
          return data
        }
      )
    )
  }

  async function queryUser(searchString) {
    return query(elem.dataset.queryUserUrl, searchString, "@")
  }

  async function queryComment(searchString) {
    return query(elem.dataset.queryCommentUrl, searchString, "#")
  }

  async function queryMention(searchString) {
    return query(elem.dataset.queryMentionUrl, searchString, "~")
  }

  const script_id = `${elem.id}_script`
  document.querySelector(`[for$="${elem.id}"]`).style.float = 'none';
  const config = JSON.parse(
    document.getElementById(script_id).textContent,
    (key, value) => {
      if(value.toString().includes('/')){
        return new RegExp(value.replaceAll('/', ''));
      }
      return value;
    }
  );

  config.typing = { transformations: { extra: emojies.map(d => {return { from: `${d.from} `, to: `${d.to} ` }}) } };

  function emojiItemRenderer(item) {
    const itemElement = document.createElement('span');
    itemElement.textContent = item.id;
    const emojiElement = document.createElement('span');
    emojiElement.classList.add("mx-4");
    emojiElement.textContent = item.text;
    itemElement.appendChild( emojiElement );
    return itemElement;
  }

  function mentionItemRenderer(item) {
    const itemElement = document.createElement("div");
    itemElement.innerHTML = `
      <div class="d-flex">
        <span class="w-100 p-2 fw-bold">${item.name}</span>
        <span class="align-self-start px-1 flex-shrink-1 badge bg-secondary">${item.model_verbose_name}</span>
      </div>
      <span class="text-muted">${item.subtitle}</span>
    `
    return itemElement
  }

  config.mention = {
    feeds: [
      {
        marker: ':',
        feed: emojies.map(d => { return { id: d.from, text: d.to } }),
        itemRenderer: emojiItemRenderer,
        minimumCharacters: 0
      },
      {
        marker: "@",
        minimumCharacters: 0,
        itemRenderer: mentionItemRenderer,
        feed: queryUser
      },
      {
        marker: "#",
        minimumCharacters: 0,
        itemRenderer: mentionItemRenderer,
        feed: queryComment
      },
      {
        marker: "~",
        minimumCharacters: 1,
        itemRenderer: mentionItemRenderer,
        feed: queryMention
      }
    ]
  };
  let editorTypes = {
    classic: CommunityEditorClassic,
    inline: CommunityEditorInline,
    balloon: CommunityEditorBalloon,
    "balloon-block": CommunityEditorBalloonBlock
  }
  if (elem.dataset.uploadUrl) {

    config['simpleUpload'] = {
      'uploadUrl': elem.dataset.uploadUrl,
      'headers': {
        'X-CSRFTOKEN': getCookie("csrftoken"),
      }
    }
    config.plugins = [
      ...editorTypes[elem.dataset.editorType].builtinPlugins,
      SimpleUploadAdapter,
      ImageUpload]
  }
  return editorTypes[elem.dataset.editorType].create(elem, config).then(
    editor => {
      if (elem.required) {
        elem.required = false;
        editor.ui.element.classList.add("required");
      }
      window.CKEditor.editors[elem.id] = editor;
      return editor;
    }
  )
}

window.addEventListener("load", () => {
  const allEditors = document.querySelectorAll('.community-ckeditor5');

  window.CKEditor = {
    editors: editors,
    init: initCommunityEditor
  }

  for (let i = 0; i < allEditors.length; ++i) {
    initCommunityEditor(allEditors[i]).catch(
      error => { console.error("Error creating editor", error) }
    );
  }

}, {passive: true});
