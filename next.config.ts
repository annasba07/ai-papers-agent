import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Disable aggressive caching in development
  experimental: {
    staleTimes: {
      dynamic: 0,  // Disable cache for dynamic routes
      static: 0,   // Disable cache for static content
    },
  },

  // Ensure dev server doesn't cache API routes
  async headers() {
    if (process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/api/:path*',
          headers: [
            { key: 'Cache-Control', value: 'no-store, must-revalidate' },
          ],
        },
      ];
    }
    return [];
  },

  async redirects() {
    return [
      {
        source: '/',
        destination: '/explore',
        permanent: false,
      },
    ];
  },
};

export default nextConfig;
