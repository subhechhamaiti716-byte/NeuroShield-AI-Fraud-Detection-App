import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, RefreshControl } from 'react-native';
import apiClient from '../../api/axios';
import { Ionicons } from '@expo/vector-icons';

const TransactionsScreen = () => {
  const [transactions, setTransactions] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    setRefreshing(true);
    try {
      const res = await apiClient.get('/transactions/?limit=50');
      setTransactions(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const renderTransaction = ({ item }: { item: any }) => {
    const date = new Date(item.timestamp).toLocaleDateString();
    
    return (
      <View style={styles.transactionCard}>
        <View style={styles.txLeft}>
          <View style={[styles.iconBox, { backgroundColor: item.is_suspicious ? '#7F1D1D' : '#047857' }]}>
            <Ionicons name={item.is_suspicious ? 'warning' : 'receipt-outline'} size={24} color={item.is_suspicious ? '#EF4444' : '#10B981'} />
          </View>
          <View>
            <Text style={styles.txMerchant}>{item.merchant}</Text>
            <Text style={styles.txMeta}>{item.category} • {date}</Text>
          </View>
        </View>
        <View style={styles.txRight}>
          <Text style={styles.txAmount}>${item.amount.toFixed(2)}</Text>
          {item.is_suspicious && (
            <Text style={styles.txRisk}>{item.user_confirmed_safe ? 'Marked Safe' : 'Suspicious'}</Text>
          )}
        </View>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>All Transactions</Text>
      <FlatList
        data={transactions}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderTransaction}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={loadData} tintColor="#00D09E" />}
        contentContainerStyle={{ paddingBottom: 20 }}
        ListEmptyComponent={<Text style={styles.emptyText}>No transactions found.</Text>}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F172A', padding: 20 },
  title: { fontSize: 24, fontWeight: 'bold', color: '#F8FAFC', marginBottom: 20, marginTop: 10 },
  transactionCard: { flexDirection: 'row', justifyContent: 'space-between', backgroundColor: '#1E293B', padding: 15, borderRadius: 12, marginBottom: 10 },
  txLeft: { flexDirection: 'row', alignItems: 'center' },
  iconBox: { width: 44, height: 44, borderRadius: 22, justifyContent: 'center', alignItems: 'center', marginRight: 15 },
  txMerchant: { color: '#F8FAFC', fontSize: 16, fontWeight: '600' },
  txMeta: { color: '#94A3B8', fontSize: 12, marginTop: 4 },
  txRight: { alignItems: 'flex-end', justifyContent: 'center' },
  txAmount: { color: '#F8FAFC', fontSize: 16, fontWeight: 'bold' },
  txRisk: { color: '#EF4444', fontSize: 12, marginTop: 4, fontWeight: 'bold' },
  emptyText: { color: '#94A3B8', textAlign: 'center', marginTop: 20 }
});

export default TransactionsScreen;
