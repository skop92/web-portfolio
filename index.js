const express = require('express');
const app = express();
const path = require('path');
const helmet = require('helmet');

app.use(express.static(path.join(__dirname, '/src')));
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, '/views'));

app.use(helmet());

const scriptSrcUrls = [
    "'unsafe-inline'",
];
const styleSrcUrls = [
    "https://fonts.googleapis.com",
    "'unsafe-inline'",
];
const connectSrcUrls = [];
const fontSrcUrls = [
	"https://fonts.gstatic.com",
];
const imgSrcUrls = [
	'blob:',
    'data:',
];
app.use(
    helmet.contentSecurityPolicy({
        directives: {
            defaultSrc: ["'self'"],
            connectSrc: ["'self'", ...connectSrcUrls],
            scriptSrc: ["'self'", ...scriptSrcUrls],
            styleSrc: ["'self'", ...styleSrcUrls],
            workerSrc: ["'self'", 'blob:'],
            childSrc: ['blob:'],
            objectSrc: [],
            imgSrc: ["'self'", ...imgSrcUrls],
            fontSrc: ["'self'", ...fontSrcUrls],
			//upgradeInsecureRequests: null // To allow http in local network
        }
    })
);

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

const port = process.env.PORT || 3000;
app.listen(port, () => {
	console.log(`LISTENING ON PORT ${port}`);
});
