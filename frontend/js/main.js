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
// DATA
// =======================

// фейк данные (будет запрос к api)
const thoughtArr = [
    {
        id: 1,
        text: 'Оставим мертвым хоронить мертвых, а пока жив, надо жить и быть счастливым',
        author: 'Лев Толстой',
        is_public: true
    },
    {
        id: 2,
        text: 'Стремитесь не к успеху, а к ценностям, которые он дает',
        author: 'Альберт Эйнштейн',
        is_public: true
    },
    {
        id: 3,
        text: 'Нет ничего более сильного, чем человек, решивший встать после падения',
        author: 'Фёдор Достоевский',
        is_public: true
    },
];

// =======================
// RANDOM THOUGHT
// =======================

function getRandomThoughtIndex() {
    return Math.floor(thoughtArr.length * Math.random());
}
// фейк данные (будет запрос к api)

function displayThought() {
    const thought = thoughtArr[getRandomThoughtIndex()];
    
    thoughtText.textContent = '"' + thought.text + '"';
    thoughtAuthor.textContent = '- ' + thought.author;
}

startButton.addEventListener('click', () => {
    startPage.hidden = true;
    thoughtPage.hidden = false;

    displayThought();
});

thoughtButton.addEventListener('click', () => {
    displayThought();
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
