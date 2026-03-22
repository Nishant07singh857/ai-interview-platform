/** @type {import('next').NextConfig} */
const nextConfig = { reactStrictMode: true, swcMinify: true, images: { domains: ['firebasestorage.googleapis.com', 'lh3.googleusercontent.com'] }, eslint: { ignoreDuringBuilds: true }, typescript: { ignoreBuildErrors: true }, poweredByHeader: false, output: 'standalone', experimental: { typedRoutes: false }, pageExtensions: ['tsx','ts','jsx','js'] };
module.exports = nextConfig;
