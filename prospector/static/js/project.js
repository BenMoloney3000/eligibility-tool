const correctionInputs = document.querySelectorAll('#id_data_correct input')
const correctionInputTarget = document.querySelector('#correction')
const roleInputs = document.querySelectorAll('input[name=respondent_role]')
const otherRoleTarget = document.querySelector('#other-detail')
const addressSelector = document.querySelector('.postcode-populator select')
const address1Field = document.querySelector('.target-address_1 input')
const address2Field = document.querySelector('.target-address_2 input')
const address3Field = document.querySelector('.target-address_3 input')

function setCorrectionVisibility() {
    if (document.querySelector('#id_data_correct_1').checked) {
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
        let selectedAddress = addresses[e.target.value]

        address1Field.value = selectedAddress.address1
        address2Field.value = selectedAddress.address2
        address3Field.value = selectedAddress.address3
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

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHandler)
} else {
    initHandler()
}
