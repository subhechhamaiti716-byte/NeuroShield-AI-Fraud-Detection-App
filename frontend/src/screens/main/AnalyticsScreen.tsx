import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import apiClient from '../../api/axios';

const AnalyticsScreen = () => {
  const [stats, setStats] = useState({ totalSpent: 0, suspiciousCount: 0, totalCount: 0 });
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    setRefreshing(true);
    try {
      const res = await apiClient.get('/transactions/?limit=100');
      const txs = res.data;
      
      let spent = 0;
      let susp = 0;
      txs.forEach((tx: any) => {
        spent += tx.amount;
        if (tx.is_suspicious) susp++;
      });
      
      setStats({
        totalSpent: spent,
        suspiciousCount: susp,
        totalCount: txs.length
      });
    } catch (e) {
      console.error(e);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={loadData} tintColor="#00D09E" />}
    >
      <Text style={styles.title}>Analytics Overview</Text>
      
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Total Spending</Text>
        <Text style={styles.cardValue}>${stats.totalSpent.toFixed(2)}</Text>
        <Text style={styles.cardSub}>Based on recent transactions</Text>
      </View>
      
      <View style={styles.row}>
        <View style={[styles.card, styles.halfCard]}>
          <Text style={styles.cardTitle}>Total Txns</Text>
          <Text style={styles.cardValue}>{stats.totalCount}</Text>
        </View>
        <View style={[styles.card, styles.halfCard, { borderColor: '#7F1D1D', borderWidth: 1 }]}>
          <Text style={[styles.cardTitle, { color: '#EF4444' }]}>Fraud Alerts</Text>
          <Text style={[styles.cardValue, { color: '#EF4444' }]}>{stats.suspiciousCount}</Text>
        </View>
      </View>
      
      <View style={styles.insightCard}>
        <Text style={styles.insightTitle}>AI Insights</Text>
        {stats.suspiciousCount > 0 ? (
          <Text style={styles.insightText}>We detected {stats.suspiciousCount} anomalous patterns in your recent spending. Maintain caution and verify any high-risk flagged transactions.</Text>
        ) : (
          <Text style={styles.insightText}>Your spending behavior is normal. No anomalous activities detected recently. Great job maintaining secure habits!</Text>
        )}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F172A', padding: 20 },
  title: { fontSize: 24, fontWeight: 'bold', color: '#F8FAFC', marginBottom: 20, marginTop: 10 },
  card: { backgroundColor: '#1E293B', padding: 20, borderRadius: 16, marginBottom: 15 },
  cardTitle: { color: '#94A3B8', fontSize: 14, marginBottom: 8 },
  cardValue: { color: '#F8FAFC', fontSize: 32, fontWeight: 'bold' },
  cardSub: { color: '#64748B', fontSize: 12, marginTop: 4 },
  row: { flexDirection: 'row', justifyContent: 'space-between' },
  halfCard: { width: '48%' },
  insightCard: { backgroundColor: '#022C22', padding: 20, borderRadius: 16, marginTop: 15, borderWidth: 1, borderColor: '#065F46' },
  insightTitle: { color: '#34D399', fontSize: 16, fontWeight: 'bold', marginBottom: 8 },
  insightText: { color: '#A7F3D0', lineHeight: 22 }
});

export default AnalyticsScreen;
