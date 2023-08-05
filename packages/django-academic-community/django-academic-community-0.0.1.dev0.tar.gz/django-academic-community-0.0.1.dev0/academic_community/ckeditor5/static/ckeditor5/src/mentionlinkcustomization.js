function MentionLinkCustomization(editor) {

    // Downcast the model 'mention' text attribute to a view <a> element.
    editor.conversion.for( 'downcast' ).attributeToElement( {
        model: 'mention',
        view: ( modelAttributeValue, { writer } ) => {

            // Do not convert empty attributes (lack of value means no mention).
            if ( !modelAttributeValue || (typeof(modelAttributeValue.url) === "undefined") ) {
                return;
            }

            let attrs = structuredClone(modelAttributeValue.out_attrs);
            attrs["data-mention"] = modelAttributeValue.id;
            attrs["data-mention-id"] = modelAttributeValue.id.slice(1);
            attrs["href"] = modelAttributeValue.url;

            return writer.createAttributeElement( 'a', attrs, {
                // Make mention attribute to be wrapped by other attribute elements.
                priority: 20,
                // Prevent merging mentions together.
                id: modelAttributeValue.id
            } );
        },
        converterPriority: 'high'
    } );
}

export default MentionLinkCustomization;
