const testForm = document.querySelector(".testForm")
const testInput = document.querySelector(".testInput")
const testList = document.querySelector(".testList")

const TESTS_LS = "tests";
let tests = [];

function deleteTest(event) {
    const btn = event.target;
    const li = btn.parentNode;
    testList.removeChild(li);
    const cleanTests = tests.filter(function(test) {
        return test.id !== parseInt(li.id);
    });

    tests = cleanTests;
    saveTests();
}

function saveTests() {
    localStorage.setItem(TESTS_LS, JSON.stringify(tests));
}

function createTest(text) {
    const li = document.createElement("li");
    const delBtn = document.createElement("button");
    const span = document.createElement("span");
    const newId = tests.length +1;
    delBtn.innerText = "삭제";
    
    delBtn.addEventListener("click", deleteTest);

    span.innerText = text;

    li.appendChild(span);
    li.appendChild(delBtn);
    li.id = newId;

    testList.appendChild(li);

    const testObj = {
        text : text,
        id : newId
    };

    tests.push(testObj);
    saveTests();
}

function handleSubmit(event) {
    event.preventDefault();
    const currentValue = testInput.value;
    createTest(currentValue);
    testInput.value = ""; //이 코드가 없다면? 어떻게 될까?
}

function loadTests(){
    const loadedTests = localStorage.getItem(TESTS_LS);
    if (loadedTests !== null) {
        const parsedTests = JSON.parse(loadedTests);
        parsedTests.forEach(function(test) {
            createTest(test.text);
        });
    }
}


function init(){
    loadTests();
    testForm.addEventListener('submit', handleSubmit);
}

// function init(){
//     loadTests();
//     testForm.addEventListener("keyup", (event) => {
//         const ENTER = 13
//         if (event.keyCode === ENTER) {
//             handleSubmit(event);
//         }
//     })


//     // testForm.addEventListener("submit", getTests);
//     getTests();
// }

init();

// function getTests(){
//     document.getElementById('tset-btn').onclick = function tset() {
//         let testsss = localStorage.getItem('tests');
//         return testsss
//     }
// }

// function jsontest(){
//     var httpRequest;
//     document.getElementById('test-btn').addEventListener('click', makeRequest);

//     function makeRequest() {
//         httpRequest = new XMLHttpRequest();

//         if(!httpRequest) {
//             alert('에러..ㅠㅠ');
//             return false;
//         }
//         httpRequest.onreadystatechange = saveContents;
//         httpRequest.open('POST', 'test_step2.html');
//         httpRequest.send();
//     }

//     function saveContents() {
//         if (httpRequest.readyState === XMLHttpRequest.DONE) {
//             if (httpRequest.status === 200) {

//             }
//         }
//     }
// }