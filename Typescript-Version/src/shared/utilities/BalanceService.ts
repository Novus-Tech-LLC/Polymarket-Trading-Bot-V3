import { ethers } from 'ethers';
import { ENV } from '../config/EnvironmentConfig';

const RPC_URL = ENV.RPC_URL;
const USDC_CONTRACT_ADDRESS = ENV.USDC_CONTRACT_ADDRESS;

const USDC_ABI = ['function balanceOf(address owner) view returns (uint256)'];

/**
 * Balance Service for retrieving USDC balances
 */
export class BalanceService {
    /**
     * Get USDC balance for a given address
     * @param address - Ethereum address to check balance for
     * @returns Promise resolving to USDC balance as number
     */
    static async getBalance(address: string): Promise<number> {
        const rpcProvider = new ethers.providers.JsonRpcProvider(RPC_URL);
        const usdcContract = new ethers.Contract(USDC_CONTRACT_ADDRESS, USDC_ABI, rpcProvider);
        const balance_usdc = await usdcContract.balanceOf(address);
        const balance_usdc_real = ethers.utils.formatUnits(balance_usdc, 6);
        return parseFloat(balance_usdc_real);
    }
}

// Export default for backward compatibility
export default BalanceService.getBalance;
