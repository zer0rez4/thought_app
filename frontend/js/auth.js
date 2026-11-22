import { 
    registerUser, resendEmailVerification,
    loginUser
 } from '../js/api.js';


const registerForm = document.getElementById('register-form');
const authForm = document.getElementById('auth-form');

const resendButton = document.querySelector('.resend-email-btn')
const loginResendEmailButton = document.getElementById('login-resend-email-btn')

const registerError = document.getElementById('register-error');
const loginError = document.getElementById('login-error')

const checkEmailWindow = document.querySelector('.check-email')
const errorText = document.getElementById('resend-email-status-text')


let registeredEmail = '';


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


registerForm.addEventListener('submit', async event => {
    event.preventDefault();

    const formData = new FormData(registerForm);

    const username = formData.get('username');
    const email = formData.get('email');
    const password = formData.get('password');

    try {
        const response = await registerUser(username, email, password);
    
        const responseData = await response.json();

        if (response.status === 409 && responseData['detail'] === 'User already exists') {
            registerError.textContent = 'Аккаунт с этой почтой уже существует';
            
            return
        }

        if (!response.ok) {
            registerError.textContent = 'Ошибка сервера, попробуйте позже';

            throw new Error(`Error: ${response.status}\nDetail: ${responseData['detail']}`);
        }

        registerForm.hidden = true;
        checkEmailWindow.hidden = false;
    }
    catch (error) {
        console.error(error.message);
        return
    }

    registeredEmail = email;
});


resendButton.addEventListener('click', async event => {    
    try {
        const response = await resendEmailVerification(registeredEmail);

        const responseData = await response.json();

        if (response.status === 409 && responseData['detail'] === 'email is already verified') {
            errorText.textContent = 'Аккаунт уже подтвержден';
            return
        }

        if (response.status === 429 && responseData['detail'] === 'Please wait before requesting another email') {
            errorText.textContent = 'Нельзя отправлять много запросов';
            return
        }

        if (!response.ok) {
            errorText.textContent = 'Ошибка сервера, попробуйте позже';
            
            throw new Error(`Error: ${response.status}\nDetail: ${responseData['detail']}`);
        }

        errorText.textContent = 'Письмо отправлено';
    }
    catch (error) {
        console.error(error.message);
        return
    }

})


authForm.addEventListener('submit', async event => {
    event.preventDefault();

    const formData = new FormData(authForm);

    const email = formData.get('email');
    const password = formData.get('password');
    
    try {
        const response = await loginUser(email, password)
        const responseData = await response.json()

        if (response.status === 404 && responseData.detail === 'User does not exist') {
            loginError.textContent = 'Пользователь не зарегистрирован';
        }
        if (response.status === 401 && responseData.detail === 'password is incorrect') {
            loginError.textContent = 'Неверный пароль';
        }
        if (response.status === 403 && responseData.detail === 'account is deleted') {
            loginError.textContent = 'Аккаунт удален';
        }
        if (response.status === 403 && responseData.detail === 'email is not verified') {
            loginError.textContent = 'Аккаунт не подтвержден';

            loginResendEmailButton.hidden = false;
        }
    }
    catch (error) {
        console.error(error.message);
        loginError.textContent = 'Ошибка сервера';
        return;
    }

    localStorage.setItem('access_token', responseData.access_token);
    localStorage.setItem('refresh_token', responseData.refresh_token);

    document.getElementById('auth-modal').close();

    authForm.reset();
    loginResendEmailButton.hidden = true;
    loginError.textContent = '';

    window.location.reload();
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
