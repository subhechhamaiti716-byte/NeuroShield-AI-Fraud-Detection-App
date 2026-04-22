import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import apiClient from '../../api/axios';

const FraudAlertScreen = ({ route, navigation }: any) => {
  const { transaction_id, amount, merchant } = route.params;
  const [loading, setLoading] = useState(false);

  const handleFeedback = async (isSafe: boolean) => {
    setLoading(true);
    try {
      await apiClient.put(`/transactions/${transaction_id}/feedback`, { is_safe: isSafe });
      
      Alert.alert(
        isSafe ? 'Marked Safe' : 'Reported as Fraud', 
        isSafe ? 'The transaction has been processed.' : 'We have blocked this transaction and notified our security team.',
        [{ text: 'OK', onPress: () => navigation.popToTop() }]
      );
    } catch (e: any) {
      Alert.alert('Error', e.response?.data?.detail || 'An error occurred.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.warningIconContainer}>
        <Ionicons name="warning" size={80} color="#EF4444" />
      </View>
      
      <Text style={styles.title}>Suspicious Transaction Detected</Text>
      <Text style={styles.subtitle}>Our AI model flagged this transaction as potentially fraudulent.</Text>
      
      <View style={styles.card}>
        <Text style={styles.cardLabel}>Merchant</Text>
        <Text style={styles.cardValue}>{merchant}</Text>
        
        <View style={styles.divider} />
        
        <Text style={styles.cardLabel}>Amount</Text>
        <Text style={styles.cardValue}>${amount}</Text>
      </View>
      
      <Text style={styles.prompt}>Did you make this transaction?</Text>
      
      {loading ? (
        <ActivityIndicator size="large" color="#EF4444" style={{ marginTop: 20 }} />
      ) : (
        <View style={styles.actionButtons}>
          <TouchableOpacity 
            style={[styles.button, styles.safeButton]} 
            onPress={() => handleFeedback(true)}
          >
            <Ionicons name="checkmark-circle-outline" size={24} color="#0F172A" />
            <Text style={styles.safeButtonText}>Yes, it's me</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.button, styles.fraudButton]} 
            onPress={() => handleFeedback(false)}
          >
            <Ionicons name="shield-half-outline" size={24} color="#F8FAFC" />
            <Text style={styles.fraudButtonText}>Report Fraud</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#7F1D1D', padding: 20, justifyContent: 'center', alignItems: 'center' },
  warningIconContainer: { backgroundColor: '#450A0A', padding: 20, borderRadius: 100, marginBottom: 20 },
  title: { fontSize: 24, fontWeight: 'bold', color: '#F8FAFC', textAlign: 'center', marginBottom: 10 },
  subtitle: { fontSize: 16, color: '#FECACA', textAlign: 'center', marginBottom: 40, paddingHorizontal: 20, lineHeight: 24 },
  card: { backgroundColor: '#991B1B', width: '100%', padding: 20, borderRadius: 16, marginBottom: 40 },
  cardLabel: { color: '#FECACA', fontSize: 14, marginBottom: 4 },
  cardValue: { color: '#F8FAFC', fontSize: 22, fontWeight: 'bold' },
  divider: { height: 1, backgroundColor: '#7F1D1D', marginVertical: 15 },
  prompt: { fontSize: 18, fontWeight: 'bold', color: '#F8FAFC', marginBottom: 20 },
  actionButtons: { width: '100%', gap: 15 },
  button: { width: '100%', padding: 16, borderRadius: 12, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: 10 },
  safeButton: { backgroundColor: '#10B981' },
  safeButtonText: { color: '#0F172A', fontWeight: 'bold', fontSize: 16 },
  fraudButton: { backgroundColor: '#1E293B', borderWidth: 1, borderColor: '#334155' },
  fraudButtonText: { color: '#F8FAFC', fontWeight: 'bold', fontSize: 16 },
});

export default FraudAlertScreen;
