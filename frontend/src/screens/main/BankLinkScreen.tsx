import React, { useState, useEffect, useContext } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ActivityIndicator, Platform, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import apiClient from '../../api/axios';
import { AuthContext } from '../../context/AuthContext';

declare global {
  interface Window {
    Plaid: any;
  }
}

const BankLinkScreen = ({ navigation }: any) => {
  const { fetchUser } = useContext(AuthContext);
  const [loading, setLoading] = useState(false);
  const [linkToken, setLinkToken] = useState<string | null>(null);

  useEffect(() => {
    // Load Plaid script on Web
    if (Platform.OS === 'web') {
      const script = document.createElement('script');
      script.src = 'https://cdn.plaid.com/link/v2/stable/link-initialize.js';
      script.async = true;
      document.body.appendChild(script);
      
      // Fetch link token
      fetchLinkToken();
      
      return () => {
        document.body.removeChild(script);
      };
    } else {
        // For mobile, mock initialization
        setLinkToken("mock_link_token");
    }
  }, []);

  const fetchLinkToken = async () => {
    try {
      const response = await apiClient.post('/bank/create_link_token');
      setLinkToken(response.data.link_token);
    } catch (error) {
      console.error('Error fetching link token:', error);
      // Don't alert if we're just developing
    }
  };

  const handleOpenPlaid = () => {
    if (Platform.OS === 'web' && window.Plaid && linkToken && linkToken !== "mock_link_token") {
      const handler = window.Plaid.create({
        token: linkToken,
        onSuccess: async (public_token: string, metadata: any) => {
          setLoading(true);
          try {
            await apiClient.post(`/bank/exchange_public_token?public_token=${public_token}`);
            // Fetch updated balance immediately
            await apiClient.get('/bank/balance');
            await fetchUser();
            window.alert('Bank account linked and balance updated!');
            navigation.goBack();
          } catch (error) {
            console.error('Error exchanging public token:', error);
            window.alert('Failed to link bank account.');
          } finally {
            setLoading(false);
          }
        },
        onExit: (err: any, metadata: any) => {
          if (err != null) {
            console.error('Plaid Link exit error:', err);
          }
        },
      });
      handler.open();
    } else {
        // Mock success for development/mobile without native SDK
        Alert.alert('Sandbox Link', 'Simulate successful Plaid link (Sandbox Mode)?', [
            { text: 'Cancel', style: 'cancel' },
            { text: 'Link Bank', onPress: async () => {
                setLoading(true);
                try {
                    // For a real app, this needs a valid public token from Plaid UI
                    // In sandbox mode, we can use 'public-sandbox-...'
                    await apiClient.post('/bank/exchange_public_token?public_token=public-sandbox-5cd37e72-2298-4423-863a-e53aa6c5b058');
                    await apiClient.get('/bank/balance');
                    await fetchUser();
                    Alert.alert('Success', 'Mock bank account linked!');
                    navigation.goBack();
                } catch(e) {
                    Alert.alert('Error', 'Check your PLAID_CLIENT_ID and SECRET in .env');
                } finally { setLoading(false); }
            }}
        ]);
    }
  };

  return (
    <View style={styles.container}>
      <Ionicons name="business" size={80} color="#00D09E" style={styles.icon} />
      <Text style={styles.title}>Connect Your Bank</Text>
      <Text style={styles.subtitle}>
        NeuroShield uses Plaid to securely connect to your bank account and fetch your real balance without ever seeing your password.
      </Text>

      <TouchableOpacity 
        style={[styles.button, (!linkToken || loading) && styles.buttonDisabled]} 
        onPress={handleOpenPlaid}
        disabled={!linkToken || loading}
      >
        {loading ? (
          <ActivityIndicator color="#0F172A" />
        ) : (
          <>
            <Ionicons name="link" size={20} color="#0F172A" />
            <Text style={styles.buttonText}>Link with Plaid</Text>
          </>
        )}
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F172A', padding: 30, justifyContent: 'center', alignItems: 'center' },
  icon: { marginBottom: 20 },
  title: { fontSize: 24, fontWeight: 'bold', color: '#F8FAFC', marginBottom: 15 },
  subtitle: { fontSize: 16, color: '#94A3B8', textAlign: 'center', lineHeight: 24, marginBottom: 40 },
  button: { 
    flexDirection: 'row', 
    backgroundColor: '#00D09E', 
    paddingVertical: 15, 
    paddingHorizontal: 30, 
    borderRadius: 12, 
    alignItems: 'center' 
  },
  buttonDisabled: { backgroundColor: '#334155' },
  buttonText: { color: '#0F172A', fontSize: 18, fontWeight: 'bold', marginLeft: 10 }
});

export default BankLinkScreen;
