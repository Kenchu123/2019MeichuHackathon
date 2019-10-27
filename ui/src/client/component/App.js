import React from 'react';
import PDFManager from './PDFManager';
import ResponsiveDrawer from './ResponsiveDrawer';
import MicroChip from './MicroChip';

const App = () => (
  <div className="App">
    <ResponsiveDrawer>
      <MicroChip width="1224" height="1584" />
      <PDFManager />
    </ResponsiveDrawer>
  </div>
);

export default App;
