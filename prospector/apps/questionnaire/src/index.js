import { initAll } from 'govuk-frontend'

const correctionInputs = document.querySelectorAll('#div_id_data_correct input')
const correctionInputTarget = document.querySelector('#correction')
const roleInputs = document.querySelectorAll('input[name=respondent_role]')
const otherRoleTarget = document.querySelector('#other-detail')
const addressSelector = document.querySelector('.postcode-populator select')
const address1Field = document.querySelector('.target-address_1 input')
const address2Field = document.querySelector('.target-address_2 input')
const address3Field = document.querySelector('.target-address_3 input')

const READONLY = 'readonly'

function setCorrectionVisibility() {
    if (document.querySelector('#id_data_correct_2').checked) {
        correctionInputTarget.style.display = 'block'
    } else {
        correctionInputTarget.style.display = 'none'
    }
}

function setRoleVisibility() {
    if (document.querySelector('#id_respondent_role_OTHER').checked) {
        otherRoleTarget.style.display = 'block'
    } else {
        otherRoleTarget.style.display = 'none'
    }
}

function updateAddressFields(e) {
    const addresses = JSON.parse(document.getElementById('allPostcodes').textContent)
    if (e.target.value in addresses) {
        const selectedAddress = addresses[e.target.value]

        address1Field.value = selectedAddress.address1
        address1Field.setAttribute(READONLY, READONLY)
        address2Field.value = selectedAddress.address2
        address2Field.setAttribute(READONLY, READONLY)
        address3Field.value = selectedAddress.address3
        address3Field.setAttribute(READONLY, READONLY)
    } else {
        address1Field.value = ''
        address1Field.removeAttribute(READONLY)
        address2Field.value = ''
        address2Field.removeAttribute(READONLY)
        address3Field.value = ''
        address3Field.removeAttribute(READONLY)
    }
}

function initHandler() {
    correctionInputs.forEach((e) => {
        e.addEventListener('click', setCorrectionVisibility)
    })
    /* Special case: 'other' role field */
    if (document.querySelector('#id_respondent_role_OTHER')) {
        setRoleVisibility()
        roleInputs.forEach((e) => e.addEventListener('click', setRoleVisibility))
    }
    if (addressSelector) {
        addressSelector.addEventListener('change', updateAddressFields)
    }
}

function init() {
    initAll()
    initHandler()
}

document.addEventListener('DOMContentLoaded', init, false)
