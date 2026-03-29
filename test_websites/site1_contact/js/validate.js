/**
 * Contact Form Validation — Site 1
 * All validation is in JavaScript (not HTML5 only).
 * Errors are DOM text in .error-msg divs.
 */
(function () {
    'use strict';

    var form = document.getElementById('contactForm');

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        clearErrors();

        var valid = true;

        // Name: 2-50 characters
        var name = form.name.value.trim();
        if (name.length < 2 || name.length > 50) {
            showError('name-error', 'Name must be 2-50 characters');
            valid = false;
        }

        // Email: basic regex
        var email = form.email.value.trim();
        var emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRe.test(email)) {
            showError('email-error', 'Enter a valid email address');
            valid = false;
        }

        // Subject: must be selected
        if (!form.subject.value) {
            showError('subject-error', 'Please select a subject');
            valid = false;
        }

        // Message: 10-500 characters
        var msg = form.message.value.trim();
        if (msg.length < 10 || msg.length > 500) {
            showError('message-error', 'Message must be 10-500 characters');
            valid = false;
        }

        if (valid) {
            window.location.href = 'success.html';
        }
    });

    function showError(id, text) {
        document.getElementById(id).textContent = text;
    }

    function clearErrors() {
        var msgs = document.querySelectorAll('.error-msg');
        for (var i = 0; i < msgs.length; i++) {
            msgs[i].textContent = '';
        }
    }
})();
