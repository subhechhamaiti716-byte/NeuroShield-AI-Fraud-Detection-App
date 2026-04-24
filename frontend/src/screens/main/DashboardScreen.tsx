import React, { useContext, useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, FlatList, RefreshControl } from 'react-native';
import { AuthContext } from '../../context/AuthContext';
import apiClient from '../../api/axios';
import { Ionicons } from '@expo/vector-icons';

const DashboardScreen = ({ navigation }: any) => {
  const { user, fetchUser, logout } = useContext(AuthContext);
  const [transactions, setTransactions] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    setRefreshing(true);
    await fetchUser();
    try {
      const res = await apiClient.get('/transactions/?limit=5');
      setTransactions(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    const unsubscribe = navigation.addListener('focus', () => {
      loadData();
    });
    return unsubscribe;
  }, [navigation]);

  const renderTransaction = ({ item }: { item: any }) => (
    <View style={styles.transactionCard}>
      <View style={styles.txLeft}>
        <View style={[styles.iconBox, { backgroundColor: item.is_suspicious ? '#7F1D1D' : '#047857' }]}>
          <Ionicons name={item.is_suspicious ? 'warning' : 'cash-outline'} size={24} color={item.is_suspicious ? '#EF4444' : '#10B981'} />
        </View>
        <View>
          <Text style={styles.txMerchant}>{item.merchant}</Text>
          <Text style={styles.txCategory}>{item.category}</Text>
        </View>
      </View>
      <View style={styles.txRight}>
        <Text style={styles.txAmount}>${item.amount.toFixed(2)}</Text>
        {item.is_suspicious && <Text style={styles.txRisk}>High Risk</Text>}
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Hello, {user?.name.split(' ')[0]}</Text>
          <Text style={styles.subtitle}>Welcome back!</Text>
        </View>
        <TouchableOpacity onPress={logout} style={styles.logoutBtn}>
          <Ionicons name="log-out-outline" size={24} color="#EF4444" />
        </TouchableOpacity>
      </View>

      <View style={styles.balanceCard}>
        <Text style={styles.balanceLabel}>Total Balance</Text>
        <Text style={styles.balanceAmount}>${user?.balance?.toFixed(2) || '0.00'}</Text>
        <View style={styles.balanceRow}>
          <View style={styles.riskIndicator}>
            <Ionicons name="shield-checkmark" size={16} color="#00D09E" />
            <Text style={styles.riskText}>Protected by NeuroShield</Text>
          </View>
          <TouchableOpacity onPress={() => navigation.navigate('DepositFunds')} style={styles.depositBtn}>
            <Ionicons name="card" size={16} color="#1E293B" />
            <Text style={styles.depositBtnText}>Deposit</Text>
          </TouchableOpacity>
        </View>
        <TouchableOpacity 
          onPress={() => navigation.navigate('BankLink')} 
          style={styles.linkBankBtn}
        >
          <Ionicons name="link-outline" size={16} color="#94A3B8" />
          <Text style={styles.linkBankBtnText}>Link Real Bank Account</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.actionRow}>
        <Text style={styles.sectionTitle}>Recent Transactions</Text>
        <TouchableOpacity onPress={() => navigation.navigate('AddTransaction')} style={styles.addButton}>
          <Ionicons name="add" size={20} color="#0F172A" />
          <Text style={styles.addButtonText}>Add</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={transactions}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderTransaction}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={loadData} tintColor="#00D09E" />}
        contentContainerStyle={{ paddingBottom: 20 }}
        ListEmptyComponent={<Text style={styles.emptyText}>No recent transactions.</Text>}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F172A', padding: 20 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 25, marginTop: 10 },
  greeting: { fontSize: 24, fontWeight: 'bold', color: '#F8FAFC' },
  subtitle: { fontSize: 14, color: '#94A3B8' },
  logoutBtn: { padding: 8, backgroundColor: '#1E293B', borderRadius: 50 },
  balanceCard: { backgroundColor: '#1E293B', padding: 20, borderRadius: 16, marginBottom: 30, borderWidth: 1, borderColor: '#334155' },
  balanceLabel: { color: '#94A3B8', fontSize: 16, marginBottom: 8 },
  balanceAmount: { color: '#00D09E', fontSize: 40, fontWeight: 'bold', marginBottom: 15 },
  riskIndicator: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#064E3B', padding: 8, borderRadius: 8 },
  riskText: { color: '#00D09E', marginLeft: 6, fontSize: 12, fontWeight: '600' },
  balanceRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  depositBtn: { flexDirection: 'row', backgroundColor: '#00D09E', paddingHorizontal: 12, paddingVertical: 8, borderRadius: 8, alignItems: 'center' },
  depositBtnText: { color: '#1E293B', fontWeight: 'bold', marginLeft: 6 },
  linkBankBtn: { flexDirection: 'row', alignItems: 'center', marginTop: 15, paddingTop: 15, borderTopWidth: 1, borderTopColor: '#334155' },
  linkBankBtnText: { color: '#94A3B8', fontSize: 14, marginLeft: 8 },
  actionRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 15 },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', color: '#F8FAFC' },
  addButton: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#00D09E', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20 },
  addButtonText: { color: '#0F172A', fontWeight: 'bold', marginLeft: 4 },
  transactionCard: { flexDirection: 'row', justifyContent: 'space-between', backgroundColor: '#1E293B', padding: 15, borderRadius: 12, marginBottom: 10 },
  txLeft: { flexDirection: 'row', alignItems: 'center' },
  iconBox: { width: 44, height: 44, borderRadius: 22, justifyContent: 'center', alignItems: 'center', marginRight: 15 },
  txMerchant: { color: '#F8FAFC', fontSize: 16, fontWeight: '600' },
  txCategory: { color: '#94A3B8', fontSize: 12, marginTop: 2 },
  txRight: { alignItems: 'flex-end', justifyContent: 'center' },
  txAmount: { color: '#F8FAFC', fontSize: 16, fontWeight: 'bold' },
  txRisk: { color: '#EF4444', fontSize: 12, marginTop: 4, fontWeight: 'bold' },
  emptyText: { color: '#94A3B8', textAlign: 'center', marginTop: 20 }
});

export default DashboardScreen;
