import '../js/auth.js'

// =======================
// DOM ELEMENTS
// =======================

const startPage = document.querySelector('.start-page');
const thoughtPage = document.querySelector('.thought-page');

const startButton = document.getElementById('start-btn');
const thoughtButton = document.getElementById('thought-btn');

const accountButton = document.getElementById('account-btn');

const searchButton = document.getElementById('thought-search-btn');
const createButton = document.getElementById('thought-create-btn');

const thoughtText = document.getElementById('thought-text');
const thoughtAuthor = document.getElementById('author-name');

const registerWrapper = document.querySelector('.register');
const authWrapper = document.querySelector('.authorisation');

const dialog = document.getElementById('auth-modal');
const closeButton = document.querySelectorAll('.close-btn');
const changeAuthButton = document.querySelectorAll('.change-auth-btn');

// =======================
// RANDOM THOUGHT
// =======================

async function getRandomThought() {
    const thought = {
        'text': '',
        'author': ''
    };
    
    try {
        const response = await fetch('http://127.0.0.1:8000/thoughts/random', {
            method: 'GET'
        });

        const responseData = await response.json();

        if (response.status === 404) {
            console.warn(responseData['detail']);
           
            thought.text = 'Сейчас доступных мыслей нет, но Вы можете добавить свои';
            thought.author = 'Админ THOUGHTS';

            return thought;

        } else if (!response.ok) {
            throw new Error(`Error: ${response.status}\nDetail: ${responseData['detail']}`);
        }

        thought.text = responseData['text'];
        thought.author = responseData['author'];

        return thought;
    }
    catch (error) {
        console.error(error.message);

        thought.text = 'Ошибка сервера, попробуйте позже';
        thought.author = 'Злой сервер';

        return thought;
    }
}

async function displayRadomThought() {
    const thought = await getRandomThought();
    
    thoughtText.textContent = '"' + thought.text + '"';
    thoughtAuthor.textContent = '- ' + thought.author;
}

startButton.addEventListener('click', () => {
    startPage.hidden = true;
    thoughtPage.hidden = false;

    displayRadomThought();
});

thoughtButton.addEventListener('click', () => {
    displayRadomThought();
});

// =======================
// AUTH MODAL
// =======================

// вместо этого будет нормальная обработка 
[accountButton, searchButton, createButton].forEach(button => {
    button.addEventListener('click', () => {
        if (registerWrapper.hidden === true && authWrapper.hidden === true) {
            authWrapper.hidden = false;
        }

        dialog.showModal();
    });
});

changeAuthButton.forEach(button => {
    button.addEventListener('click', () => {
        registerWrapper.hidden = !registerWrapper.hidden;
        authWrapper.hidden = !authWrapper.hidden;
    });
});

closeButton.forEach(button => {
    button.addEventListener('click', () => {
        dialog.close();
    });
});


