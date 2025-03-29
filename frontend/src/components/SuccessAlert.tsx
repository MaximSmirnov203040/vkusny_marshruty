import React from 'react';
import { Alert, AlertTitle, Box } from '@mui/material';
import { motion } from 'framer-motion';

interface SuccessAlertProps {
  message: string;
  title?: string;
  onClose?: () => void;
}

const SuccessAlert: React.FC<SuccessAlertProps> = ({
  message,
  title = 'Успешно',
  onClose,
}) => {
  return (
    <Box mb={2}>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3 }}
      >
        <Alert severity="success" onClose={onClose}>
          <AlertTitle>{title}</AlertTitle>
          {message}
        </Alert>
      </motion.div>
    </Box>
  );
};

export default SuccessAlert; 