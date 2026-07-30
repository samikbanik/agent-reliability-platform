import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  eslint: {
    // Lint runs via `pnpm lint` / `make check`; keep image builds focused on compile.
    ignoreDuringBuilds: true,
  },
}

export default nextConfig;
