import React from 'react'

class MouseDraw extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            last_mouseY: 0,
            last_mouseX: 0,
            mouseIsDown: false,
        }
        this.drawRef = React.createRef()
        this.mouseDown = this.mouseDown.bind(this)
        this.mouseUp = this.mouseUp.bind(this)
        this.mouseMove = this.mouseMove.bind(this)
    }

    componentDidMount() {
        console.log(this.props)
    }

    mouseDown(e) {
        console.log('mouseDown')
        let canvas = this.drawRef.current
        const canPos = canvas.getBoundingClientRect()
        this.state.last_mouseX = parseInt(e.clientX - canPos.left)
        this.state.last_mouseY = parseInt(e.clientY - canPos.top)
        this.state.mouseIsDown = true
    }

    mouseUp(e) {
        console.log('mouseUp')
        this.state.mouseIsDown = false
    }

    mouseMove(e) {
        let canvas = this.drawRef.current
        const ctx = canvas.getContext('2d')
        console.log(canvas)
        if (this.state.mouseIsDown) {
            ctx.clearRect(0, 0, canvas.width, canvas.height)
            ctx.beginPath()
            let width = e.clientX - this.state.last_mouseX - canvas.getBoundingClientRect().left
            let height = e.clientY - this.state.last_mouseY - canvas.getBoundingClientRect().top
            ctx.rect(this.state.last_mouseX, this.state.last_mouseY, width, height)
            ctx.strokeStyle = 'black'
            ctx.lineWidth = 3
            ctx.stroke()
        }
    }
    render() {
        return (
            <canvas
                ref={this.drawRef}
                width={this.props.width}
                height={this.props.height}
                style={{border: '1px solid'}}
                onMouseDown={e => this.mouseDown(e)}
                onMouseMove={e => this.mouseMove(e)}
                onMouseUp={e => this.mouseUp(e)}
            />
        )
    }
}

export default MouseDraw