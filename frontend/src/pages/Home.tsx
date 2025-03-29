import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Button,
  Rating,
  CircularProgress,
} from '@mui/material';
import { motion } from 'framer-motion';
import { toursApi, Tour } from '../api/tours';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [tours, setTours] = useState<Tour[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const fetchTours = async () => {
      try {
        const data = await toursApi.getPopularTours();
        setTours(data);
      } catch (err) {
        setError('Ошибка при загрузке туров. Пожалуйста, попробуйте позже.');
      } finally {
        setLoading(false);
      }
    };

    fetchTours();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box
        sx={{
          bgcolor: 'primary.main',
          color: 'white',
          py: 8,
          mb: 6,
        }}
      >
        <Container>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Typography variant="h2" component="h1" gutterBottom align="center">
              Вкусные маршруты
            </Typography>
            <Typography variant="h5" align="center" sx={{ mb: 4 }}>
              Откройте для себя гастрономические сокровища России
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
              <Button
                variant="contained"
                color="secondary"
                size="large"
                onClick={() => navigate('/tours')}
              >
                Смотреть все туры
              </Button>
              <Button
                variant="outlined"
                color="inherit"
                size="large"
                onClick={() => navigate('/tours')}
              >
                Подобрать тур
              </Button>
            </Box>
          </motion.div>
        </Container>
      </Box>

      <Container>
        <Typography variant="h4" component="h2" gutterBottom align="center" sx={{ mb: 4 }}>
          Популярные туры
        </Typography>

        {error ? (
          <Typography color="error" align="center">
            {error}
          </Typography>
        ) : (
          <Grid container spacing={4}>
            {tours.map((tour) => (
              <Grid item xs={12} sm={6} md={4} key={tour.id}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5 }}
                >
                  <Card
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      cursor: 'pointer',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        transition: 'transform 0.2s ease-in-out',
                      },
                    }}
                    onClick={() => navigate(`/tours/${tour.id}`)}
                  >
                    <CardMedia
                      component="img"
                      height="200"
                      image={tour.image_url}
                      alt={tour.title}
                    />
                    <CardContent sx={{ flexGrow: 1 }}>
                      <Typography gutterBottom variant="h6" component="h3">
                        {tour.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" paragraph>
                        {tour.description}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Rating value={tour.rating} readOnly precision={0.5} />
                        <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                          ({tour.rating})
                        </Typography>
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        Длительность: {tour.duration}
                      </Typography>
                      <Typography variant="h6" color="primary" sx={{ mt: 1 }}>
                        от {tour.price} ₽
                      </Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        )}
      </Container>
    </Box>
  );
};

export default Home; 