import { useEffect, useContext, useRef } from 'react';
import { Alert, Platform } from 'react-native';
import { AuthContext } from '../context/AuthContext';
const WS_URL = process.env.EXPO_PUBLIC_WS_URL || 'ws://127.0.0.1:8000/ws/alerts';

export const useWebSockets = () => {
  const { user } = useContext(AuthContext);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (user) {
      const connect = () => {
        ws.current = new WebSocket(`${WS_URL}/${user.id}`);

        ws.current.onopen = () => {
          console.log('WebSocket Connected');
        };

        ws.current.onmessage = (e) => {
          const data = JSON.parse(e.data);
          if (data.type === 'FRAUD_ALERT') {
            Alert.alert(
              '🚨 FRAUD ALERT',
              `Suspicious transaction detected!\nMerchant: ${data.merchant}\nAmount: $${data.amount}\nRisk: ${data.risk_level}`,
              [{ text: 'Review', style: 'destructive' }]
            );
          } else if (data.type === 'BANK_SYNC') {
            Alert.alert('Bank Sync', data.message);
          }
        };

        ws.current.onerror = (e) => {
          console.error('WebSocket Error', e);
        };

        ws.current.onclose = () => {
          console.log('WebSocket Disconnected. Reconnecting...');
          setTimeout(connect, 3000); // Simple reconnection logic
        };
      };

      connect();

      return () => {
        if (ws.current) {
          ws.current.close();
        }
      };
    }
  }, [user]);

  return ws.current;
};
