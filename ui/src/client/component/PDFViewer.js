// for rendering pdf
import React from 'react';
import MouseDraw from './MouseDraw';
import IconButton from '@material-ui/core/IconButton';
import Button from '@material-ui/core/Button';
import ChevronRightIcon from '@material-ui/icons/ChevronRight';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import Typography from '@material-ui/core/Typography';

class PDFViewer extends React.Component {
  constructor(props) {
    super(props);
    this.pageRef = React.createRef();
    this.state = {
      pageNum: 1,
      width: 0,
      height: 0
    };
    this.setPage = this.setPage.bind(this);
    this.renderPDF = this.renderPDF.bind(this);
    this.rect = new MouseDraw();
  }

  setPage(n) {
    let { pdf } = this.props;
    let { pageNum } = this.state;
    if (pageNum + n >= 1 && pageNum + n <= pdf.numPages) {
      this.setState({ pageNum: pageNum + n }, this.renderPDF);
    }
  }

  renderPDF() {
    let { pdf } = this.props;
    let { pageNum } = this.state;
    pdf.getPage(pageNum).then(page => {
      let scale = 1.2;
      let viewport = page.getViewport({ scale: scale });
      let canvas = this.pageRef.current;
      canvas.height = viewport.height;
      canvas.width = viewport.width;
      let context = canvas.getContext('2d');
      // context.clearRect(0, 0, canvas.width, canvas.height)

      // Render PDF page into canvas context
      let renderContext = {
        canvasContext: context,
        viewport: viewport
      };
      this.setState({
        height: viewport.height,
        width: viewport.width
      });
      page.render(renderContext);
    });
  }

  componentDidMount() {
    this.renderPDF();
  }

  render() {
    return (
      <div id="viewer">
        <Typography gutterBottom variant="h2">
          Select Area
        </Typography>
        <Typography paragraph variant="h5">
          Click and drag to select a desired area
        </Typography>
        <Button
          variant="contained"
          color="default"
          endIcon={<ChevronRightIcon />}
        >
          Next
        </Button>
        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <IconButton onClick={() => this.setPage(-1)}>
            <ChevronLeftIcon />
          </IconButton>
          <p>{`${this.state.pageNum} / ${this.props.pdf.numPages}`}</p>
          <IconButton onClick={() => this.setPage(1)}>
            <ChevronRightIcon />
          </IconButton>
        </div>
        <div id="viewer" className="container">
          <div style={{ position: 'relative' }}>
            <canvas ref={this.pageRef} />
            <MouseDraw width={this.state.width} height={this.state.height} />
          </div>
        </div>
      </div>
    );
  }
}

export default PDFViewer;
