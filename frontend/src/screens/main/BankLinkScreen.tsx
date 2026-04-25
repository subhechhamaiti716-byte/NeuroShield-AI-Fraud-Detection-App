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
        // SIMULATION MODE
        const msg = !linkToken ? 'Simulation Mode: No Plaid keys found. Would you like to simulate a bank link with sample data and Fraud Alerts?' : 'Link Sandbox Bank account?';
        
        Alert.alert('NeuroShield Simulation', msg, [
            { text: 'Cancel', style: 'cancel' },
            { text: 'Simulate Link', onPress: async () => {
                setLoading(true);
                try {
                    // Call a specialized simulation endpoint to populate data
                    await apiClient.post('/bank/simulate_link');
                    await fetchUser();
                    Alert.alert('Success', 'Simulation Complete! Your dashboard has been populated with real-world scenarios.');
                    navigation.goBack();
                } catch(e) {
                    Alert.alert('Error', 'Simulation failed. Please try again.');
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
        style={[styles.button, loading && styles.buttonDisabled]} 
        onPress={handleOpenPlaid}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#0F172A" />
        ) : (
          <>
            <Ionicons name="link" size={20} color="#0F172A" />
            <Text style={styles.buttonText}>
              {!linkToken ? "Simulate Bank Link" : "Link with Plaid"}
            </Text>
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
