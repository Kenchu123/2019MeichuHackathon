// for render image
import React from 'react'

class Img extends React.Component {
    constructor(props) {
        super(props)
    }
    render() {
        return (
            <div>
                {this.props.url === '' ? '' : <img src={this.props.url} />}
            </div>
        )
    }
}

export default Img