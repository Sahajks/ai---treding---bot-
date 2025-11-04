import pandas as pd
import numpy as np
import requests
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

class SimpleAITradingBot:
    def __init__(self, initial_capital=1000):
        self.portfolio = {
            'cash': initial_capital,
            'positions': {},
            'total_value': initial_capital
        }
        self.trade_history = []
        self.risk_per_trade = 0.02  # 2% risk per trade
        
    def analyze_memecoin(self, pair_data: Dict) -> Dict:
        """Basic AI analysis for memecoins"""
        analysis = {
            'score': 0,
            'decision': 'HOLD',
            'confidence': 0,
            'reasons': []
        }
        
        try:
            # 1. Liquidity Analysis (30% weight)
            liquidity = float(pair_data.get('liquidity', {}).get('usd', 0))
            liquidity_score = self._calculate_liquidity_score(liquidity)
            analysis['score'] += liquidity_score * 0.3
            if liquidity_score > 0.7:
                analysis['reasons'].append(f"Good liquidity: ${liquidity:,.0f}")
            
            # 2. Price Momentum (25% weight)
            price_change = self._calculate_price_momentum(pair_data)
            analysis['score'] += price_change * 0.25
            if price_change > 0.7:
                analysis['reasons'].append("Strong positive momentum")
            
            # 3. Volume Analysis (20% weight)
            volume_score = self._analyze_volume(pair_data)
            analysis['score'] += volume_score * 0.2
            if volume_score > 0.6:
                analysis['reasons'].append("High trading volume")
            
            # 4. Age Analysis (15% weight)
            age_score = self._analyze_token_age(pair_data)
            analysis['score'] += age_score * 0.15
            if age_score > 0.8:
                analysis['reasons'].append("Fresh token launch")
            
            # 5. Social Score (10% weight)
            social_score = self._estimate_social_presence(pair_data)
            analysis['score'] += social_score * 0.1
            
            # Determine decision
            analysis['confidence'] = analysis['score']
            if analysis['score'] >= 0.7:
                analysis['decision'] = 'BUY'
            elif analysis['score'] <= 0.3:
                analysis['decision'] = 'SELL'
            else:
                analysis['decision'] = 'HOLD'
                
        except Exception as e:
            analysis['reasons'].append(f"Analysis error: {str(e)}")
            
        return analysis
    
    def _calculate_liquidity_score(self, liquidity: float) -> float:
        """Calculate liquidity score"""
        if liquidity >= 50000:
            return 1.0
        elif liquidity >= 25000:
            return 0.8
        elif liquidity >= 10000:
            return 0.6
        elif liquidity >= 5000:
            return 0.4
        else:
            return 0.2
    
    def _calculate_price_momentum(self, pair_data: Dict) -> float:
        """Calculate price momentum score"""
        try:
            price_change = pair_data.get('priceChange', {})
            h24_change = price_change.get('h24', 0)
            
            if h24_change > 0.5:  # 50%+ gain
                return 0.9
            elif h24_change > 0.2:  # 20%+ gain
                return 0.7
            elif h24_change > 0:  # Positive
                return 0.5
            elif h24_change > -0.1:  # Small loss
                return 0.3
            else:  # Big loss
                return 0.1
        except:
            return 0.5
    
    def _analyze_volume(self, pair_data: Dict) -> float:
        """Analyze trading volume"""
        try:
            volume = pair_data.get('volume', {})
            h24_volume = volume.get('h24', 0)
            
            if h24_volume > 1000000:  # $1M+ volume
                return 1.0
            elif h24_volume > 500000:  # $500K+ volume
                return 0.8
            elif h24_volume > 100000:  # $100K+ volume
                return 0.6
            elif h24_volume > 50000:  # $50K+ volume
                return 0.4
            else:
                return 0.2
        except:
            return 0.3
    
    def _analyze_token_age(self, pair_data: Dict) -> float:
        """Analyze how new the token is"""
        try:
            pair_created_at = pair_data.get('pairCreatedAt')
            if pair_created_at:
                created_time = datetime.fromtimestamp(pair_created_at / 1000)
                age_hours = (datetime.now() - created_time).total_seconds() / 3600
                
                if age_hours <= 1:  # 1 hour old
                    return 1.0
                elif age_hours <= 6:  # 6 hours old
                    return 0.8
                elif age_hours <= 24:  # 1 day old
                    return 0.6
                else:
                    return 0.3
        except:
            pass
        return 0.5
    
    def _estimate_social_presence(self, pair_data: Dict) -> float:
        """Estimate social media presence"""
        # This would integrate with Twitter/Telegram APIs
        # For now, using basic estimation
        base_token = pair_data.get('baseToken', {})
        symbol = base_token.get('symbol', '').lower()
        name = base_token.get('name', '').lower()
        
        # Check for common social indicators in name/symbol
        social_indicators = ['elon', 'moon', 'doge', 'shib', 'pepe', 'wojak']
        matches = sum(1 for indicator in social_indicators 
                     if indicator in symbol or indicator in name)
        
        return min(1.0, matches * 0.2)
    
    def calculate_position_size(self, symbol: str, price: float, stop_loss: float) -> float:
        """Calculate position size based on risk management"""
        risk_amount = self.portfolio['cash'] * self.risk_per_trade
        price_risk = abs(price - stop_loss)
        
        if price_risk == 0:
            return 0
            
        shares = risk_amount / price_risk
        max_position_value = self.portfolio['cash'] * 0.1  # Max 10% in one position
        max_shares = max_position_value / price
        
        return min(shares, max_shares)
    
    def execute_trade(self, symbol: str, decision: str, price: float, amount: float) -> Dict:
        """Execute a trade (simulated for now)"""
        trade_value = amount * price
        
        if decision == 'BUY' and trade_value <= self.portfolio['cash']:
            # Buy logic
            self.portfolio['cash'] -= trade_value
            if symbol in self.portfolio['positions']:
                self.portfolio['positions'][symbol]['shares'] += amount
                self.portfolio['positions'][symbol]['cost_basis'] = (
                    (self.portfolio['positions'][symbol]['cost_basis'] * 
                     (self.portfolio['positions'][symbol]['shares'] - amount) + trade_value) / 
                    self.portfolio['positions'][symbol]['shares']
                )
            else:
                self.portfolio['positions'][symbol] = {
                    'shares': amount,
                    'cost_basis': price,
                    'entry_time': datetime.now()
                }
            
            trade_record = {
                'symbol': symbol,
                'action': 'BUY',
                'shares': amount,
                'price': price,
                'value': trade_value,
                'timestamp': datetime.now()
            }
            self.trade_history.append(trade_record)
            return trade_record
        
        elif decision == 'SELL' and symbol in self.portfolio['positions']:
            position = self.portfolio['positions'][symbol]
            if amount > position['shares']:
                amount = position['shares']
            
            # Sell logic
            trade_value = amount * price
            self.portfolio['cash'] += trade_value
            position['shares'] -= amount
            
            if position['shares'] == 0:
                del self.portfolio['positions'][symbol]
            
            trade_record = {
                'symbol': symbol,
                'action': 'SELL',
                'shares': amount,
                'price': price,
                'value': trade_value,
                'timestamp': datetime.now()
            }
            self.trade_history.append(trade_record)
            return trade_record
        
        return {'error': 'Trade execution failed'}
    
    def get_portfolio_value(self) -> float:
        """Calculate total portfolio value"""
        total = self.portfolio['cash']
        for symbol, position in self.portfolio['positions'].items():
            # In real implementation, you'd get current price
            total += position['shares'] * position['cost_basis']
        return total

class DexScreenerAPI:
    def __init__(self):
        self.base_url = "https://api.dexscreener.com/latest/dex"
    
    def get_new_pairs(self, limit: int = 50) -> List[Dict]:
        """Get newly created pairs from DexScreener"""
        try:
            url = f"{self.base_url}/search/?q=created"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            pairs = data.get('pairs', [])[:limit]
            
            # Filter for very new pairs (last 24 hours)
            recent_pairs = []
            for pair in pairs:
                created_at = pair.get('pairCreatedAt', 0)
                if datetime.now().timestamp() * 1000 - created_at < 24 * 60 * 60 * 1000:
                    recent_pairs.append(pair)
            
            return recent_pairs
            
        except Exception as e:
            print(f"Error fetching pairs: {e}")
            return []
    
    def get_trending_pairs(self) -> List[Dict]:
        """Get trending trading pairs"""
        try:
            url = f"{self.base_url}/search/?q=volume"
            response = requests.get(url, timeout=10)
            data = response.json()
            return data.get('pairs', [])[:20]
        except Exception as e:
            print(f"Error fetching trending: {e}")
            return []
