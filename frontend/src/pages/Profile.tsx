import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Paper,
  Button,
} from '@mui/material';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';

const Profile: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated, logout } = useAuth();

  if (!isAuthenticated) {
    navigate('/login');
    return null;
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 8, mb: 4 }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Paper elevation={3} sx={{ p: 4 }}>
            <Typography variant="h4" component="h1" gutterBottom>
              Профиль пользователя
            </Typography>
            <Typography variant="body1" paragraph>
              Здесь будет информация о пользователе
            </Typography>
            <Button
              variant="contained"
              color="primary"
              onClick={logout}
              sx={{ mt: 2 }}
            >
              Выйти
            </Button>
          </Paper>
        </motion.div>
      </Box>
    </Container>
  );
};

export default Profile; 