import React from 'react';
import { Box, Container, Typography, Grid, Link } from '@mui/material';

const Footer: React.FC = () => {
  return (
    <Box
      component="footer"
      sx={{
        bgcolor: 'primary.main',
        color: 'white',
        py: 6,
        mt: 'auto',
      }}
    >
      <Container maxWidth="lg">
        <Grid container spacing={4}>
          <Grid item xs={12} sm={4}>
            <Typography variant="h6" gutterBottom>
              Вкусные маршруты
            </Typography>
            <Typography variant="body2">
              Откройте для себя гастрономические сокровища России вместе с нами
            </Typography>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Typography variant="h6" gutterBottom>
              Контакты
            </Typography>
            <Typography variant="body2">
              Email: info@tastyroutes.ru
              <br />
              Телефон: +7 (999) 123-45-67
            </Typography>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Typography variant="h6" gutterBottom>
              Полезные ссылки
            </Typography>
            <Link href="/tours" color="inherit" display="block">
              Все туры
            </Link>
            <Link href="/about" color="inherit" display="block">
              О нас
            </Link>
            <Link href="/contact" color="inherit" display="block">
              Связаться с нами
            </Link>
          </Grid>
        </Grid>
        <Box mt={4} pt={3} borderTop={1} borderColor="rgba(255,255,255,0.1)">
          <Typography variant="body2" align="center">
            © {new Date().getFullYear()} Вкусные маршруты. Все права защищены.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};

export default Footer; 