import React from 'react';
import data from './result.js';

class MicroChip extends React.Component {
  getCSS(textObject, mouseXY) {
    const [x0, y0, x1, y1] = textObject.bbox;
    const { startX, startY, endX, endY } = mouseXY;
    if ((x1 - x0) / 612 >= (y1 - y0) / 792) {
      return {
        width: `${((x1 - x0) / 612) * this.props.width * 1.4}px`,
        height: `${((y1 - y0) / 792) * this.props.height * 1.4}px`,
        left: `${((x0 / 612) * this.props.width - startX) * 1.4}px`,
        top: `${(((792 - y1) / 792) * this.props.height - startY) * 1.4}px`
      };
    } else {
      return {
        height: `${((x1 - x0) / 612) * this.props.width * 1.4}px`,
        width: `${((y1 - y0) / 792) * this.props.height * 1.4}px`,
        left: `${((x0 / 612) * this.props.width - startX) * 1.4}px`,
        top: `${(((792 - y1) / 792) * this.props.height - startY) * 1.4}px`,
        transform: 'rotate(-90deg)'
      };
    }
  }

  rotation(isVertical) {
    return isVertical ? { transform: 'rotate(-90deg)' } : {};
  }

  render() {
    if (!this.props.show) return '';
    return (
      <div
        style={{
          position: 'relative',
          width: this.props.width,
          height: this.props.height
        }}
      >
        {/* <img
          src={this.props.imgUrl}
          width={parseInt(this.props.width)}
          height={parseInt(this.props.height)}
        /> */}
        {Object.keys(data).map(id => (
          <div
            key={id}
            style={{
              position: 'absolute',
              background: 'rgb(0,153,255)',
              ...this.getCSS(data[id], this.props.mouseXY)
            }}
          >
            {data[id].text}
          </div>
        ))}
      </div>
    );
  }
}

export default MicroChip;
