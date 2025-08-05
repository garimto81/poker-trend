const { Pool } = require('pg');
const mongoose = require('mongoose');
const redis = require('redis');
const { logger } = require('../utils/logger');

// PostgreSQL connection
const pgPool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// MongoDB connection
const mongooseOptions = {
  useNewUrlParser: true,
  useUnifiedTopology: true,
  maxPoolSize: 10,
  serverSelectionTimeoutMS: 5000,
  socketTimeoutMS: 45000,
};

// Redis connection
const redisClient = redis.createClient({
  url: process.env.REDIS_URL,
  retry_strategy: (options) => {
    if (options.error && options.error.code === 'ECONNREFUSED') {
      logger.error('Redis server connection refused');
      return new Error('Redis server connection refused');
    }
    if (options.total_retry_time > 1000 * 60 * 60) {
      logger.error('Redis retry time exhausted');
      return new Error('Retry time exhausted');
    }
    if (options.attempt > 10) {
      logger.error('Redis connection attempts exceeded');
      return undefined;
    }
    // Reconnect after
    return Math.min(options.attempt * 100, 3000);
  }
});

async function connectDatabases() {
  try {
    // Test PostgreSQL connection
    const pgClient = await pgPool.connect();
    await pgClient.query('SELECT NOW()');
    pgClient.release();
    logger.info('✅ PostgreSQL connected successfully');

    // Connect to MongoDB
    await mongoose.connect(process.env.MONGODB_URL, mongooseOptions);
    logger.info('✅ MongoDB connected successfully');

    // Connect to Redis
    await redisClient.connect();
    logger.info('✅ Redis connected successfully');

    // Setup MongoDB event listeners
    mongoose.connection.on('error', (err) => {
      logger.error('MongoDB connection error:', err);
    });

    mongoose.connection.on('disconnected', () => {
      logger.warn('MongoDB disconnected');
    });

    // Setup Redis event listeners
    redisClient.on('error', (err) => {
      logger.error('Redis connection error:', err);
    });

    redisClient.on('connect', () => {
      logger.info('Redis connected');
    });

    redisClient.on('ready', () => {
      logger.info('Redis ready');
    });

  } catch (error) {
    logger.error('Database connection failed:', error);
    throw error;
  }
}

// Graceful shutdown
process.on('SIGINT', async () => {
  logger.info('Closing database connections...');
  
  try {
    await pgPool.end();
    await mongoose.connection.close();
    await redisClient.quit();
    logger.info('All database connections closed');
  } catch (error) {
    logger.error('Error closing database connections:', error);
  }
});

module.exports = {
  pgPool,
  mongoose,
  redisClient,
  connectDatabases
};