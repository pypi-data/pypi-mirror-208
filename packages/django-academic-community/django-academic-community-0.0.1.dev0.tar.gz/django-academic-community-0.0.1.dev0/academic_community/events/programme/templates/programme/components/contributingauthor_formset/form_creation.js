
{% load community_utils %}

let container = document.querySelector("#{{ container_id|default:'ca-form' }}")
let addCAButton = document.querySelector("#add-ca-form")

let totalAffilForms = document.querySelector("#id_affiliation_set-TOTAL_FORMS")
let totalAuthorForms = document.querySelector("#id_author_set-TOTAL_FORMS")
let totalCAForms = document.querySelector("#id_contributingauthor_set-TOTAL_FORMS")

let authorFormNum = document.querySelectorAll(".author-form").length-1
let affilFormNum = document.querySelectorAll(".affil-form").length-1
let caFormNum = document.querySelectorAll(".ca-form-card").length-1

function addContributingAuthorForm(){
    let newForm = document.createElement("div")
    newForm.innerHTML = `
      {% filter escapejs %}
        {% include "programme/components/contributingauthor_formset/card.html" %}
      {% endfilter %}
    `
    // let newForm = rootElem.children[0].cloneNode(true)
    // djangos Formset.empty_form uses a __prefix__ that should be replaced
    // with the correct number
    let caFormRegex = RegExp(`contributingauthor_set-__prefix__-`,'g')
    let authorFormRegex = RegExp(`author_set-__prefix__-`,'g')
    let affiliationFormRegex = RegExp(`affiliation_set-__prefix__-`,'g')
    let idFormRegex = RegExp(`_id(\\d){1}`,'g')

    authorFormNum++
    affilFormNum++
    caFormNum++

    newForm.innerHTML = newForm.innerHTML.replace(
      caFormRegex, `contributingauthor_set-${caFormNum}-`
    )
    newForm.innerHTML = newForm.innerHTML.replace(
      authorFormRegex, `author_set-${authorFormNum}-`
    )
    newForm.innerHTML = newForm.innerHTML.replace(
      affiliationFormRegex, `affiliation_set-${affilFormNum}-`
    )
    newForm.innerHTML = newForm.innerHTML.replace(idFormRegex, `_id${caFormNum}`)
    container.insertBefore(newForm, addCAButton)

    // ----------------------------------------------------------------------
    // call post-creation functions for the new element

    // django-select2
    $('.django-select2').djangoSelect2()

    // create the switches for is_presenting (see the
    // academic_community/components/switch.html template)
    renderSwitches()

    // ----------------------------------------------------------------------
    // increase authorlist position values
    // necessary for sorting the authors in the backend
    $(`[id$='affiliation_set-${affilFormNum}-authorlist_position']`).val(
      `${caFormNum + 1}`
    )
    $(`[id$='author_set-${authorFormNum}-authorlist_position']`).val(
      `${caFormNum + 1}`
    )
    $(`[id$='contributingauthor_set-${caFormNum}-authorlist_position']`).val(
      `${caFormNum + 1}`
    )


    totalCAForms.setAttribute('value', `${caFormNum+1}`)
    totalAffilForms.setAttribute('value', `${affilFormNum+1}`)
    totalAuthorForms.setAttribute('value', `${authorFormNum+1}`)
}

function addAffilForm(selector){

    let affilForm = document.querySelectorAll(`.affil-form${selector}`)
    let container = document.querySelector(`#affil-form-container${selector}`)
    let addAffilButton = document.querySelector(`#add-affil-form${selector}`)

    let newForm = affilForm[0].cloneNode(true)
    let formRegex = RegExp(`affiliation_set-(\\d){1}-`,'g')

    affilFormNum++
    newForm.innerHTML = newForm.innerHTML.replace(formRegex, `affiliation_set-${affilFormNum}-`)
    container.insertBefore(newForm, addAffilButton)

    totalAffilForms.setAttribute('value', `${affilFormNum+1}`)
}
