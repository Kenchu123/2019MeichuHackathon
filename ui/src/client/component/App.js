import React from 'react';
import PDFManager from './PDFManager';
import PDFViewer from './PDFViewer';
import ResponsiveDrawer from './ResponsiveDrawer';
import MicroChip from './MicroChip';

const pages = [PDFManager, PDFViewer];

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = { page: 0, pdf: null };
    this.nextPage = this.nextPage.bind(this);
    this.updatePdf = this.updatePdf.bind(this);
  }

  nextPage() {
    if (this.state.page + 1 < pages.length)
      this.setState({ page: this.state.page + 1 });
  }

  updatePdf(pdf) {
    this.setState({ pdf });
  }

  render() {
    const Page = pages[this.state.page];
    return (
      <div className="App">
        <ResponsiveDrawer>
          <Page
            nextPage={this.nextPage}
            updatePdf={this.updatePdf}
            pdf={this.state.pdf}
          />
        </ResponsiveDrawer>
      </div>
    );
  }
}

export default App;
