import { defineConfig } from "drizzle-kit";

const connectionString = process.env.DATABASE_URL;

// Support both MySQL and PostgreSQL
const getDatabaseConfig = () => {
  if (!connectionString) {
    // For development without database, return a mock config
    console.warn("DATABASE_URL not configured. Using mock configuration for development.");
    return {
      schema: "./drizzle/schema.ts",
      out: "./drizzle",
      dialect: "mysql",
      dbCredentials: {
        url: "mysql://root:password@localhost:3306/cobuddy_dev",
      },
    };
  }

  // Auto-detect database type from connection string
  const isPostgres = connectionString.startsWith('postgresql://') || connectionString.startsWith('postgres://');
  const isMySQL = connectionString.startsWith('mysql://');
  
  if (!isPostgres && !isMySQL) {
    throw new Error("Unsupported database type. Use MySQL or PostgreSQL connection string.");
  }

  return {
    schema: "./drizzle/schema.ts",
    out: "./drizzle",
    dialect: isPostgres ? "postgresql" : "mysql",
    dbCredentials: {
      url: connectionString,
    },
  };
};

export default defineConfig(getDatabaseConfig());
