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

const registerDialog = document.querySelector('.register');
const authDialog = document.querySelector('.authorisation');

const dialog = document.getElementById('auth-modal');
const closeButton = document.querySelectorAll('.close-btn');
const changeAuthButton = document.querySelectorAll('.change-auth-btn');

const registerForm = document.getElementById('register-form');
const authForm = document.getElementById('auth-form');

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

[accountButton, searchButton, createButton].forEach(button => {
    button.addEventListener('click', () => {
        dialog.showModal();
    });
});

changeAuthButton.forEach(button => {
    button.addEventListener('click', () => {
        registerDialog.hidden = !registerDialog.hidden;
        authDialog.hidden = !authDialog.hidden;
    });
});

closeButton.forEach(button => {
    button.addEventListener('click', () => {
        dialog.close();
    });
});

// =======================
// FORM VALIDATION
// =======================

function validateForm(form) {
    let isValid = true;

    const inputs = form.querySelectorAll('input');

    inputs.forEach(input => {
        const error = input.nextElementSibling;

        if (!input.checkValidity()) {
            isValid = false;
            input.classList.add('invalid');

            if (input.validity.valueMissing) {
                error.textContent = 'Это поле обязательно';
            } else if (input.validity.typeMismatch) {
                error.textContent = 'Некорректный формат';
            } else if (input.validity.tooShort) {
                error.textContent = 'Пароль должен содержать минимум 6 символов';
            }
        } else {
            input.classList.remove('invalid');
            error.textContent = '';
        }
    });

    return isValid;
}

registerForm.addEventListener('submit', event => {
    event.preventDefault();

    if (!validateForm(registerForm)) {
        return;
    }

    // здесь будет запрос к API
});

authForm.addEventListener('submit', event => {
    event.preventDefault();

    if (!validateForm(authForm)) {
        return;
    }

    // здесь будет запрос к API
});


[registerForm, authForm].forEach(form => {
    form.addEventListener('input', event => {
        const input = event.target;

        const errorText = input.nextElementSibling;

        if (input.checkValidity()) {
            input.classList.remove('invalid');
            errorText.textContent = '';
        }
    });
})
