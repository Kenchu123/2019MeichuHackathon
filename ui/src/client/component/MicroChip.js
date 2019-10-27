import React from 'react';
import data from './result.js';

class MicroChip extends React.Component {
  getCSS(textObject) {
    const [x0, y0, x1, y1] = textObject.bbox;
    if ((x1 - x0) / 612 >= (y1 - y0) / 792) {
      return {
        width: ((x1 - x0) / 612) * this.props.width,
        height: ((y1 - y0) / 792) * this.props.height,
        left: (x0 / 612) * this.props.width,
        top: ((792 - y0) / 792) * this.props.height
      };
    } else {
      return {
        height: ((x1 - x0) / 612) * this.props.width,
        width: ((y1 - y0) / 792) * this.props.height,
        left: (x0 / 612) * this.props.width,
        top: ((792 - y0) / 792) * this.props.height,
        transform: 'rotate(-90deg)'
      };
    }
  }

  rotation(isVertical) {
    return isVertical ? { transform: 'rotate(-90deg)' } : {};
  }

  render() {
    return (
      <div
        style={{
          position: 'relative',
          width: this.props.width,
          height: this.props.height
        }}
      >
        <img src="/public/test.png" />
        {Object.keys(data).map(id => (
          <div
            key={id}
            style={{
              position: 'absolute',
              background: 'blue',
              ...this.getCSS(data[id])
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
