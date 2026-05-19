export const setToken = (accessToken: string, refreshToken: string) => {
  if (typeof window === 'undefined') return;
  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('refresh_token', refreshToken);
};

export const getToken = () => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
};

export const clearTokens = () => {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

export const isAuthenticated = () => {
  return !!getToken();
};
