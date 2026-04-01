/**
 * Site 8 — Medical Clinic Validation (appointment + patient)
 * Complex: no-Sunday dates, past DOB, phone pattern.
 */
(function () {
    'use strict';

    function showError(id, text) { document.getElementById(id).textContent = text; }
    function clearErrors() {
        var msgs = document.querySelectorAll('.error-msg');
        for (var i = 0; i < msgs.length; i++) msgs[i].textContent = '';
    }
    var emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    /* ── Appointment form ── */
    var af = document.getElementById('appointmentForm');
    if (af) {
        af.addEventListener('submit', function (e) {
            e.preventDefault(); clearErrors(); var valid = true;
            if (!af.doctor.value) { showError('doctor-error', 'Please select a doctor'); valid = false; }
            var d = af.appDate.value;
            if (!d) { showError('appDate-error', 'Appointment date is required'); valid = false; }
            else {
                var sel = new Date(d), today = new Date(); today.setHours(0,0,0,0);
                if (sel < today) { showError('appDate-error', 'Date cannot be in the past'); valid = false; }
                else if (sel.getDay() === 0) { showError('appDate-error', 'Clinic is closed on Sundays'); valid = false; }
            }
            if (!af.appTime.value) { showError('appTime-error', 'Please select a time'); valid = false; }
            if (!af.visitType.value) { showError('visitType-error', 'Please select a visit type'); valid = false; }
            var r = af.reason.value.trim();
            if (r.length < 10 || r.length > 300) { showError('reason-error', 'Reason must be 10-300 characters'); valid = false; }
            if (valid) { af.style.display = 'none'; document.getElementById('appointmentSuccess').style.display = 'block'; }
        });
    }

    /* ── Patient registration form ── */
    var pf = document.getElementById('patientForm');
    if (pf) {
        pf.addEventListener('submit', function (e) {
            e.preventDefault(); clearErrors(); var valid = true;
            var fn = pf.firstName.value.trim();
            if (fn.length < 2 || fn.length > 30) { showError('firstName-error', 'First name must be 2-30 characters'); valid = false; }
            var ln = pf.lastName.value.trim();
            if (ln.length < 2 || ln.length > 30) { showError('lastName-error', 'Last name must be 2-30 characters'); valid = false; }
            var dob = pf.dob.value;
            if (!dob) { showError('dob-error', 'Date of birth is required'); valid = false; }
            else {
                var dd = new Date(dob), now = new Date();
                if (dd >= now) { showError('dob-error', 'Date of birth must be in the past'); valid = false; }
                else if (now.getFullYear() - dd.getFullYear() > 120) { showError('dob-error', 'Age cannot exceed 120 years'); valid = false; }
            }
            if (!pf.gender.value) { showError('gender-error', 'Please select a gender'); valid = false; }
            if (!/^\d{10,15}$/.test(pf.patientPhone.value.trim())) { showError('patientPhone-error', 'Phone must be 10-15 digits'); valid = false; }
            if (!emailRe.test(pf.patientEmail.value.trim())) { showError('patientEmail-error', 'Enter a valid email address'); valid = false; }
            var ec = pf.emergencyContact.value.trim();
            if (ec.length < 2 || ec.length > 50) { showError('emergencyContact-error', 'Emergency contact must be 2-50 characters'); valid = false; }
            if (!pf.bloodType.value) { showError('bloodType-error', 'Please select a blood type'); valid = false; }
            if (valid) { pf.style.display = 'none'; document.getElementById('patientSuccess').style.display = 'block'; }
        });
    }
})();
