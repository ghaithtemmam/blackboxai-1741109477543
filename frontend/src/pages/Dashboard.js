import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  IconButton,
  CircularProgress,
  useTheme,
} from '@mui/material';
import {
  Message as MessageIcon,
  People as PeopleIcon,
  Campaign as CampaignIcon,
  Description as TemplateIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';
import axios from 'axios';

const StatCard = ({ title, value, icon, color, loading }) => {
  const theme = useTheme();
  
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" color="textSecondary">
            {title}
          </Typography>
          <Box sx={{ 
            backgroundColor: `${color}20`,
            borderRadius: '50%',
            padding: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            {React.cloneElement(icon, { sx: { color: color } })}
          </Box>
        </Box>
        {loading ? (
          <CircularProgress size={20} />
        ) : (
          <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
            {value}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

const Dashboard = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalMessages: 0,
    activeAccounts: 0,
    activeCampaigns: 0,
    templates: 0,
  });
  const [messageHistory, setMessageHistory] = useState([]);
  const [campaignPerformance, setCampaignPerformance] = useState([]);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      // In a real application, these would be actual API calls
      // Simulated data for demonstration
      setStats({
        totalMessages: 1234,
        activeAccounts: 5,
        activeCampaigns: 3,
        templates: 8,
      });

      setMessageHistory([
        { date: '2024-01', messages: 450 },
        { date: '2024-02', messages: 680 },
        { date: '2024-03', messages: 890 },
        { date: '2024-04', messages: 1234 },
      ]);

      setCampaignPerformance([
        { name: 'Campaign A', sent: 300, delivered: 290, responded: 145 },
        { name: 'Campaign B', sent: 500, delivered: 480, responded: 200 },
        { name: 'Campaign C', sent: 200, delivered: 190, responded: 80 },
      ]);

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Dashboard
        </Typography>
        <IconButton onClick={fetchDashboardData} disabled={loading}>
          <RefreshIcon />
        </IconButton>
      </Box>

      <Grid container spacing={3}>
        {/* Stats Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Messages"
            value={stats.totalMessages}
            icon={<MessageIcon />}
            color={theme.palette.primary.main}
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Accounts"
            value={stats.activeAccounts}
            icon={<PeopleIcon />}
            color={theme.palette.success.main}
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Campaigns"
            value={stats.activeCampaigns}
            icon={<CampaignIcon />}
            color={theme.palette.warning.main}
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Templates"
            value={stats.templates}
            icon={<TemplateIcon />}
            color={theme.palette.info.main}
            loading={loading}
          />
        </Grid>

        {/* Message History Chart */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Message History
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={messageHistory}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="messages"
                      stroke={theme.palette.primary.main}
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Campaign Performance Chart */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Campaign Performance
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={campaignPerformance}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="sent" fill={theme.palette.primary.main} />
                    <Bar dataKey="delivered" fill={theme.palette.success.main} />
                    <Bar dataKey="responded" fill={theme.palette.warning.main} />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
