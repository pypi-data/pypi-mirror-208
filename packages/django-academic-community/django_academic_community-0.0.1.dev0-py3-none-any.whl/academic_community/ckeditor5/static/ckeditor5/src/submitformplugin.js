import Plugin from '@ckeditor/ckeditor5-core/src/plugin';
import EnterObserver from '@ckeditor/ckeditor5-enter/src/enterobserver';

/**
 * This plugin handles submits the form when hitting Ctrl+Shift+Enter
 */

export default class SubmitForm extends Plugin {

  static get pluginName() {
    return 'SubmitForm';
  }

  init() {
    const editor = this.editor;
    const view = editor.editing.view;
    const viewDocument = view.document;

    view.addObserver( EnterObserver );

    this.listenTo(viewDocument, 'enter', (evt, data) => {

      if ( !viewDocument.isComposing ) {
      	data.preventDefault();
	    }

      if ( !data.isSoft || !data.domEvent.ctrlKey) {
		    return;
      }

      let editorId = data.domTarget.id
      document.querySelectorAll("form").forEach(
        (form) => {
          if (form.querySelector("#" + editorId)) {
            form.querySelector("[type=submit]").click();
            evt.stop();
          }
        }
      )

    }, { priority: 'high' } );
  }
}
