import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, Alert, ScrollView } from 'react-native';
import apiClient from '../../api/axios';

const AddTransactionScreen = ({ navigation }: any) => {
  const [amount, setAmount] = useState('');
  const [merchant, setMerchant] = useState('');
  const [category, setCategory] = useState('Shopping');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);

  // Use Razorpay flow here conceptually - we are simulating it directly via our backend first
  const handleSubmit = async () => {
    if (!amount || !merchant) {
      Alert.alert('Error', 'Please enter amount and merchant');
      return;
    }

    setLoading(true);
    try {
      const res = await apiClient.post('/transactions/add', {
        amount: parseFloat(amount),
        merchant,
        category,
        notes,
        location: 'Current Location'
      });
      
      const { is_suspicious, id } = res.data;
      
      if (is_suspicious) {
        // Normally WebSocket triggers UI, but we can also manually show it if requested
        navigation.navigate('FraudAlert', { transaction_id: id, amount, merchant });
      } else {
        Alert.alert('Success', 'Transaction successful', [
          { text: 'OK', onPress: () => navigation.goBack() }
        ]);
      }
    } catch (e: any) {
      Alert.alert('Transaction Failed', e.response?.data?.detail || 'An error occurred.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.label}>Amount</Text>
      <View style={{ flexDirection: 'row', alignItems: 'center' }}>
        <Text style={{ fontSize: 24, color: '#00D09E', marginRight: 10 }}>₹</Text>
        <TextInput
          style={[styles.inputWrapper, { flex: 1 }]}
          placeholder="0.00"
          placeholderTextColor="#64748B"
          keyboardType="decimal-pad"
          value={amount}
          onChangeText={setAmount}
        />
      </View>
      
      <Text style={styles.label}>Merchant</Text>
      <TextInput
        style={styles.inputWrapper}
        placeholder="e.g. Amazon, Starbucks"
        placeholderTextColor="#64748B"
        value={merchant}
        onChangeText={setMerchant}
      />
      
      <Text style={styles.label}>Category</Text>
      <View style={styles.categoryRow}>
        {['Shopping', 'Food', 'Travel', 'Bills'].map(cat => (
          <TouchableOpacity 
            key={cat} 
            style={[styles.catBadge, category === cat && styles.catBadgeActive]}
            onPress={() => setCategory(cat)}
          >
            <Text style={[styles.catText, category === cat && styles.catTextActive]}>{cat}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <Text style={styles.label}>Notes (Optional)</Text>
      <TextInput
        style={[styles.inputWrapper, { height: 100, textAlignVertical: 'top' }]}
        placeholder="What was this for?"
        placeholderTextColor="#64748B"
        multiline
        value={notes}
        onChangeText={setNotes}
      />

      <TouchableOpacity style={styles.button} onPress={handleSubmit} disabled={loading}>
        {loading ? <ActivityIndicator color="#0F172A" /> : <Text style={styles.buttonText}>Confirm Transaction</Text>}
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F172A', padding: 20 },
  label: { color: '#94A3B8', fontSize: 14, marginBottom: 8, marginTop: 15 },
  inputWrapper: { backgroundColor: '#1E293B', color: '#F8FAFC', borderRadius: 8, padding: 15, borderWidth: 1, borderColor: '#334155', fontSize: 16 },
  categoryRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  catBadge: { backgroundColor: '#1E293B', paddingHorizontal: 16, paddingVertical: 10, borderRadius: 20, borderWidth: 1, borderColor: '#334155' },
  catBadgeActive: { backgroundColor: '#00D09E', borderColor: '#00D09E' },
  catText: { color: '#94A3B8', fontWeight: '600' },
  catTextActive: { color: '#0F172A' },
  button: { backgroundColor: '#00D09E', padding: 15, borderRadius: 8, alignItems: 'center', marginTop: 30, marginBottom: 40 },
  buttonText: { color: '#0F172A', fontWeight: 'bold', fontSize: 16 },
});

export default AddTransactionScreen;
