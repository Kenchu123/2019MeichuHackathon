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
            uploadStatus: '',
        }
        this.uploadPDF = this.uploadPDF.bind(this)
        this.pdf = null
    }
    uploadPDF(e) {
        e.preventDefault()
        let file = e.target.files[0]
        if (file.type !== "application/pdf") {
            console.error(file.name, 'is not a pdf file.')
            return
        }
        // open uploaded file
        let fileReader = new FileReader()
        fileReader.onload = (e) => {
            this.setState({ uploadStatus: 'Loading...' })
            
            // load pdf with pdf js
            let typedarray = new Uint8Array(e.target.result)
            pdfjsLib.getDocument(typedarray).promise.then(pdf => {
                // upload finish
                this.pdf = pdf
                this.setState({ uploadStatus: '' })
            }, (err) => {
                this.setState({ uploadStatus: 'Fail to upload!!'})
                console.error(err)
            })
        }
        fileReader.readAsArrayBuffer(file)
    }
    render() {
        let pdfViewer
        if (this.state.uploadStatus !== '') {
            pdfViewer = <p>{this.state.uploadStatus}</p>
        }
        else if (this.pdf){
            pdfViewer = <PDFViewer pdf={this.pdf} />
        }

        return (
            <div>
                <h3>Upload datasheet and try to get your microchip!</h3>
                <p></p>
                <input type='file' accept="application/pdf" onChange={e => this.uploadPDF(e)}></input>
                <br />
                {pdfViewer}
            </div>
        )
    }
    
}

export default PDFManager