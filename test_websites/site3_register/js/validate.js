(function () {
    'use strict';
    var form = document.getElementById('registerForm');

    function clearErrors() {
        var msgs = form.querySelectorAll('.error-msg');
        for (var i = 0; i < msgs.length; i++) msgs[i].textContent = '';
    }

    function showError(id, msg) {
        var el = document.getElementById(id);
        if (el) el.textContent = msg;
    }

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        clearErrors();
        var valid = true;

        var username = form.querySelector('#username').value.trim();
        var email = form.querySelector('#email').value.trim();
        var password = form.querySelector('#password').value;
        var confirmPassword = form.querySelector('#confirmPassword').value;
        var age = form.querySelector('#age').value.trim();

        // Username: 3-20 chars, only letters, digits, underscores
        var usernameRe = /^[a-zA-Z0-9_]{3,20}$/;
        if (!username) {
            showError('usernameError', 'Username is required.');
            valid = false;
        } else if (!usernameRe.test(username)) {
            showError('usernameError', 'Username must be 3–20 characters (letters, digits, underscore only).');
            valid = false;
        }

        // Email
        var emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email) {
            showError('emailError', 'Email address is required.');
            valid = false;
        } else if (!emailRe.test(email)) {
            showError('emailError', 'Please enter a valid email address.');
            valid = false;
        }

        // Password: ≥8 chars, at least one uppercase, one digit, one special char
        if (!password) {
            showError('passwordError', 'Password is required.');
            valid = false;
        } else if (password.length < 8) {
            showError('passwordError', 'Password must be at least 8 characters.');
            valid = false;
        } else if (!/[A-Z]/.test(password)) {
            showError('passwordError', 'Password must contain at least one uppercase letter.');
            valid = false;
        } else if (!/[0-9]/.test(password)) {
            showError('passwordError', 'Password must contain at least one digit.');
            valid = false;
        } else if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
            showError('passwordError', 'Password must contain at least one special character.');
            valid = false;
        }

        // Confirm password
        if (!confirmPassword) {
            showError('confirmPasswordError', 'Please confirm your password.');
            valid = false;
        } else if (password && confirmPassword !== password) {
            showError('confirmPasswordError', 'Passwords do not match.');
            valid = false;
        }

        // Age: integer 18-120
        var ageNum = parseInt(age, 10);
        if (!age) {
            showError('ageError', 'Age is required.');
            valid = false;
        } else if (isNaN(ageNum) || ageNum < 18 || ageNum > 120) {
            showError('ageError', 'Age must be between 18 and 120.');
            valid = false;
        }

        if (valid) {
            form.style.display = 'none';
            var banner = document.getElementById('successBanner');
            var welcome = document.getElementById('welcomeMsg');
            welcome.textContent = 'Account created! Welcome, ' + username + '.';
            banner.style.display = 'block';
        }
    });
})();
