import React from 'react';
import { Typography, Box } from '@mui/material';
import { useParams } from 'react-router-dom';

const Booking: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <Box>
      <Typography variant="h2" gutterBottom>
        Бронирование тура
      </Typography>
      <Typography variant="body1">
        Здесь будет форма бронирования тура с ID: {id}
      </Typography>
    </Box>
  );
};

export default Booking; 