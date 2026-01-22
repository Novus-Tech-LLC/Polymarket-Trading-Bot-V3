import mongoose from 'mongoose';
import { ENV } from './env';
import chalk from 'chalk';
import { DatabaseError } from '../utils/errors';

const uri = ENV.MONGO_URI || 'mongodb://localhost:27017/polymarket_copytrading';

/**
 * Connect to MongoDB database
 * @throws DatabaseError if connection fails
 */
const connectDB = async (): Promise<void> => {
    try {
        await mongoose.connect(uri);
        console.log(chalk.green('✓'), 'MongoDB connected');
    } catch (error) {
        console.log(chalk.red('✗'), 'MongoDB connection failed:', error);
        throw new DatabaseError('Failed to connect to MongoDB', error);
    }
};

/**
 * Close MongoDB connection gracefully
 * @throws DatabaseError if closing fails
 */
export const closeDB = async (): Promise<void> => {
    try {
        await mongoose.connection.close();
        console.log(chalk.green('✓'), 'MongoDB connection closed');
    } catch (error) {
        console.log(chalk.red('✗'), 'Error closing MongoDB connection:', error);
        throw new DatabaseError('Failed to close MongoDB connection', error);
    }
};

export default connectDB;
