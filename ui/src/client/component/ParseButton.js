// for parseButton
import React from 'react'
import Button from '@material-ui/core/Button';
import CloudUploadIcon from '@material-ui/icons/CloudUpload';

// get pageNum (PDFViewer)
// get startX endX (MouseDraw)
// get url ('/api/parsetype/diagram') and '/api/parsetype/table'
// get name () 'Execute with Pin Diagram' 'Execute with Pin Table'
class ParseButton extends React.Component {
    constructor(props) {
        super(props)
        this.sendData = this.sendData.bind(this)
    }

    sendData() {
        const { type } = this.props // still have pageNum, startXY endXY
        const url = `/api/parsetype/${type}`
        const data = {
            type: type,
            ...this.props.data
        }
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(res => {
            console.log(res)
            return res.blob()
        })
        .then(imgBlob => {
            console.log(imgBlob)
            let url = URL.createObjectURL(imgBlob)
            // add image tag
            this.props.getImg(url)
        })
        .catch(err => console.error(err))
    }

    render () {
        return (
            <Button
                variant="contained"
                color="default"
                startIcon={<CloudUploadIcon />}
                component="label"
                onClick={e => this.sendData()}>
                    Execute Pin {this.props.type}
            </Button>
        )
    }
}

export default ParseButton