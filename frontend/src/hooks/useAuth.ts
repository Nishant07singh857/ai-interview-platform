import { useAppDispatch, useAppSelector } from '@/store/store'
import {
  login as loginThunk,
  register as registerThunk,
  logout as logoutThunk,
  verifyEmail as verifyEmailThunk,
  forgotPassword as forgotPasswordThunk,
  resetPassword as resetPasswordThunk,
  changePassword as changePasswordThunk,
} from '@/store/slices/authSlice'

export const useAuth = () => {
  const dispatch = useAppDispatch()
  const { user, isLoading, isAuthenticated, error } = useAppSelector((state) => state.auth)

  const login = async (email: string, password: string) => {
    return dispatch(loginThunk({ email, password })).unwrap()
  }

  const register = async (data: { email: string; password: string; displayName?: string }) => {
    return dispatch(registerThunk(data)).unwrap()
  }

  const logout = async () => {
    return dispatch(logoutThunk()).unwrap()
  }

  const verifyEmail = async (token: string) => {
    return dispatch(verifyEmailThunk(token)).unwrap()
  }

  const forgotPassword = async (email: string) => {
    return dispatch(forgotPasswordThunk(email)).unwrap()
  }

  const resetPassword = async (token: string, newPassword: string) => {
    return dispatch(resetPasswordThunk({ token, newPassword })).unwrap()
  }

  const changePassword = async (currentPassword: string, newPassword: string) => {
    return dispatch(changePasswordThunk({ currentPassword, newPassword })).unwrap()
  }

  return {
    user,
    isLoading,
    isAuthenticated,
    error,
    login,
    register,
    logout,
    verifyEmail,
    forgotPassword,
    resetPassword,
    changePassword,
  }
}
