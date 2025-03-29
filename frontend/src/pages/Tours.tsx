import { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardMedia,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Slider,
  Chip,
  Stack,
} from '@mui/material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const MotionBox = motion(Box);

const tours = [
  {
    id: 1,
    title: 'Гастрономический тур по Москве',
    description: 'Откройте для себя лучшие рестораны и кафе столицы',
    image: '/images/moscow-food.jpg',
    price: 5000,
    duration: '3 дня',
    category: 'Гастрономический',
    rating: 4.8,
  },
  {
    id: 2,
    title: 'Винный тур по Крыму',
    description: 'Посещение лучших виноделен и дегустация местных вин',
    image: '/images/crimea-wine.jpg',
    price: 8000,
    duration: '5 дней',
    category: 'Винный',
    rating: 4.9,
  },
  {
    id: 3,
    title: 'Кулинарный мастер-класс в Санкт-Петербурге',
    description: 'Научитесь готовить блюда русской кухни у лучших шеф-поваров',
    image: '/images/spb-cooking.jpg',
    price: 3000,
    duration: '1 день',
    category: 'Мастер-класс',
    rating: 4.7,
  },
  // Добавьте больше туров по необходимости
];

const categories = ['Все', 'Гастрономический', 'Винный', 'Мастер-класс', 'Фермерский'];

const Tours = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('Все');
  const [priceRange, setPriceRange] = useState<number[]>([0, 10000]);

  const filteredTours = tours.filter((tour) => {
    const matchesSearch = tour.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tour.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'Все' || tour.category === selectedCategory;
    const matchesPrice = tour.price >= priceRange[0] && tour.price <= priceRange[1];
    return matchesSearch && matchesCategory && matchesPrice;
  });

  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom sx={{ mt: 4 }}>
        Все туры
      </Typography>

      {/* Filters */}
      <Box sx={{ mb: 4 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Поиск туров"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Категория</InputLabel>
              <Select
                value={selectedCategory}
                label="Категория"
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                {categories.map((category) => (
                  <MenuItem key={category} value={category}>
                    {category}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography gutterBottom>Ценовой диапазон</Typography>
            <Slider
              value={priceRange}
              onChange={(_, newValue) => setPriceRange(newValue as number[])}
              valueLabelDisplay="auto"
              min={0}
              max={10000}
              step={100}
            />
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2">{priceRange[0]} ₽</Typography>
              <Typography variant="body2">{priceRange[1]} ₽</Typography>
            </Box>
          </Grid>
        </Grid>
      </Box>

      {/* Tours Grid */}
      <Grid container spacing={4}>
        {filteredTours.map((tour) => (
          <Grid item xs={12} sm={6} md={4} key={tour.id}>
            <MotionBox
              whileHover={{ y: -10 }}
              transition={{ duration: 0.3 }}
            >
              <Card sx={{ height: '100%' }}>
                <CardMedia
                  component="img"
                  height="200"
                  image={tour.image}
                  alt={tour.title}
                />
                <CardContent>
                  <Typography gutterBottom variant="h5" component="h3">
                    {tour.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {tour.description}
                  </Typography>
                  <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
                    <Chip label={tour.category} size="small" />
                    <Chip label={tour.duration} size="small" />
                    <Chip label={`${tour.rating} ★`} size="small" color="primary" />
                  </Stack>
                  <Typography variant="h6" color="primary" gutterBottom>
                    от {tour.price} ₽
                  </Typography>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => navigate(`/tours/${tour.id}`)}
                    fullWidth
                  >
                    Подробнее
                  </Button>
                </CardContent>
              </Card>
            </MotionBox>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default Tours; 