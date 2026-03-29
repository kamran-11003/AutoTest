(function () {
    'use strict';
    var form = document.getElementById('feedbackForm');
    var commentInput = document.getElementById('comment');
    var charCounter = document.getElementById('charCount');

    // Live character counter for comment
    if (commentInput) {
        commentInput.addEventListener('input', function () {
            charCounter.textContent = commentInput.value.length;
        });
    }

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

        // Name (required)
        var name = form.querySelector('#name').value.trim();
        if (!name) {
            showError('nameError', 'Full name is required.');
            valid = false;
        }

        // Email (optional, but must be valid if provided)
        var email = form.querySelector('#email').value.trim();
        if (email) {
            var emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRe.test(email)) {
                showError('emailError', 'Please enter a valid email address.');
                valid = false;
            }
        }

        // Rating (required — at least one radio selected)
        var ratingSelected = form.querySelector('input[name="rating"]:checked');
        if (!ratingSelected) {
            showError('ratingError', 'Please select a rating.');
            valid = false;
        }

        // Categories (at least one checkbox checked)
        var checked = form.querySelectorAll('input[name="categories"]:checked');
        if (checked.length === 0) {
            showError('categoriesError', 'Please select at least one feedback category.');
            valid = false;
        }

        // Comment (optional, max 300)
        var comment = form.querySelector('#comment').value;
        if (comment.length > 300) {
            showError('commentError', 'Comment must not exceed 300 characters.');
            valid = false;
        }

        // Phone (optional, 7-15 digits if provided — strip non-digits for counting)
        var phone = form.querySelector('#phone').value.trim();
        if (phone) {
            var digitsOnly = phone.replace(/\D/g, '');
            if (digitsOnly.length < 7 || digitsOnly.length > 15) {
                showError('phoneError', 'Phone number must be between 7 and 15 digits.');
                valid = false;
            }
        }

        if (valid) {
            window.location.href = 'thank-you.html';
        }
    });
})();
