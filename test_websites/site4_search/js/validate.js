(function () {
    'use strict';
    var form = document.getElementById('searchForm');

    function clearErrors() {
        var msgs = form.querySelectorAll('.error-msg');
        for (var i = 0; i < msgs.length; i++) msgs[i].textContent = '';
    }

    function showError(id, msg) {
        var el = document.getElementById(id);
        if (el) el.textContent = msg;
    }

    function randPrice(min, max) {
        return '$' + (Math.random() * (max - min) + min).toFixed(2);
    }

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        clearErrors();
        document.getElementById('results').style.display = 'none';
        var valid = true;

        var keywords = form.querySelector('#keywords').value.trim();
        var category = form.querySelector('#category').value;
        var minPriceVal = form.querySelector('#minPrice').value.trim();
        var maxPriceVal = form.querySelector('#maxPrice').value.trim();

        // Keywords: at least 2 chars
        if (!keywords) {
            showError('keywordsError', 'Keywords are required.');
            valid = false;
        } else if (keywords.length < 2) {
            showError('keywordsError', 'Keywords must be at least 2 characters.');
            valid = false;
        }

        // Category: required
        if (!category) {
            showError('categoryError', 'Please select a category.');
            valid = false;
        }

        // Min price: ≥0 if provided (defaults to 0)
        var minPrice = 0;
        if (minPriceVal !== '') {
            minPrice = parseFloat(minPriceVal);
            if (isNaN(minPrice) || minPrice < 0) {
                showError('minPriceError', 'Minimum price must be 0 or greater.');
                valid = false;
            }
        }

        // Max price: ≥ minPrice and ≤10000 if provided
        var maxPrice = 10000;
        if (maxPriceVal !== '') {
            maxPrice = parseFloat(maxPriceVal);
            if (isNaN(maxPrice) || maxPrice < 0) {
                showError('maxPriceError', 'Maximum price must be 0 or greater.');
                valid = false;
            } else if (maxPrice > 10000) {
                showError('maxPriceError', 'Maximum price cannot exceed $10,000.');
                valid = false;
            } else if (!isNaN(minPrice) && maxPrice < minPrice) {
                showError('maxPriceError', 'Maximum price must be greater than or equal to minimum price.');
                valid = false;
            }
        }

        if (valid) {
            // Populate dummy results
            var catLabel = category.charAt(0).toUpperCase() + category.slice(1);
            document.getElementById('resultMeta').textContent =
                'Showing results for "' + keywords + '" in ' + catLabel +
                ' ($' + minPrice.toFixed(2) + ' – $' + maxPrice.toFixed(2) + ')';

            var mid = (minPrice + maxPrice) / 2;
            var r1 = [minPrice, mid], r2 = [minPrice, mid], r3 = [mid, maxPrice];

            document.getElementById('r1Cat').textContent = catLabel;
            document.getElementById('r2Cat').textContent = catLabel;
            document.getElementById('r3Cat').textContent = catLabel;
            document.getElementById('r1Price').textContent = randPrice(r1[0], r1[1] || r1[0] + 1);
            document.getElementById('r2Price').textContent = randPrice(r2[0], r2[1] || r2[0] + 1);
            document.getElementById('r3Price').textContent = randPrice(r3[0], r3[1] || r3[0] + 1);

            document.getElementById('results').style.display = 'block';
        }
    });
})();
