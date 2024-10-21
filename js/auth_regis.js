async function checkRegis() {
    var login = document.getElementById("login").value;
    var password = document.getElementById("password").value;
    var loginInput = document.getElementById("login");
    var passwordInput = document.getElementById("password");

    if (login.length < 1) {
        loginInput.classList.add('is-invalid');
        loginInput.classList.remove('is-valid');
    } else {
        loginInput.classList.remove('is-invalid');
        loginInput.classList.add('is-valid');
    }

    if (password.length < 8) {
        passwordInput.classList.add('is-invalid');
        passwordInput.classList.remove('is-valid');
    } else {
        passwordInput.classList.remove('is-invalid');
        passwordInput.classList.add('is-valid');
    }

    if (login.length > 1 && password.length >= 8) {
        const user = {
            login: login,
            password: password
        }

        // регистрация
        try {
            let response = await fetch(`/user/registration`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(user)
            });

            if (response.ok) {
                window.location.href = '/';
            } else {
                let errorData = await response.json();
                if (errorData.detail === "Пользователь с таким логином уже существует") {
                    
                    var userExistsModal = new bootstrap.Modal(document.getElementById('userExistsModal'));
                    userExistsModal.show();
                } else {
                    alert(errorData.error || 'Произошла ошибка при регистрации.');
                }
            }
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при регистрации.');
        }
    }
}
async function checkLogin() {
    var login = document.getElementById("login").value;
    var password = document.getElementById("password").value;
    var loginInput = document.getElementById("login");
    var passwordInput = document.getElementById("password");

    if (login.length < 1) {
        loginInput.classList.add('is-invalid');
        loginInput.classList.remove('is-valid');
    } else {
        loginInput.classList.remove('is-invalid');
        loginInput.classList.add('is-valid');
    }

    if (password.length < 8) {
        passwordInput.classList.add('is-invalid');
        passwordInput.classList.remove('is-valid');
    } else {
        passwordInput.classList.remove('is-invalid');
        passwordInput.classList.add('is-valid');
    }

    if (login.length > 1 && password.length >= 8) {
        const formData = new FormData();
        formData.append('username', login);  
        formData.append('password', password);

        try {
            let response = await fetch('/users/login', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                window.location.href = '/storage';
            } else {
                let errorData = await response.json();
                if (errorData.detail === "Неверный номер телефона или пароль") {
                     
                    var loginErrorModal = new bootstrap.Modal(document.getElementById('loginErrorModal'));
                    loginErrorModal.show();
                } else {
                    alert('Произошла ошибка при авторизации.');
                }
            }
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при авторизации.');
        }
    }
}



 
document.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {  
        event.preventDefault();    
        document.querySelector('.button_regis').click();   
    }
});