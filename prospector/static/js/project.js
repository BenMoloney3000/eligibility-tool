const correctionInputs = document.querySelectorAll('#id_data_correct input')
const correctionInputTarget = document.querySelector('#correction')
const roleInputs = document.querySelectorAll('input[name=respondent_role]')
const otherRoleTarget = document.querySelector('#other-detail')

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

function initHandler() {
    correctionInputs.forEach((e) => {
        e.addEventListener('click', setCorrectionVisibility)
    })
    /* Special case: 'other' role field */
    if (document.querySelector('#id_respondent_role_OTHER')) {
        setRoleVisibility()
        roleInputs.forEach((e) => e.addEventListener('click', setRoleVisibility))
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHandler)
} else {
    initHandler()
}
