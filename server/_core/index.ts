import "dotenv/config";
import express from "express";
import { createServer } from "http";
import net from "net";
import path from "path";
import { spawn } from "child_process";

// Cross-platform path normalization
const normalizePath = (p: string): string => {
  return path.normalize(p).replace(/\\/g, '/');
};

// Platform detection
const platform = process.platform;
const isWindows = platform === 'win32';
const isAndroid = platform === 'android' || process.env.TERMUX_VERSION !== undefined;

function isPortAvailable(port: number): Promise<boolean> {
  return new Promise(resolve => {
    const server = net.createServer();
    server.listen(port, () => {
      server.close(() => resolve(true));
    });
    server.on("error", () => resolve(false));
  });
}

async function findAvailablePort(startPort: number = 3000): Promise<number> {
  for (let port = startPort; port < startPort + 20; port++) {
    if (await isPortAvailable(port)) {
      return port;
    }
  }
  throw new Error(`No available port found starting from ${startPort}`);
}

async function startCobuddyAGI() {
  const port = parseInt(process.env.PORT || "8000");
  
  console.log(`🚀 Starting Co-Buddy AGI Server on port ${port}`);
  console.log(`📱 Platform: ${isWindows ? 'Windows' : isAndroid ? 'Android (Termux)' : 'Linux/macOS'}`);
  console.log(`🔧 Environment: ${process.env.NODE_ENV || 'development'}`);
  
  // Check for Python and start the unified AGI server
  const pythonProcess = spawn('python3', ['server/cobuddy_agi_unified.py'], {
    cwd: process.cwd(),
    stdio: 'inherit',
    env: { ...process.env, PORT: port.toString() }
  });
  
  pythonProcess.on('error', (error) => {
    console.error(`❌ Failed to start Python AGI server: ${error.message}`);
    console.log('💡 Make sure Python 3 is installed and cobuddy_agi_unified.py exists');
  });
  
  pythonProcess.on('close', (code) => {
    console.log(`🐍 Python AGI server exited with code ${code}`);
  });
  
  return pythonProcess;
}

async function startWebInterface() {
  const app = express();
  const server = createServer(app);
  
  // Configure body parser
  app.use(express.json({ limit: "50mb" }));
  app.use(express.urlencoded({ limit: "50mb", extended: true }));
  
  // Serve static files in production
  if (process.env.NODE_ENV !== "development") {
    app.use(express.static('dist/public'));
    
    // SPA fallback
    app.get('*', (req, res) => {
      res.sendFile(path.resolve(process.cwd(), 'dist/public/index.html'));
    });
  } else {
    // Development proxy to AGI server
    app.get('/', (req, res) => {
      res.json({
        message: "Co-Buddy AGI Development Mode",
        agi_server: "http://localhost:8000",
        web_interface: "Coming soon"
      });
    });
  }
  
  const webPort = await findAvailablePort(parseInt(process.env.WEB_PORT || "3000"));
  
  server.listen(webPort, () => {
    console.log(`🌐 Web Interface running on http://localhost:${webPort}/`);
    console.log(`� AGI Server available at http://localhost:8000`);
    console.log(`� API Documentation: http://localhost:8000/docs`);
  });
  
  return server;
}

async function startServer() {
  console.log(`\n🧠 Co-Buddy AGI - Universal Learning Agent`);
  console.log(`==========================================`);
  
  // Start the AGI server (Python)
  const agiProcess = await startCobuddyAGI();
  
  // Wait a moment for AGI server to start
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Start the web interface (Node.js)
  const webServer = await startWebInterface();
  
  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log('\n� Shutting down Co-Buddy AGI...');
    agiProcess.kill();
    process.exit(0);
  });
  
  console.log(`\n✅ Co-Buddy AGI is fully operational!`);
  console.log(`🎯 Ready to learn any process and automate everything!\n`);
}

startServer().catch(console.error);
