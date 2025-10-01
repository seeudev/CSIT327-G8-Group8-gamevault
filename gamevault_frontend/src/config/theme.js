/**
 * Theme Configuration
 * Centralized theme settings for easy branding and customization
 */

export const theme = {
  // Brand Colors
  colors: {
    primary: '#3498db',
    primaryDark: '#2980b9',
    secondary: '#2c3e50',
    secondaryLight: '#34495e',
    accent: '#e74c3c',
    accentDark: '#c0392b',
    success: '#27ae60',
    successDark: '#229954',
    warning: '#f39c12',
    warningDark: '#e67e22',
    info: '#17a2b8',
    infoDark: '#138496',
    
    // Neutral Colors
    white: '#ffffff',
    black: '#000000',
    gray: {
      50: '#f8f9fa',
      100: '#e9ecef',
      200: '#dee2e6',
      300: '#ced4da',
      400: '#adb5bd',
      500: '#6c757d',
      600: '#495057',
      700: '#343a40',
      800: '#212529',
      900: '#1a1a1a'
    },
    
    // Text Colors
    text: {
      primary: '#2c3e50',
      secondary: '#7f8c8d',
      muted: '#95a5a6',
      light: '#bdc3c7',
      inverse: '#ffffff'
    },
    
    // Background Colors
    background: {
      primary: '#ffffff',
      secondary: '#f8f9fa',
      tertiary: '#e9ecef',
      dark: '#2c3e50',
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    },
    
    // Border Colors
    border: {
      light: '#e1e8ed',
      medium: '#d1d5db',
      dark: '#9ca3af'
    }
  },
  
  // Typography
  typography: {
    fontFamily: {
      primary: '"Inter", "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif',
      secondary: '"Georgia", "Times New Roman", serif',
      mono: '"Fira Code", "Monaco", "Consolas", "Liberation Mono", "Courier New", monospace'
    },
    
    fontSize: {
      xs: '0.75rem',    // 12px
      sm: '0.875rem',   // 14px
      base: '1rem',     // 16px
      lg: '1.125rem',   // 18px
      xl: '1.25rem',    // 20px
      '2xl': '1.5rem',  // 24px
      '3xl': '1.875rem', // 30px
      '4xl': '2.25rem', // 36px
      '5xl': '3rem',    // 48px
      '6xl': '3.75rem'  // 60px
    },
    
    fontWeight: {
      light: 300,
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
      extrabold: 800
    },
    
    lineHeight: {
      tight: 1.25,
      snug: 1.375,
      normal: 1.5,
      relaxed: 1.625,
      loose: 2
    }
  },
  
  // Spacing
  spacing: {
    0: '0',
    1: '0.25rem',   // 4px
    2: '0.5rem',    // 8px
    3: '0.75rem',   // 12px
    4: '1rem',      // 16px
    5: '1.25rem',   // 20px
    6: '1.5rem',    // 24px
    8: '2rem',      // 32px
    10: '2.5rem',   // 40px
    12: '3rem',     // 48px
    16: '4rem',     // 64px
    20: '5rem',     // 80px
    24: '6rem',     // 96px
    32: '8rem'      // 128px
  },
  
  // Border Radius
  borderRadius: {
    none: '0',
    sm: '0.125rem',   // 2px
    base: '0.25rem',  // 4px
    md: '0.375rem',   // 6px
    lg: '0.5rem',     // 8px
    xl: '0.75rem',    // 12px
    '2xl': '1rem',    // 16px
    '3xl': '1.5rem',  // 24px
    full: '9999px'
  },
  
  // Shadows
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
    none: 'none'
  },
  
  // Transitions
  transitions: {
    fast: '0.15s ease-in-out',
    base: '0.3s ease-in-out',
    slow: '0.5s ease-in-out'
  },
  
  // Breakpoints
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px'
  },
  
  // Z-Index
  zIndex: {
    dropdown: 1000,
    sticky: 1020,
    fixed: 1030,
    modal: 1040,
    popover: 1050,
    tooltip: 1060
  }
};

// Helper functions for theme usage
export const getColor = (colorPath) => {
  const keys = colorPath.split('.');
  let value = theme.colors;
  
  for (const key of keys) {
    value = value[key];
    if (value === undefined) {
      console.warn(`Color path "${colorPath}" not found in theme`);
      return theme.colors.gray[500];
    }
  }
  
  return value;
};

export const getSpacing = (size) => {
  return theme.spacing[size] || size;
};

export const getBorderRadius = (size) => {
  return theme.borderRadius[size] || size;
};

export const getShadow = (size) => {
  return theme.shadows[size] || size;
};

export const getTransition = (speed) => {
  return theme.transitions[speed] || speed;
};

export default theme;
