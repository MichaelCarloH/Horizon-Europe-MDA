import { createCsrfMiddleware, createCsrfProtect } from '@edge-csrf/nextjs';

// initalize csrf protection middleware
export default createCsrfProtect({
  cookie: {
    secure: process.env.NODE_ENV === 'production',
  },
});
