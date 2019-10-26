import React from 'react';
import Typography from '@material-ui/core/Typography';

class PinInfo extends React.Component {
  render() {
    return (
      <div>
        <Typography variant="h2" gutterBottom>
          A0-A12
        </Typography>
        <Typography paragraph variant="h5">
          Row Address Input
        </Typography>
        <Typography gutterBottom variant="h3">
          Type
        </Typography>
        <Typography paragraph variant="body1" style={{ fontSize: '1.3rem' }}>
          Input Pin
        </Typography>
        <Typography gutterBottom variant="h3">
          Function (In Detail)
        </Typography>
        <Typography paragraph variant="body1" style={{ fontSize: '1.3rem' }}>
          Address Inputs: A0-A12 are sampled during the ACTIVE command
          (row-address A0-A12) and READ/WRITE command (column address A0-A9
          (x8), or A0-A8 (x16); with A10 defining auto precharge) to select one
          location out of the memory array in the respective bank. A10 is
          sampled during a PRECHARGE command to determine if all banks are to be
          precharged (A10 HIGH) or bank selected by BA0, BA1 (LOW). The address
          inputs also provide the op-code during a LOAD MODE REGISTER command.
        </Typography>
      </div>
    );
  }
}

export default PinInfo;
