import React, { useEffect, useContext, useRef } from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { Platform } from 'react-native';

import { AuthContext } from '../context/AuthContext';

import DashboardScreen from '../screens/main/DashboardScreen';
import TransactionsScreen from '../screens/main/TransactionsScreen';
import AnalyticsScreen from '../screens/main/AnalyticsScreen';
import AddTransactionScreen from '../screens/main/AddTransactionScreen';
import FraudAlertScreen from '../screens/main/FraudAlertScreen';
import DepositFundsScreen from '../screens/main/DepositFundsScreen';
import BankLinkScreen from '../screens/main/BankLinkScreen';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

const TabNavigator = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap = 'home';
          if (route.name === 'Home') iconName = focused ? 'home' : 'home-outline';
          else if (route.name === 'Transactions') iconName = focused ? 'list' : 'list-outline';
          else if (route.name === 'Analytics') iconName = focused ? 'pie-chart' : 'pie-chart-outline';
          
          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#00D09E',
        tabBarInactiveTintColor: '#64748B',
        tabBarStyle: {
          backgroundColor: '#1E293B',
          borderTopColor: '#334155',
        },
        headerStyle: {
          backgroundColor: '#1E293B',
        },
        headerTintColor: '#F8FAFC',
      })}
    >
      <Tab.Screen name="Home" component={DashboardScreen} options={{ title: 'NeuroShield' }} />
      <Tab.Screen name="Transactions" component={TransactionsScreen} />
      <Tab.Screen name="Analytics" component={AnalyticsScreen} />
    </Tab.Navigator>
  );
};

const MainTabs = () => {
  const { user } = useContext(AuthContext);
  const navigation = useNavigation<any>();
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<any>(null);

  const connectWebSocket = () => {
    if (!user) return;

    const isProd = process.env.NODE_ENV === 'production';
    const fallbackWs = isProd ? 'wss://neuroshield-ai-fraud-detection-app.onrender.com/ws/alerts' : 'ws://127.0.0.1:8000/ws/alerts';
    const baseUrl = process.env.EXPO_PUBLIC_WS_URL || fallbackWs;
    const wsUrl = `${baseUrl}/${user.id}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type === 'FRAUD_ALERT') {
          navigation.navigate('FraudAlert', {
            transaction_id: message.transaction_id,
            amount: message.amount,
            merchant: message.merchant,
            reasons: message.reasons
          });
        }
        else if (message.type === 'BANK_SYNC') {
           // Would normally trigger a global refetch via Context, omitting for brevity
           console.log("Sync event:", message.message);
        }
      } catch (e) {
        console.error('Error parsing WS message', e);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected. Reconnecting in 5s...');
      reconnectTimeout.current = setTimeout(connectWebSocket, 5000);
    };

    wsRef.current = ws;
  };

  useEffect(() => {
    connectWebSocket();

    return () => {
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, [user]);

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Tabs" component={TabNavigator} />
      <Stack.Screen 
        name="AddTransaction" 
        component={AddTransactionScreen} 
        options={{ presentation: 'modal', headerShown: true, title: 'Add Transaction', headerStyle: { backgroundColor: '#1E293B' }, headerTintColor: '#F8FAFC' }} 
      />
      <Stack.Screen 
        name="DepositFunds" 
        component={DepositFundsScreen} 
        options={{ presentation: 'modal', headerShown: true, title: 'Add Funds', headerStyle: { backgroundColor: '#1E293B' }, headerTintColor: '#F8FAFC' }} 
      />
      <Stack.Screen 
        name="BankLink" 
        component={BankLinkScreen} 
        options={{ presentation: 'modal', headerShown: true, title: 'Link Bank Account', headerStyle: { backgroundColor: '#1E293B' }, headerTintColor: '#F8FAFC' }} 
      />
      <Stack.Screen 
        name="FraudAlert" 
        component={FraudAlertScreen} 
        options={{ presentation: 'fullScreenModal', animation: 'slide_from_bottom' }} 
      />
    </Stack.Navigator>
  );
};

export default MainTabs;
