import { configureStore } from '@reduxjs/toolkit'
import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux'

import authReducer from './slices/authSlice'
import userReducer from './slices/userSlice'
import practiceReducer from './slices/practiceSlice'
import resumeReducer from './slices/resumeSlice'
import analyticsReducer from './slices/analyticsSlice'
import interviewReducer from './slices/interviewSlice'
import uiReducer from './slices/uiSlice'
import notificationReducer from './slices/notificationSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    user: userReducer,
    practice: practiceReducer,
    resume: resumeReducer,
    analytics: analyticsReducer,
    interview: interviewReducer,
    ui: uiReducer,
    notifications: notificationReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types
        ignoredActions: ['persist/PERSIST'],
        // Ignore these field paths in all actions
        ignoredActionPaths: ['payload.error', 'payload.file', 'meta.arg', 'meta.arg.file'],
        // Ignore these paths in the state
        ignoredPaths: ['practice.currentSession', 'interview.currentSession'],
      },
    }),
  devTools: process.env.NODE_ENV !== 'production',
})

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch

// Use throughout your app instead of plain `useDispatch` and `useSelector`
export const useAppDispatch: () => AppDispatch = useDispatch
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector
