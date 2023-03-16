const express = require('express');
const app = express();
const path = require('path');

app.use(express.static(path.join(__dirname, '/src')));
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, '/views'));


/* GET */

app.get('/', (req, res) => {
	res.render('home', { active: "home" } );
});

app.get('/portfolio', (req, res) => {
	res.render('portfolio', { active: "portfolio" } );
});

app.get('/portfolio-articles/:article', (req, res) => {
	//console.log(req.params);
	const { article } = req.params;
	res.render(article, { active: "article" } );
});

app.listen(3000, () => {
	console.log("LISTENING ON PORT 3000");
});
