// for rendering pdf
import React from 'react'
import pdfjsLib from 'pdfjs-dist'

class PDFViewer extends React.Component {
    constructor(props) {
        super(props)
        this.pageRef = React.createRef();
        this.state = {
            pageNum: 1
        }
        this.setPage = this.setPage.bind(this)
        this.renderPDF = this.renderPDF.bind(this)
    }
    setPage(n) {
        let { pdf } = this.props
        let { pageNum } = this.state
        console.log(pdf)
        if (pageNum + n >= 1 && pageNum + n <= pdf.numPages) {
            this.setState({pageNum: pageNum + n})
        }
    }

    renderPDF() {
        let { pdf } = this.props
        let { pageNum } = this.state
        pdf.getPage(pageNum).then(page => {
            let scale = 1
            let viewport = page.getViewport({scale: scale})
            let canvas = this.pageRef.current
            canvas.height = viewport.height
            canvas.width = viewport.width
            var context = canvas.getContext('2d')

            // Render PDF page into canvas context
            let renderContext = {
                canvasContext: context,
                viewport: viewport
            }

            let renderTask = page.render(renderContext);
            renderTask.promise.then(function () {
                console.log('Page rendered');
            })

        })
    }

    render() {
        this.renderPDF()
        return (
            <div id='viewer'>
                <button onClick={() => this.setPage(-1)}>Prev</button>
                <button onClick={() => this.setPage(1)}>Next</button>
                <br />
                <canvas ref={this.pageRef} />
            </div>
        )
    }
    
}

export default PDFViewer