function filterHTML(html) {

  let whiteList = filterXSS.getDefaultWhiteList();
  whiteList.a.push("class");
  whiteList.a.push("data-mention-id");
  whiteList.blockquote.push("data-mention-id");
  whiteList.mark.push("class");
  whiteList.label = ["class"];
  whiteList.td.push("style");
  whiteList.th.push("style");
  whiteList.figure.push("style");
  whiteList.figure.push("class");
  whiteList.table.push("class");
  whiteList.table.push("style");
  whiteList.col.push("style");
  return filterXSS(html, {
    whiteList: whiteList,
    onIgnoreTag: (tag, html, options) => {
      if (tag == "input") {
        if (html.indexOf("checkbox") >= 0) {
          if (html.indexOf("checked") >= 0) {
            return "<input type='checkbox' checked disabled>"
          } else {
            return "<input type='checkbox' disabled>"
          }
        }
      }
    }
  })
}
