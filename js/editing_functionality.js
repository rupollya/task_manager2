function changeColor(color) {
    document.execCommand('foreColor', false, color); // меняем цвет выделенного текста
}

let currentFontSize = 3;
let currentBackgroundColor = 'white'; // цвет по умолчанию

function setFontSize(size) {
    currentFontSize = size;
    document.getElementById("editableDiv").focus(); // фокусируемся на поле
    document.execCommand('fontSize', false, size); // применяем размер шрифта
}

// применяем размер шрифта при каждом вводе текста
document.getElementById('editableDiv').addEventListener('input', function () {
    document.execCommand('fontSize', false, currentFontSize);
});

function setBackgroundColor(color) {
    currentBackgroundColor = color;
    document.getElementById("editableDiv").focus(); // фокусируемся на поле
    document.execCommand('hiliteColor', false, color); // применяем цвет фона
}

// применяем цвет фона при каждом вводе текста
document.getElementById('editableDiv').addEventListener('input', function () {
    document.execCommand('hiliteColor', false, currentBackgroundColor);
});

// применение стиля текста (жирный, курсив, подчеркнутый)
function applyTextStyle(style) {
    document.getElementById("editableDiv").focus(); // фокусируемся на поле
    document.execCommand(style, false, null); // применяем стиль
}

// удаляем всех стилей
function removeAllStyles() {
    document.getElementById("editableDiv").focus(); // фокусируемся на поле
    document.execCommand('removeFormat', false, null); // снимаем все стили
}
const editableDiv = document.getElementById('editableDiv');

editableDiv.addEventListener('input', function () {
    const text = editableDiv.innerText;

    // обрезаем длину
    if (text.length > 1000) {
        editableDiv.innerText = text.substring(0, 1000);
        // курсор в конец текста
        placeCaretAtEnd(editableDiv);
    }
});

// Функция для установки курсора в конец текста
function placeCaretAtEnd(el) {
    el.focus();
    const range = document.createRange();
    range.selectNodeContents(el);
    range.collapse(false);
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
}