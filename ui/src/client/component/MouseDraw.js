import React from 'react'

class MouseDraw {
    constructor() {
        this.last_mouseX = 0
        this.last_mouseY = 0
        this.mouseIsDown = false
    }

    mouseDown(e, canvas) {
        console.log('mouseDown')
        const canPos = canvas.getBoundingClientRect()
        this.last_mouseX = parseInt(e.clientX - canPos.left)
        this.last_mouseY = parseInt(e.clientY - canPos.top)
        this.mouseIsDown = true
    }

    mouseUp(e, canvas) {
        console.log('mouseUp')
        this.mouseIsDown = false
    }

    mouseMove(e, canvas) {
        const ctx = canvas.getContext('2d')

        if (this.mouseIsDown) {
            ctx.clearRect(0, 0, canvas.width, canvas.height)
            ctx.beginPath()
            let width = e.clientX - this.last_mouseX - canvas.getBoundingClientRect().left;
            let height = e.clientY - this.last_mouseY - canvas.getBoundingClientRect().top;
            ctx.rect(this.last_mouseX, this.last_mouseY, width, height);
            ctx.strokeStyle = 'black';
            ctx.lineWidth = 10;
            ctx.stroke();
        }
    }
}

export default MouseDraw