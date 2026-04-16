const config = require('./config');
const logger = require('./logger');
const ExpressServer = require('./expressServer');

const { MongoMemoryServer } = require('mongodb-memory-server');
const mongoose = require('mongoose');

const launchServer = async () => {
  try {
    logger.info('Starting MongoDB Virtual Server...');
    const mongoServer = await MongoMemoryServer.create();
    const mongoUri = mongoServer.getUri();
    
    await mongoose.connect(mongoUri);
    logger.info(`Connected to MongoDB In-Memory at ${mongoUri}`);

    this.expressServer = new ExpressServer(config.URL_PORT, config.OPENAPI_YAML);
    this.expressServer.launch();
    logger.info('Express server running');
  } catch (error) {
    logger.error('Express Server failure', error.message);
    await this.close();
  }
};

launchServer().catch(e => logger.error(e));
