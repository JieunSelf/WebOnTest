const testForm = document.querySelector('.testForm');
const testInput = testForm.querySelector('.testInput');
const result = document.querySelector('.result');

const TESTS_LS = 'testss';
let testss = [];


function paintTest(text){
    const li = document.createElement("li");
    const span = document.createElement("span");
    span.innerText = text;

    const delBtn = document.createElement("button");
    delBtn.innerText = '지워';
    delBtn.addEventListener('click', deleteTest);
    
    const newId = testss.length + 1;

    li.appendChild(span);
    li.appendChild(delBtn);
    li.id = newId;

    result.appendChild(li);
    const testObj = {
        text: text, 
        id : newId
    };

    testss.push(testObj);

    saveTests();
}

function saveTests() {
    localStorage.setItem(TESTS_LS, JSON.stringify(testss));
}

function deleteTest(event) {
    const btn = event.target;
    const li = btn.parentNode;
    result.removeChild(li);
    const cleanTests = testss.filter(function(test) {
        return test.id !== parseInt(li.id);
    });
    testss = cleanTests;
    saveTests();
}

function handleSubmit(event) {
    event.preventDefault();
    const currentValue = testInput.value;
    paintTest(currentValue);
    testInput.value = "";
}

function loadTests() {
    const loadedTests = localStorage.getItem(TESTS_LS);
    if (loadedTests !== null) {
        const parsedTests = JSON.parse(loadedTests);
        parsedTests.forEach(function(test) {
            paintTest(test.txt);
        })
    }
}

function init() {
    loadTests();
    testForm.addEventListener('submit', handleSubmit);

}

init();

