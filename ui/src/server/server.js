const express = require('express');
const webpack = require('webpack');
const webpackDevMiddleware = require('webpack-dev-middleware');
const webpackConfig = require('../../webpack.dev.js');

const spawn = require('child_process').spawn;
const multer = require('multer');
const upload = multer({ dest: '../../uploads/' });

const fs = require('fs');

// Setup an Express server
const app = express();
app.use(express.static('public'));

if (process.env.NODE_ENV === 'development') {
  // Setup Webpack for development
  const compiler = webpack(webpackConfig);
  app.use(webpackDevMiddleware(compiler));
} else {
  // Static serve the dist/ folder in production
  app.use(express.static('dist'));
}

// api
// download pdf, store in ui/uploads
app.post('/api/download', upload.single('pdf'), (req, res, next) => {
  let file = req.file;
  if (!file) {
    const err = new Error('Please upload a file');
    err.httpStatusCode = 400;
    return next(err);
  }
  fs.readFile(file.path, (err, data) => {
    fs.writeFile(`../uploads/${file.originalname}`, data, err => {
      if (err) console.log(err);
    });
  });

  res.send({ success: true });
});
// for get user input (which is pdf place)

// Listen on port
const port = process.env.PORT || 3000;
const server = app.listen(port);
console.log(`Server listening on port ${port}`);

// python process
// const pythonProcess = spawn('python3', ['./test.py'])
// pythonProcess.stdout.on('data', data => {
//   console.log(data.toString())
// })
