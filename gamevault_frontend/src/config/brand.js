/**
 * Brand Configuration
 * Centralized brand settings for easy customization
 */

export const brand = {
  // Brand Identity
  name: 'GameVault',
  tagline: 'Your Digital Game Collection',
  description: 'Discover, purchase, and manage your digital game library with ease.',
  
  // Logo and Images
  logo: {
    text: 'GameVault',
    icon: '🎮', // Can be replaced with actual logo file
    favicon: '/favicon.ico'
  },
  
  // Contact Information
  contact: {
    email: 'support@gamevault.com',
    phone: '+1 (555) 123-4567',
    address: {
      street: '123 Game Street',
      city: 'Gaming City',
      state: 'GC',
      zip: '12345',
      country: 'United States'
    },
    social: {
      twitter: '@gamevault',
      facebook: 'gamevault',
      instagram: 'gamevault',
      discord: 'gamevault'
    }
  },
  
  // Business Information
  business: {
    founded: '2024',
    currency: 'USD',
    timezone: 'America/New_York',
    language: 'en-US'
  },
  
  // Feature Flags
  features: {
    enableReviews: true,
    enableWishlist: true,
    enableGiftCards: true,
    enableRefunds: true,
    enableMultiCurrency: false,
    enableDarkMode: true
  },
  
  // SEO and Meta
  seo: {
    title: 'GameVault - Digital Game Store',
    description: 'Discover and purchase digital games for PC, console, and mobile platforms.',
    keywords: ['games', 'digital', 'store', 'pc', 'console', 'mobile'],
    author: 'GameVault Team',
    robots: 'index, follow'
  },
  
  // Analytics and Tracking
  analytics: {
    googleAnalytics: '', // Add GA tracking ID
    facebookPixel: '',   // Add Facebook Pixel ID
    hotjar: ''          // Add Hotjar tracking ID
  },
  
  // Payment and Checkout
  checkout: {
    supportedMethods: ['credit_card', 'paypal', 'apple_pay', 'google_pay'],
    defaultMethod: 'credit_card',
    enableGuestCheckout: true,
    requireAccount: false
  },
  
  // Shipping and Fulfillment
  shipping: {
    freeShippingThreshold: 50,
    defaultShippingCost: 5.99,
    estimatedDeliveryDays: 1 // Digital delivery
  },
  
  // Customer Service
  support: {
    hours: '24/7',
    responseTime: '2 hours',
    channels: ['email', 'chat', 'phone'],
    knowledgeBase: true,
    faq: true
  }
};

// Helper functions
export const getBrandName = () => brand.name;
export const getBrandTagline = () => brand.tagline;
export const getContactEmail = () => brand.contact.email;
export const getCurrency = () => brand.business.currency;
export const isFeatureEnabled = (feature) => brand.features[feature] || false;

export default brand;
