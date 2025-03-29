import React from 'react';
import { Typography, Box } from '@mui/material';
import { useParams } from 'react-router-dom';

const TourDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <Box>
      <Typography variant="h2" gutterBottom>
        Детали тура
      </Typography>
      <Typography variant="body1">
        Здесь будет информация о туре с ID: {id}
      </Typography>
    </Box>
  );
};

export default TourDetails; 