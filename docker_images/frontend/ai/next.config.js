/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false,
  images: {
    domains: ['storage.googleapis.com'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: '/api/:path*',
      },
      {
        source: '/db/:path*',
        destination: '/db/:path*',
      },
      {
        source: '/socket.io/:path*',
        destination: '/socket.io/:path*',
      },
    ];
  },
}

module.exports = nextConfig
