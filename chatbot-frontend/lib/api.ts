import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer $\{token}`;
  }
  return config;
});

export default api;

export const authAPI = {
  register: (email: string, password: string) => 
    api.post('/auth/register', { email, password }),
  login: (email: string, password: string) => 
    api.post('/auth/login', { email, password }),
};

export const chatAPI = {
  listChats: () => api.get('/chats'),
  createChat: (title: string) => api.post('/chats', { title }),
  getMessages: (chatId: number) => api.get(`/chats/$\{chatId}/messages`),
  deleteChat: (chatId: number) => api.delete(`/chats/$\{chatId}`),
};

export const fileAPI = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/files/upload', formData);
  },
  list: () => api.get('/files'),
  delete: (fileId: number) => api.delete(`/files/$\{fileId}`),
};

export const queryAPI = {
  query: (query: string, chatId?: number) => 
    api.post('/query', { query, chat_id: chatId }),
};
