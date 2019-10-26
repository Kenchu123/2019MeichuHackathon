import React from 'react';
import PDFManager from './PDFManager';
import ResponsiveDrawer from './ResponsiveDrawer';

const App = () => (
  <div className="App">
    <ResponsiveDrawer>
      <PDFManager />
    </ResponsiveDrawer>
  </div>
);

export default App;
