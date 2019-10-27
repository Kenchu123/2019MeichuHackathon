// for rendering pdf
import React from 'react';
import pdfjsLib from 'pdfjs-dist';
import Button from '@material-ui/core/Button';
import CloudUploadIcon from '@material-ui/icons/CloudUpload';
import Typography from '@material-ui/core/Typography';
import CircularProgress from '@material-ui/core/CircularProgress';

// The workerSrc property shall be specified.
pdfjsLib.GlobalWorkerOptions.workerSrc =
  '//mozilla.github.io/pdf.js/build/pdf.worker.js';

const UPLOAD_STATUS = { PENDING: 0, LOADING: 1, FINISHED: 2, FAILED: 3 };
class PDFManager extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      uploadStatus: UPLOAD_STATUS.PENDING,
      pdf: null
    };
    this.uploadPDF = this.uploadPDF.bind(this);
  }

  uploadPDF(e) {
    e.preventDefault();
    let file = e.target.files[0];
    if (file.type !== 'application/pdf') {
      console.error(file.name, 'is not a pdf file.');
      return;
    }
    // open uploaded file
    let fileReader = new FileReader();
    fileReader.onload = e => {
      this.setState({ uploadStatus: UPLOAD_STATUS.LOADING });

      // load pdf with pdf js
      let typedarray = new Uint8Array(e.target.result);
      pdfjsLib
        .getDocument(typedarray)
        .promise.then(pdf => {
          // upload finish
          this.props.updatePdf(pdf);
          this.props.nextPage();
          // this.setState({ uploadStatus: UPLOAD_STATUS.FINISHED, pdf });
        })
        .catch(err => {
          this.setState({ uploadStatus: UPLOAD_STATUS.FAILED });
          console.error(err);
        });
    };
    fileReader.readAsArrayBuffer(file);

    // pass to server
    let formData = new FormData();
    formData.append('pdf', file);
    fetch('/api/download', {
      method: 'POST',
      body: formData
    }).then(res => {
      console.log(res.json);
    });
  }

  render() {
    let pdfViewer;
    return (
      <div>
        <Typography gutterBottom variant="h2">
          Upload File
        </Typography>
        <Typography paragraph variant="h5">
          Upload datasheet and select the desired area to parse
        </Typography>
        <Button
          variant="contained"
          color="default"
          startIcon={<CloudUploadIcon />}
          component="label"
          style={{ margin: '8px' }}
        >
          <input
            id="file-upload"
            type="file"
            accept="application/pdf"
            onChange={this.uploadPDF}
            style={{ display: 'none' }}
          />
          {this.state.uploadStatus === UPLOAD_STATUS.LOADING ? (
            <div
              style={{
                width: '61px',
                display: 'flex',
                justifyContent: 'center'
              }}
            >
              <CircularProgress color="primary" size={24} />
            </div>
          ) : (
            'Upload'
          )}
        </Button>
      </div>
    );
  }
}

export default PDFManager;
