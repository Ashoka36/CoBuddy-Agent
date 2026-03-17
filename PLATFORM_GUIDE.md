# Cross-Platform Development Guide for Co-Buddy

## Platform Compatibility

This application is configured to work across multiple platforms:

### Windows
- Use `pnpm run build:windows` for cross-compatible builds
- Environment variables work with both CMD and PowerShell
- Paths are normalized for Windows filesystem

### Linux Mint / Ubuntu
- Standard build with `pnpm run build`
- Native filesystem performance
- Full PostgreSQL/MySQL support

### Android (via Termux)
- Use `pnpm run build:dev` for resource-constrained builds
- Lightweight database options (SQLite fallback)
- Optimized for mobile hardware

## Platform-Specific Scripts

```bash
# Windows (CMD/PowerShell)
pnpm run build:windows

# Linux / macOS
pnpm run build

# Development (any platform)
pnpm run build:dev

# Android / Termux
pnpm run build:dev
```

## Environment Setup

1. Copy `.env.example` to `.env`
2. Configure database URL for your platform:
   - Windows: `mysql://localhost:3306/cobuddy`
   - Linux: `postgresql://localhost:5432/cobuddy`
   - Android: `sqlite:./data/cobuddy.db`

## Database Configuration

### Windows (MySQL recommended)
```
DATABASE_URL=mysql://root:password@localhost:3306/cobuddy
```

### Linux (PostgreSQL recommended)
```
DATABASE_URL=postgresql://username:password@localhost:5432/cobuddy
```

### Android (SQLite fallback)
```
DATABASE_URL=sqlite:./data/cobuddy.db
```

## NVIDIA NIM Endpoint

Configure the NVIDIA NIM endpoint for AI functionality:
```
VITE_NVIDIA_NIM_ENDPOINT=https://integrate.api.nvidia.com/v1/chat/completions
NVIDIA_NIM_API_KEY=your_api_key_here
```

## Troubleshooting

### Windows Issues
- Use Git Bash for better Unix compatibility
- Ensure Node.js 18.19+ is installed
- Run as Administrator if port access issues occur

### Linux Issues
- Check PostgreSQL/MySQL service status
- Verify firewall settings for port 3000
- Use native package managers for dependencies

### Android Issues
- Install Termux from F-Droid (not Play Store)
- Use `pkg install nodejs npm` for Node.js
- Limited database support (SQLite recommended)

## Performance Optimization

Each platform has specific optimizations:
- Windows: Optimized for PowerShell performance
- Linux: Native filesystem and database performance
- Android: Resource-constrained builds and caching
