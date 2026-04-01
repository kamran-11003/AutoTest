const express = require('express');
const path = require('path');

const app = express();
const PORT = 3008;

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(express.static(path.join(__dirname, 'public')));

app.get('/',                  (_req, res) => res.render('index'));
app.get('/doctors',           (_req, res) => res.render('doctors'));
app.get('/appointment',       (_req, res) => res.render('appointment'));
app.get('/patient-register',  (_req, res) => res.render('patient-register'));

app.listen(PORT, () => {
  console.log(`site8_medical (Express+EJS) running at http://localhost:${PORT}`);
});
