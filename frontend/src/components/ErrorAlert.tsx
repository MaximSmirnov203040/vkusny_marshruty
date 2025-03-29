import React from 'react';
import { Alert, AlertTitle, Box } from '@mui/material';
import { motion } from 'framer-motion';

interface ErrorAlertProps {
  message: string;
  title?: string;
  onClose?: () => void;
}

const ErrorAlert: React.FC<ErrorAlertProps> = ({
  message,
  title = 'Ошибка',
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
        <Alert severity="error" onClose={onClose}>
          <AlertTitle>{title}</AlertTitle>
          {message}
        </Alert>
      </motion.div>
    </Box>
  );
};

export default ErrorAlert; 