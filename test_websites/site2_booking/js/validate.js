(function () {
    'use strict';
    var form = document.getElementById('bookingForm');

    function clearErrors() {
        var msgs = form.querySelectorAll('.error-msg');
        for (var i = 0; i < msgs.length; i++) msgs[i].textContent = '';
    }

    function showError(id, msg) {
        var el = document.getElementById(id);
        if (el) el.textContent = msg;
    }

    function parseDate(str) {
        var parts = str.split('-');
        return new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
    }

    function todayStr() {
        var d = new Date();
        var mm = ('0' + (d.getMonth() + 1)).slice(-2);
        var dd = ('0' + d.getDate()).slice(-2);
        return d.getFullYear() + '-' + mm + '-' + dd;
    }

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        clearErrors();
        var valid = true;

        var checkin = form.querySelector('#checkin').value.trim();
        var checkout = form.querySelector('#checkout').value.trim();
        var guests = form.querySelector('#guests').value.trim();
        var room = form.querySelector('#room').value;
        var email = form.querySelector('#email').value.trim();

        // Check-in date
        if (!checkin) {
            showError('checkinError', 'Check-in date is required.');
            valid = false;
        } else if (checkin < todayStr()) {
            showError('checkinError', 'Check-in date cannot be in the past.');
            valid = false;
        }

        // Check-out date
        if (!checkout) {
            showError('checkoutError', 'Check-out date is required.');
            valid = false;
        } else if (checkin && checkout <= checkin) {
            showError('checkoutError', 'Check-out must be after check-in date.');
            valid = false;
        }

        // Guests
        var guestsNum = parseInt(guests, 10);
        if (!guests) {
            showError('guestsError', 'Number of guests is required.');
            valid = false;
        } else if (isNaN(guestsNum) || guestsNum < 1 || guestsNum > 10) {
            showError('guestsError', 'Guests must be between 1 and 10.');
            valid = false;
        }

        // Room type
        if (!room) {
            showError('roomError', 'Please select a room type.');
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

        if (valid) {
            var ref = 'BK' + Math.random().toString(36).substring(2, 8).toUpperCase();
            window.location.href = 'confirmed.html?ref=' + ref;
        }
    });
})();
