// for rendering pdf
import React from 'react'
import pdfjsLib from 'pdfjs-dist'
import PDFViewer from './PDFViewer'

// The workerSrc property shall be specified.
pdfjsLib.GlobalWorkerOptions.workerSrc = '//mozilla.github.io/pdf.js/build/pdf.worker.js';

class PDFManager extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            isRead: false,
            isUploading: false
        }
        this.uploadPDF = this.uploadPDF.bind(this)
        this.pdf = null
    }
    uploadPDF() {
        console.log("uploading pdf")
        let url = '/ds093.pdf'
        this.setState({ isUploading: true })
        pdfjsLib.getDocument(url).promise.then(pdf => {
            this.pdf = pdf
            this.setState({
                isRead: true,
                isUploading: false
            })
            console.log("upload finish!")
        }, (err) => {
            console.error(err)
        })
    }
    render() {
        let pdfViewer
        if (this.state.isUploading) {
            pdfViewer = <p>Loading...</p>
        }
        else if (this.state.isRead && !this.state.isUploading) {
            pdfViewer = <PDFViewer pdf={this.pdf} />
        }

        return (
            <div>
                <p>This is for pdf</p>
                <button onClick={this.uploadPDF}>Click to upload pdf</button>
                {pdfViewer}
            </div>
        )
    }
    
}

export default PDFManager