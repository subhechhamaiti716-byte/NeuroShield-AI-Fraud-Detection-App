import React, { useState, useContext, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, Platform, Alert } from 'react-native';
import apiClient from '../../api/axios';
import { AuthContext } from '../../context/AuthContext';
import { Ionicons } from '@expo/vector-icons';

declare global {
  interface Window {
    Razorpay: any;
  }
}

const DepositFundsScreen = ({ navigation }: any) => {
  const { user, fetchUser } = useContext(AuthContext);
  const [amount, setAmount] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (Platform.OS === 'web') {
      const script = document.createElement('script');
      script.src = 'https://checkout.razorpay.com/v1/checkout.js';
      script.async = true;
      document.body.appendChild(script);
      return () => {
        document.body.removeChild(script);
      };
    }
  }, []);

  const handleDeposit = async () => {
    const numAmount = parseFloat(amount);
    if (!numAmount || numAmount <= 0) {
      if (Platform.OS === 'web') {
        window.alert('Please enter a valid amount.');
      } else {
        Alert.alert('Error', 'Please enter a valid amount.');
      }
      return;
    }

    setLoading(true);
    try {
      // 1. Fetch Razorpay Config (Key ID) from backend
      const { data: config } = await apiClient.get('/payment/config');
      const RAZORPAY_KEY_ID = config.razorpay_key_id;

      // 2. Create the order
      const { data: orderData } = await apiClient.post(`/payment/create-order?amount=${numAmount}`);
      
      if (Platform.OS === 'web' && window.Razorpay) {
        const options = {
          key: RAZORPAY_KEY_ID, 
          amount: orderData.amount,
          currency: orderData.currency,
          name: 'NeuroShield Banking',
          description: 'Deposit to Account',
          order_id: orderData.order_id,
          handler: async function (response: any) {
            try {
              await apiClient.post('/payment/verify', null, {
                params: {
                  razorpay_order_id: response.razorpay_order_id,
                  razorpay_payment_id: response.razorpay_payment_id,
                  razorpay_signature: response.razorpay_signature
                }
              });
              window.alert('Funds deposited successfully!');
              fetchUser();
              navigation.goBack();
            } catch (err) {
              window.alert('Payment verification failed.');
            }
          },
          prefill: {
            name: user?.name,
            email: user?.email,
          },
          theme: {
            color: '#00D09E'
          }
        };
        const rzp = new window.Razorpay(options);
        rzp.on('payment.failed', function (response: any){
           window.alert(response.error.description);
        });
        rzp.open();
      } else {
        Alert.alert(
          'Mock Payment', 
          'Since we are on mobile without the native SDK linked, we will simulate a successful Razorpay flow!', 
          [{ text: 'Simulate Success', onPress: async () => {
              try {
                await apiClient.post('/payment/verify', null, {
                  params: {
                    razorpay_order_id: orderData.order_id,
                    razorpay_payment_id: "mock_payment_id",
                    razorpay_signature: "mock_signature_success"
                  }
                });
                Alert.alert('Success', 'Mock funds deposited successfully!');
                fetchUser();
                navigation.goBack();
              } catch(e) {
                console.log(e);
              }
            } 
          }]
        );
      }
    } catch (e) {
      console.error(e);
      if (Platform.OS === 'web') window.alert('Failed to initiate payment.');
      else Alert.alert('Error', 'Failed to initiate payment.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Deposit Funds</Text>
      <Text style={styles.subtitle}>Add money to your NeuroShield account securely via Razorpay.</Text>

      <View style={styles.inputContainer}>
        <Ionicons name="logo-usd" size={24} color="#00D09E" style={styles.currencyIcon} />
        <TextInput
          style={styles.input}
          placeholder="0.00"
          placeholderTextColor="#64748B"
          keyboardType="numeric"
          value={amount}
          onChangeText={setAmount}
        />
      </View>

      <TouchableOpacity style={styles.button} onPress={handleDeposit} disabled={loading}>
        {loading ? (
          <ActivityIndicator color="#0F172A" />
        ) : (
          <Text style={styles.buttonText}>Pay with Razorpay</Text>
        )}
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0F172A',
    padding: 20,
    justifyContent: 'center'
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#F8FAFC',
    textAlign: 'center',
    marginBottom: 10
  },
  subtitle: {
    fontSize: 14,
    color: '#94A3B8',
    textAlign: 'center',
    marginBottom: 40
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1E293B',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#334155',
    paddingHorizontal: 15,
    marginBottom: 30
  },
  currencyIcon: {
    marginRight: 10
  },
  input: {
    flex: 1,
    color: '#F8FAFC',
    fontSize: 32,
    fontWeight: 'bold',
    paddingVertical: 20
  },
  button: {
    backgroundColor: '#00D09E',
    paddingVertical: 18,
    borderRadius: 12,
    alignItems: 'center'
  },
  buttonText: {
    color: '#0F172A',
    fontSize: 18,
    fontWeight: 'bold'
  }
});

export default DepositFundsScreen;
