import apiClient from './client';

export interface Tour {
  id: number;
  title: string;
  description: string;
  price: number;
  duration: string;
  image_url: string;
  rating: number;
}

export const toursApi = {
  getPopularTours: async (): Promise<Tour[]> => {
    const response = await apiClient.get<Tour[]>('/tours/popular');
    return response.data;
  },

  getAllTours: async (): Promise<Tour[]> => {
    const response = await apiClient.get<Tour[]>('/tours');
    return response.data;
  },

  getTourById: async (id: number): Promise<Tour> => {
    const response = await apiClient.get<Tour>(`/tours/${id}`);
    return response.data;
  },
}; 