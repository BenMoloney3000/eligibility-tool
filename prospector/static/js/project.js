const correctionInputs = document.querySelectorAll('#id_data_correct input')
const correctionInputTarget = document.querySelector('#correction')

function setCorrectionVisibility() {
    if (document.querySelector('#id_data_correct_1').checked) {
        correctionInputTarget.style.display = 'block'
    } else {
        correctionInputTarget.style.display = 'none'
    }
}

function initHandler() {
    correctionInputs.forEach(() => {
        addEventListener('click', setCorrectionVisibility)
    })
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHandler)
} else {
    initHandler()
}
