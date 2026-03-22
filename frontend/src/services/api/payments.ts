import { apiClient } from './client'

export const paymentsService = {
  // Get plans
  getPlans: async () => {
    return apiClient.get('/payments/plans')
  },

  // Create subscription
  createSubscription: async (priceId: string, paymentMethodId: string) => {
    return apiClient.post('/payments/subscriptions', {
      price_id: priceId,
      payment_method_id: paymentMethodId,
    })
  },

  // Cancel subscription
  cancelSubscription: async (subscriptionId: string) => {
    return apiClient.post(`/payments/subscriptions/${subscriptionId}/cancel`)
  },

  // Update subscription
  updateSubscription: async (subscriptionId: string, priceId: string) => {
    return apiClient.put(`/payments/subscriptions/${subscriptionId}`, {
      price_id: priceId,
    })
  },

  // Get subscription
  getSubscription: async () => {
    return apiClient.get('/payments/subscriptions/current')
  },

  // Get payment methods
  getPaymentMethods: async () => {
    return apiClient.get('/payments/methods')
  },

  // Add payment method
  addPaymentMethod: async (paymentMethodId: string) => {
    return apiClient.post('/payments/methods', {
      payment_method_id: paymentMethodId,
    })
  },

  // Remove payment method
  removePaymentMethod: async (paymentMethodId: string) => {
    return apiClient.delete(`/payments/methods/${paymentMethodId}`)
  },

  // Set default payment method
  setDefaultPaymentMethod: async (paymentMethodId: string) => {
    return apiClient.put('/payments/methods/default', {
      payment_method_id: paymentMethodId,
    })
  },

  // Get invoices
  getInvoices: async (limit: number = 10) => {
    return apiClient.get(`/payments/invoices?limit=${limit}`)
  },

  // Get invoice
  getInvoice: async (invoiceId: string) => {
    return apiClient.get(`/payments/invoices/${invoiceId}`)
  },
}