import React from 'react';

class MouseDraw extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      startX: 0,
      startY: 0,
      endX: 0,
      endY: 0,
      mouseIsDown: false
    };
    this.drawRef = React.createRef();
    this.mouseDown = this.mouseDown.bind(this);
    this.mouseUp = this.mouseUp.bind(this);
    this.mouseMove = this.mouseMove.bind(this);
  }

  shouldComponentUpdate(nextProps, nextState) {
    return (
      this.props.width !== nextProps.width ||
      this.props.height !== nextProps.height
    );
  }

  mouseDown(e) {
    let canvas = this.drawRef.current;
    const canPos = canvas.getBoundingClientRect();
    this.setState({
      startX: parseInt(e.clientX - canPos.left),
      startY: parseInt(e.clientY - canPos.top),
      mouseIsDown: true
    });
  }

  mouseUp(e) {
    this.setState({ mouseIsDown: false });
  }

  mouseMove(e) {
    let canvas = this.drawRef.current;
    const ctx = canvas.getContext('2d');
    if (e.buttons === 1) {
      // left click
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.beginPath();
      const canPos = canvas.getBoundingClientRect();
      let width = e.clientX - this.state.startX - canPos.left;
      let height = e.clientY - this.state.startY - canPos.top;
      ctx.save();
      ctx.rect(this.state.startX, this.state.startY, width, height);
      ctx.strokeStyle = 'rgb(0,153,255)';
      ctx.lineWidth = 3;
      ctx.setLineDash([10, 15]);
      ctx.stroke();
      ctx.restore();
      this.setState({
        endX: e.clientX - canPos.left,
        endY: e.clientY - canPos.top
      });
    }
  }

  render() {
    return (
      <canvas
        ref={this.drawRef}
        width={this.props.width}
        height={this.props.height}
        style={{ border: '1px solid', position: 'absolute', left: 0 }}
        onMouseDown={this.mouseDown}
        onMouseMove={this.mouseMove}
        onMouseUp={this.mouseUp}
      />
    );
  }
}

export default MouseDraw;
