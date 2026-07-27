"""
Przelewy24 Payment Integration
Polish payment gateway for local customers
"""

import os
import hashlib
import requests
from typing import Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Przelewy24Service:
    """Service for Przelewy24 payment operations"""
    
    def __init__(self):
        self.merchant_id = os.getenv('P24_MERCHANT_ID')
        self.pos_id = os.getenv('P24_POS_ID')
        self.crc = os.getenv('P24_CRC')
        self.api_key = os.getenv('P24_API_KEY')
        self.sandbox = os.getenv('P24_SANDBOX', 'true').lower() == 'true'
        
        if self.sandbox:
            self.base_url = 'https://sandbox.przelewy24.pl/api/v1'
        else:
            self.base_url = 'https://secure.przelewy24.pl/api/v1'
    
    def _calculate_checksum(self, data: Dict) -> str:
        """Calculate checksum for Przelewy24"""
        # Concatenate specific fields in order
        fields = [
            data.get('session_id', ''),
            data.get('merchant_id', self.pos_id),
            data.get('amount', ''),
            data.get('currency', 'PLN'),
            self.crc
        ]
        concatenated = '|'.join(str(field) for field in fields)
        return hashlib.md5(concatenated.encode()).hexdigest()
    
    def register_transaction(self, session_id: str, amount: float, 
                           description: str, email: str, 
                           return_url: str) -> Dict:
        """Register a new transaction"""
        try:
            data = {
                'merchantId': int(self.pos_id),
                'posId': int(self.pos_id),
                'sessionId': session_id,
                'amount': str(amount),
                'currency': 'PLN',
                'description': description,
                'email': email,
                'country': 'PL',
                'language': 'pl',
                'urlReturn': return_url,
                'urlStatus': f"{return_url}/status",
                'timeLimit': 15,  # 15 minutes
                'channel': 1,  # All channels
                'encoding': 'UTF-8'
            }
            
            # Add checksum
            data['sign'] = self._calculate_checksum({
                'session_id': session_id,
                'merchant_id': self.pos_id,
                'amount': str(amount),
                'currency': 'PLN'
            })
            
            response = requests.post(
                f"{self.base_url}/transaction/register",
                json=data,
                headers={'Authorization': f'{self.pos_id}:{self.crc}'}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Registered Przelewy24 transaction: {session_id}")
                return {
                    'success': True,
                    'token': result.get('data', {}).get('token'),
                    'redirect_url': f"https://sandbox.przelewy24.pl/trnRequest/{result.get('data', {}).get('token')}"
                }
            else:
                logger.error(f"Error registering transaction: {response.text}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            logger.error(f"Error registering Przelewy24 transaction: {e}")
            return {'success': False, 'error': str(e)}
    
    def verify_transaction(self, session_id: str, amount: float, 
                          currency: str = 'PLN') -> Dict:
        """Verify a transaction"""
        try:
            data = {
                'merchantId': int(self.pos_id),
                'posId': int(self.pos_id),
                'sessionId': session_id,
                'amount': str(amount),
                'currency': currency,
                'sign': self._calculate_checksum({
                    'session_id': session_id,
                    'merchant_id': self.pos_id,
                    'amount': str(amount),
                    'currency': currency
                })
            }
            
            response = requests.put(
                f"{self.base_url}/transaction/verify",
                json=data,
                headers={'Authorization': f'{self.pos_id}:{self.crc}'}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Verified Przelewy24 transaction: {session_id}")
                return {
                    'success': True,
                    'status': result.get('data', {}).get('status')
                }
            else:
                logger.error(f"Error verifying transaction: {response.text}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            logger.error(f"Error verifying Przelewy24 transaction: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_transaction_status(self, session_id: str) -> Dict:
        """Get transaction status"""
        try:
            response = requests.get(
                f"{self.base_url}/transaction/by/sessionId/{session_id}",
                headers={'Authorization': f'{self.pos_id}:{self.crc}'}
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'status': result.get('data', {}).get('status'),
                    'amount': result.get('data', {}).get('amount'),
                    'currency': result.get('data', {}).get('currency')
                }
            else:
                logger.error(f"Error getting transaction status: {response.text}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            logger.error(f"Error getting transaction status: {e}")
            return {'success': False, 'error': str(e)}
