import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцептор для добавления токена авторизации
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Интерцептор для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Типы данных
export interface Tour {
  id: number;
  title: string;
  description: string;
  price: number;
  duration: number;
  image_url: string;
  location: string;
  rating: number;
  max_participants: number;
  available_dates: string[];
}

export interface User {
  id: number;
  email: string;
  name: string;
  role: 'user' | 'admin';
}

export interface Booking {
  id: number;
  tour_id: number;
  user_id: number;
  date: string;
  status: 'pending' | 'confirmed' | 'cancelled';
  participants: number;
  total_price: number;
}

// API методы
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  register: (username: string, email: string, password: string) =>
    api.post('/auth/register', { username, email, password }),
  getProfile: () => api.get('/auth/profile'),
};

export const toursAPI = {
  getAll: () => api.get('/tours'),
  getById: (id: number) => api.get(`/tours/${id}`),
  search: (query: string) => api.get(`/tours/search?q=${query}`),
  filter: (params: Record<string, any>) =>
    api.get('/tours/filter', { params }),
};

export const bookingsAPI = {
  create: (tourId: number, date: string, participants: number) =>
    api.post('/bookings', { tour_id: tourId, date, participants }),
  getMyBookings: () => api.get('/bookings/my'),
  cancel: (id: number) => api.post(`/bookings/${id}/cancel`),
};

export default api; 