import { useAuthStore } from '../features/auth/authStore';

describe('Auth Store', () => {
  it('should start with null access token', () => {
    const state = useAuthStore.getState();
    expect(state.accessToken).toBeNull();
  });

  it('should set access token', () => {
    useAuthStore.getState().setAccessToken('test-token');
    expect(useAuthStore.getState().accessToken).toBe('test-token');
  });

  it('should clear access token', () => {
    useAuthStore.getState().setAccessToken('test-token');
    useAuthStore.getState().setAccessToken(null);
    expect(useAuthStore.getState().accessToken).toBeNull();
  });
});
